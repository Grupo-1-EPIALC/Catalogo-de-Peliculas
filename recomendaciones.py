"""
recomendaciones.py

Funciones para armar un perfil de gustos de un usuario (generos, directores,
actores e idiomas preferidos) y generar recomendaciones de peliculas del
catalogo en base a ese perfil, de dos formas distintas:
    1. Por ranking: coincidencias ordenadas por un puntaje compuesto que
       combina el puntaje propio de la pelicula, el promedio historico de
       sus categorias preferidas, y la afinidad.
    2. Al azar: coincidencias elegidas aleatoriamente.

Depende de `busqueda.py` (para filtrar por gustos, reutilizando
buscar_por_genero/_director/_actor/_idioma) y, para el promedio historico
por categoria, de dos fuentes segun la categoria:
    - actores y directores: primero `rankings.py` (ranking_actores /
      ranking_directores), que exige un minimo de peliculas por persona y
      da un promedio mas representativo; si una persona no llega a ese
      minimo, se usa como respaldo el promedio "crudo" de `estadisticas.py`
      (promedio_por_actor / promedio_por_director).
    - generos e idiomas: directamente `estadisticas.py`. Los generos son un
      puñado de categorias fijas (no hay problema de dispersion que
      justifique el filtro de rankings.py), y `rankings.py` no tiene una
      funcion de ranking de idiomas.

Los perfiles de usuario se persisten en un JSON aparte del catalogo de
peliculas (ver `env.RUTA_PERFILES`), con un "id" numerico ademas del
nombre: dos usuarios pueden llamarse igual, asi que el nombre solo no
alcanza para identificar un perfil sin ambiguedad.

Funciones que contiene:
- crear_perfil_usuario
- cargar_perfiles
- guardar_perfiles
- obtener_perfil_por_id
- agregar_perfil
- actualizar_perfil
- eliminar_perfil
- filtrar_peliculas_por_gustos
- calcular_afinidad
- recomendar_por_ranking
- recomendar_al_azar

Funciones auxiliares (uso interno del modulo):
- _valor_numerico
- _normalizar
- _preferencia_coincide_con_valor
- _promedio_por_categoria_combinado
- _generar_id_usuario
"""

import json
import random
import unicodedata
from typing import Callable

import busqueda
import estadisticas
import rankings
from env import RUTA_PERFILES

# Cuanto suma cada preferencia coincidente (genero/director/actor/idioma) al
# puntaje compuesto de recomendar_por_ranking. El puntaje propio de la
# pelicula y el promedio historico de sus categorias ya estan en la misma
# escala que campo_puntuacion (ej. 0 a 10 para vote_average); la afinidad es
# un conteo (0..N) y necesita este peso para no quedar fuera de escala.
PESO_AFINIDAD = 0.5

# Cantidad minima de peliculas que debe tener un actor/director en el
# catalogo para que rankings.py lo incluya en su ranking (fuente primaria
# del promedio historico de esas dos categorias). Por debajo de este minimo,
# se cae al promedio "crudo" sin piso de estadisticas.py (fuente secundaria).
MINIMO_PELICULAS_RANKING = 2

# Mapea cada preferencia del perfil de usuario con:
#   - el campo correspondiente en el dict de una pelicula,
#   - la funcion de busqueda.py que filtra el catalogo por esa preferencia,
#   - la funcion de estadisticas.py que da el promedio historico "crudo" por
#     esa categoria (fuente secundaria/unica, ver _promedio_por_categoria_combinado).
# Se usa en filtrar_peliculas_por_gustos, calcular_afinidad y
# recomendar_por_ranking para no repetir la misma logica 4 veces (una por
# genero/director/actor/idioma).
CAMPOS_PREFERENCIA: dict[str, tuple[str, Callable, Callable]] = {
    "generos": ("genres", busqueda.buscar_por_genero, estadisticas.promedio_por_genero),
    "directores": ("directors", busqueda.buscar_por_director, estadisticas.promedio_por_director),
    "actores": ("cast", busqueda.buscar_por_actor, estadisticas.promedio_por_actor),
    "idiomas": ("spoken_languages", busqueda.buscar_por_idioma, estadisticas.promedio_por_idioma),
}

# Para actores y directores, la funcion de rankings.py que da el promedio
# "primario" (mas representativo, con piso minimo de peliculas). Generos e
# idiomas no estan aca: quedan solo con la fuente de CAMPOS_PREFERENCIA
# (ver el docstring del modulo, arriba, para el motivo).
FUNCIONES_RANKING_POR_CATEGORIA: dict[str, Callable] = {
    "directores": rankings.ranking_directores,
    "actores": rankings.ranking_actores,
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
#   texto (str): texto a normalizar.
# Retorna:
#   str: el texto en minusculas, sin tildes/diacriticos y sin espacios en
#       las puntas. Misma normalizacion que usa busqueda.py (duplicada aca a
#       proposito, en vez de importar el helper privado de otro modulo).
def _normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().casefold())
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


