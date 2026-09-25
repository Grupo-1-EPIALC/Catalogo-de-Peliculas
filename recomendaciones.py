"""
recomendaciones.py

Funciones para armar un perfil de gustos de un usuario (generos, directores,
actores e idiomas preferidos) y generar recomendaciones de peliculas del
catalogo en base a ese perfil, de dos formas distintas:
    1. Por ranking: coincidencias ordenadas por un puntaje compuesto que
       combina el puntaje propio de la pelicula, el promedio historico
       (estadisticas.py) de sus categorias preferidas, y la afinidad.
    2. Al azar: coincidencias elegidas aleatoriamente.

Depende de `busqueda.py` (para filtrar por gustos, reutilizando
buscar_por_genero/_director/_actor/_idioma) y de `estadisticas.py` (para el
promedio historico por categoria).

Funciones que contiene:
- crear_perfil_usuario
- filtrar_peliculas_por_gustos
- calcular_afinidad
- recomendar_por_ranking
- recomendar_al_azar

Funciones auxiliares (uso interno del modulo):
- _valor_numerico
"""

import random
from typing import Callable

import busqueda
import estadisticas

# Cuanto suma cada preferencia coincidente (genero/director/actor/idioma) al
# puntaje compuesto de recomendar_por_ranking. El puntaje propio de la
# pelicula y el promedio historico de sus categorias ya estan en la misma
# escala que campo_puntuacion (ej. 0 a 10 para vote_average); la afinidad es
# un conteo (0..N) y necesita este peso para no quedar fuera de escala.
PESO_AFINIDAD = 0.5

# Mapea cada preferencia del perfil de usuario con:
#   - el campo correspondiente en el dict de una pelicula,
#   - la funcion de busqueda.py que filtra el catalogo por esa preferencia,
#   - la funcion de estadisticas.py que da el promedio historico por esa categoria.
# Se usa en filtrar_peliculas_por_gustos, calcular_afinidad y
# recomendar_por_ranking para no repetir la misma logica 4 veces (una por
# genero/director/actor/idioma).
CAMPOS_PREFERENCIA: dict[str, tuple[str, Callable, Callable]] = {
    "generos": ("genres", busqueda.buscar_por_genero, estadisticas.promedio_por_genero),
    "directores": ("directors", busqueda.buscar_por_director, estadisticas.promedio_por_director),
    "actores": ("cast", busqueda.buscar_por_actor, estadisticas.promedio_por_actor),
    "idiomas": ("spoken_languages", busqueda.buscar_por_idioma, estadisticas.promedio_por_idioma),
}


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
#   campo (str): nombre del campo numerico a leer (ej. "vote_average", "popularity").
# Retorna:
#   float | None: el valor del campo convertido a float, o None si el campo
#       no existe, es None, o no se puede convertir.
def _valor_numerico(pelicula: dict, campo: str) -> float | None:
    valor = pelicula.get(campo)
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