# Parametros:
#   preferencia (str): un genero/director/actor/idioma preferido por el usuario.
#   valor_pelicula (str): el valor correspondiente de una pelicula.
# Retorna:
#   bool: True si la preferencia aparece (normalizada, sin importar mayusculas
#       ni tildes) dentro del valor de la pelicula. Usa la misma logica de
#       coincidencia que busqueda.py, para que una pelicula encontrada por
#       filtrar_peliculas_por_gustos nunca de afinidad 0 con la preferencia
#       que la hizo coincidir (ej. el usuario escribe "tom hanks" y la
#       pelicula tiene "Tom Hanks"). Si no hay coincidencia directa, prueba
#       ademas si `preferencia` es un genero en castellano
#       (`busqueda.traducir_categoria_a_ingles`) y compara con esa
#       traduccion; para director/actor/idioma esto no encuentra nada (el
#       diccionario es solo de generos) y no cambia el resultado.
def _preferencia_coincide_con_valor(preferencia: str, valor_pelicula: str) -> bool:
    preferencia_norm = _normalizar(preferencia)
    if not preferencia_norm:
        return False
    if preferencia_norm in _normalizar(valor_pelicula):
        return True

    preferencia_traducida = busqueda.traducir_categoria_a_ingles(preferencia)
    if preferencia_traducida is None:
        return False
    return _normalizar(preferencia_traducida) in _normalizar(valor_pelicula)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   clave_perfil (str): "generos", "directores", "actores" o "idiomas".
#   campo_puntuacion (str): campo numerico a promediar (ej. "vote_average").
# Retorna:
#   dict[str, float]: promedio historico por categoria. Para "directores" y
#       "actores", combina dos fuentes: rankings.py como primaria (mas
#       representativa, exige MINIMO_PELICULAS_RANKING peliculas por
#       persona) y estadisticas.py como secundaria/respaldo, usada solo
#       para las personas que rankings.py dejo afuera por no llegar al
#       minimo. Para "generos" e "idiomas" se devuelve directamente el
#       promedio "crudo" de estadisticas.py (unica fuente disponible/util).
def _promedio_por_categoria_combinado(catalogo: list[dict], clave_perfil: str, campo_puntuacion: str) -> dict[str, float]:
    _, _, funcion_promedio_estadisticas = CAMPOS_PREFERENCIA[clave_perfil]
    promedio_secundario = funcion_promedio_estadisticas(catalogo, campo_puntuacion)

    funcion_ranking = FUNCIONES_RANKING_POR_CATEGORIA.get(clave_perfil)
    if funcion_ranking is None:
        return promedio_secundario

    promedio_primario = dict(funcion_ranking(catalogo, campo_puntuacion, MINIMO_PELICULAS_RANKING))
    return {**promedio_secundario, **promedio_primario}


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
#   ruta_json (str): ruta al archivo JSON con los perfiles de usuario persistidos.
# Retorna:
#   list[dict]: lista de perfiles cargados desde el archivo. Lista vacia si el
#       archivo todavia no existe (caso normal la primera vez que se corre la
#       app, antes de crear ningun perfil).
# Manejo de errores esperado:
#   json.JSONDecodeError si el archivo esta mal formado: se informa y se
#   devuelve una lista vacia en vez de dejar caer el programa.
def cargar_perfiles(ruta_json: str = RUTA_PERFILES) -> list[dict]:
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if not isinstance(datos, list):
                print(f"Error: El archivo '{ruta_json}' no contiene una lista de perfiles válida.")
                return []
            return datos
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error: El archivo '{ruta_json}' está mal formado o corrupto ({e}).")
        return []


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario a persistir.
#   ruta_json (str): ruta destino del archivo JSON.
# Retorna:
#   None
# Manejo de errores esperado:
#   OSError si no se puede escribir el archivo (permisos, disco, ruta invalida).
def guardar_perfiles(perfiles: list[dict], ruta_json: str = RUTA_PERFILES) -> None:
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(perfiles, archivo, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Error de E/S al intentar guardar en '{ruta_json}': {e}")


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario ya persistidos.
# Retorna:
#   int: el proximo id disponible (el mayor id existente + 1, o 1 si `perfiles`
#       esta vacia). El nombre por si solo no alcanza para identificar a un
#       usuario sin ambiguedad (dos personas pueden llamarse igual); el id es
#       lo que usan obtener_perfil_por_id/actualizar_perfil/eliminar_perfil.
def _generar_id_usuario(perfiles: list[dict]) -> int:
    if not perfiles:
        return 1
    return max(perfil["id"] for perfil in perfiles) + 1


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario.
#   id_usuario (int): id del perfil a buscar.
# Retorna:
#   dict | None: el perfil encontrado, o None si no existe ese id.
def obtener_perfil_por_id(perfiles: list[dict], id_usuario: int) -> dict | None:
    for perfil in perfiles:
        if perfil.get("id") == id_usuario:
            return perfil
    return None


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario ya persistidos (se
#       modifica in-place: se le agrega el perfil nuevo).
#   nombre/generos_preferidos/directores_preferidos/actores_preferidos/
#   idiomas_preferidos: ver crear_perfil_usuario.
# Retorna:
#   list[dict]: `perfiles` con el nuevo perfil agregado al final (con un "id"
#       nuevo ya asignado, ver _generar_id_usuario). A diferencia de
#       crud.crear_pelicula (donde el id de la pelicula ya viene provisto por
#       el llamador), aca el id lo genera esta funcion: el usuario de la app
#       no elige su propio id.
def agregar_perfil(
    perfiles: list[dict],
    nombre: str,
    generos_preferidos: list[str],
    directores_preferidos: list[str],
    actores_preferidos: list[str],
    idiomas_preferidos: list[str],
) -> list[dict]:
    nuevo_perfil = crear_perfil_usuario(
        nombre, generos_preferidos, directores_preferidos, actores_preferidos, idiomas_preferidos
    )
    nuevo_perfil["id"] = _generar_id_usuario(perfiles)
    perfiles.append(nuevo_perfil)
    return perfiles


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario.
#   id_usuario (int): id del perfil a modificar.
#   campos_actualizados (dict): pares clave/valor a sobrescribir en el perfil
#       (ej. {"nombre": "Nuevo nombre"} o {"generos": ["Drama", "Accion"]}).
# Retorna:
#   list[dict]: `perfiles` con el perfil modificado.
# Manejo de errores esperado:
#   ValueError si no existe un perfil con ese id.
def actualizar_perfil(perfiles: list[dict], id_usuario: int, campos_actualizados: dict) -> list[dict]:
    perfil = obtener_perfil_por_id(perfiles, id_usuario)
    if perfil is None:
        raise ValueError(f"No existe ningun perfil con el id {id_usuario}.")

    for clave, valor in campos_actualizados.items():
        perfil[clave] = valor

    return perfiles


# Parametros:
#   perfiles (list[dict]): lista de perfiles de usuario.
#   id_usuario (int): id del perfil a eliminar.
# Retorna:
#   list[dict]: `perfiles` sin el perfil eliminado.
# Manejo de errores esperado:
#   ValueError si no existe un perfil con ese id.
def eliminar_perfil(perfiles: list[dict], id_usuario: int) -> list[dict]:
    perfil = obtener_perfil_por_id(perfiles, id_usuario)
    if perfil is None:
        raise ValueError(f"No existe ningun perfil con el id {id_usuario}.")

    perfiles.remove(perfil)
    return perfiles


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
#       (suma de generos, directores, actores e idiomas en comun). La
#       comparacion es normalizada (sin importar mayusculas ni tildes), igual
#       que busqueda.py, para ser consistente con filtrar_peliculas_por_gustos.
def calcular_afinidad(pelicula: dict, perfil_usuario: dict) -> int:
    afinidad = 0
    for clave_perfil, (campo_pelicula, _, _) in CAMPOS_PREFERENCIA.items():
        valores_pelicula = pelicula.get(campo_pelicula) or []
        preferencias = perfil_usuario.get(clave_perfil) or []
        afinidad += sum(
            1
            for preferencia in preferencias
            if any(_preferencia_coincide_con_valor(preferencia, valor) for valor in valores_pelicula)
        )
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
#         cada coincidencia de genero/director/actor/idioma. El promedio
#         historico de actor/director sale de rankings.py cuando esa
#         persona tiene suficientes peliculas, o de estadisticas.py si no
#         (ver _promedio_por_categoria_combinado).
#       Si una pelicula no tiene categorias coincidentes con promedio
#       historico disponible, se usa solo su puntaje propio.
def recomendar_por_ranking(catalogo: list[dict], perfil_usuario: dict, campo_puntuacion: str, cantidad: int) -> list[dict]:
    candidatas = filtrar_peliculas_por_gustos(catalogo, perfil_usuario)
    if not candidatas:
        return []

    # se calcula una sola vez por categoria (no por pelicula): recorrer todo
    # el catalogo dentro del ordenamiento seria muy costoso con miles de peliculas
    promedios_por_categoria = {
        clave_perfil: _promedio_por_categoria_combinado(catalogo, clave_perfil, campo_puntuacion)
        for clave_perfil in CAMPOS_PREFERENCIA
    }

    def _puntaje_compuesto(pelicula: dict) -> float:
        puntaje_propio = _valor_numerico(pelicula, campo_puntuacion) or 0.0

        valores_historicos = []
        for clave_perfil, (campo_pelicula, _, _) in CAMPOS_PREFERENCIA.items():
            preferencias = perfil_usuario.get(clave_perfil) or []
            promedios = promedios_por_categoria[clave_perfil]
            for valor in pelicula.get(campo_pelicula) or []:
                if valor in promedios and any(
                    _preferencia_coincide_con_valor(preferencia, valor) for preferencia in preferencias
                ):
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