# Parametros:
#   nombre (str): nombre o identificador del usuario.
#   generos_preferidos (list[str]): generos favoritos del usuario.
#   directores_preferidos (list[str]): directores favoritos del usuario.
#   actores_preferidos (list[str]): actores/actrices favoritos del usuario.
#   idiomas_preferidos (list[str]): idiomas hablados preferidos del usuario.
# Retorna:
#   dict: perfil de usuario:
#       {"nombre": ..., "generos": [...], "directores": [...],
#        "actores": [...], "idiomas": [...]}
def crear_perfil_usuario(
    nombre: str,
    generos_preferidos: list[str],
    directores_preferidos: list[str],
    actores_preferidos: list[str],
    idiomas_preferidos: list[str],
) -> dict:
    return {
        "nombre": nombre,
        "generos": generos_preferidos,
        "directores": directores_preferidos,
        "actores": actores_preferidos,
        "idiomas": idiomas_preferidos,
    }


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
# Retorna:
#   list[dict]: peliculas que coinciden con al menos un gusto del usuario
#       (genero, director, actor o idioma preferido), sin duplicados. Delega
#       el matching en busqueda.py (union de resultados por cada preferencia)
#       en vez de reimplementar la comparacion de texto.
def filtrar_peliculas_por_gustos(catalogo: list[dict], perfil_usuario: dict) -> list[dict]:
    coincidencias: dict[int, dict] = {}

    for clave_perfil, (_, funcion_busqueda, _) in CAMPOS_PREFERENCIA.items():
        for valor_preferido in perfil_usuario.get(clave_perfil) or []:
            for pelicula in funcion_busqueda(catalogo, valor_preferido):
                coincidencias[pelicula["id"]] = pelicula

    return list(coincidencias.values())


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
# Retorna:
#   int: cantidad de coincidencias entre la pelicula y los gustos del usuario
#       (suma de generos, directores, actores e idiomas en comun).
def calcular_afinidad(pelicula: dict, perfil_usuario: dict) -> int:
    afinidad = 0
    for clave_perfil, (campo_pelicula, _, _) in CAMPOS_PREFERENCIA.items():
        preferencias = set(perfil_usuario.get(clave_perfil) or [])
        valores_pelicula = set(pelicula.get(campo_pelicula) or [])
        afinidad += len(preferencias & valores_pelicula)
    return afinidad


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
#   campo_puntuacion (str): campo numerico a usar para ordenar
#       (ej. "vote_average", "popularity").
#   cantidad (int): cantidad de peliculas a recomendar.
# Retorna:
#   list[dict]: hasta `cantidad` peliculas afines al perfil, ordenadas de
#       mayor a menor segun un puntaje compuesto:
#         (puntaje propio de la pelicula + promedio historico de sus
#          categorias preferidas coincidentes) / 2, mas PESO_AFINIDAD por
#         cada coincidencia de genero/director/actor/idioma.
#       Si una pelicula no tiene categorias coincidentes con promedio
#       historico disponible, se usa solo su puntaje propio.
def recomendar_por_ranking(catalogo: list[dict], perfil_usuario: dict, campo_puntuacion: str, cantidad: int) -> list[dict]:
    candidatas = filtrar_peliculas_por_gustos(catalogo, perfil_usuario)
    if not candidatas:
        return []

    # se calcula una sola vez por categoria (no por pelicula): recorrer todo
    # el catalogo dentro del ordenamiento seria muy costoso con miles de peliculas
    promedios_por_categoria = {
        clave_perfil: funcion_promedio(catalogo, campo_puntuacion)
        for clave_perfil, (_, _, funcion_promedio) in CAMPOS_PREFERENCIA.items()
    }

    def _puntaje_compuesto(pelicula: dict) -> float:
        puntaje_propio = _valor_numerico(pelicula, campo_puntuacion) or 0.0

        valores_historicos = []
        for clave_perfil, (campo_pelicula, _, _) in CAMPOS_PREFERENCIA.items():
            preferencias = set(perfil_usuario.get(clave_perfil) or [])
            promedios = promedios_por_categoria[clave_perfil]
            for valor in pelicula.get(campo_pelicula) or []:
                if valor in preferencias and valor in promedios:
                    valores_historicos.append(promedios[valor])

        if valores_historicos:
            promedio_historico = sum(valores_historicos) / len(valores_historicos)
            base = (puntaje_propio + promedio_historico) / 2
        else:
            base = puntaje_propio

        return base + PESO_AFINIDAD * calcular_afinidad(pelicula, perfil_usuario)

    return sorted(candidatas, key=_puntaje_compuesto, reverse=True)[:cantidad]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
#   cantidad (int): cantidad de peliculas a recomendar.
# Retorna:
#   list[dict]: hasta `cantidad` peliculas afines al perfil, elegidas al azar
#       (sin repetir) entre las coincidencias.
def recomendar_al_azar(catalogo: list[dict], perfil_usuario: dict, cantidad: int) -> list[dict]:
    candidatas = filtrar_peliculas_por_gustos(catalogo, perfil_usuario)
    return random.sample(candidatas, k=min(cantidad, len(candidatas)))
