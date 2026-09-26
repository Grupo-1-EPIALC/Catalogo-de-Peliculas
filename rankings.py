"""
rankings.py

Funciones para obtener las peliculas (o categorias) mejor puntuadas, segun
distintos campos de puntuacion disponibles en el catalogo:
    "vote_average"  -> puntaje promedio de los usuarios (0 a 10)
    "vote_count"    -> cantidad de votos recibidos
    "popularity"    -> indice de popularidad de TMDB

Funciones que contiene:
- top_peliculas
- top_por_genero
- top_por_actor
- top_por_director
- ranking_generos
- ranking_actores
- ranking_directores

``top_por_genero`` acepta el genero en castellano o ingles: si no encuentra
nada con el valor tal cual, prueba traducirlo con
``busqueda.traducir_categoria_a_ingles`` (mismo criterio que
``busqueda.buscar_por_genero``, ver el docstring de ese modulo).
"""

import math
import unicodedata

import busqueda


def _valor_numerico(pelicula: dict, campo: str) -> float | None:
    valor = pelicula.get(campo)
    if valor is None:
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        return None
    return numero if math.isfinite(numero) else None


def _normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().casefold())
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


def _valores_categoria(pelicula: dict, campo_lista: str) -> list[str]:
    valores = pelicula.get(campo_lista)
    if not isinstance(valores, list):
        return []
    return [valor for valor in valores if isinstance(valor, str) and _normalizar(valor)]


def _ordenar_peliculas(catalogo: list[dict], campo_puntuacion: str, cantidad: int) -> list[dict]:
    if cantidad <= 0:
        return []

    puntuadas = []
    for pelicula in catalogo:
        if not isinstance(pelicula, dict):
            continue
        puntuacion = _valor_numerico(pelicula, campo_puntuacion)
        if puntuacion is not None:
            puntuadas.append((puntuacion, pelicula))

    puntuadas.sort(key=lambda elemento: elemento[0], reverse=True)
    return [pelicula for _, pelicula in puntuadas[:cantidad]]


def _top_por_categoria(
    catalogo: list[dict],
    campo_lista: str,
    categoria: str,
    campo_puntuacion: str,
    cantidad: int,
) -> list[dict]:
    categoria_normalizada = _normalizar(categoria)
    if not categoria_normalizada or cantidad <= 0:
        return []

    coincidencias = [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula, dict)
        and any(
            _normalizar(valor) == categoria_normalizada
            for valor in _valores_categoria(pelicula, campo_lista)
        )
    ]
    return _ordenar_peliculas(coincidencias, campo_puntuacion, cantidad)


def _ranking_por_categoria(
    catalogo: list[dict],
    campo_lista: str,
    campo_puntuacion: str,
    minimo_peliculas: int = 1,
) -> list[tuple[str, float]]:
    grupos: dict[str, list] = {}

    for pelicula in catalogo:
        if not isinstance(pelicula, dict):
            continue
        puntuacion = _valor_numerico(pelicula, campo_puntuacion)
        if puntuacion is None:
            continue

        categorias_vistas = set()
        for categoria in _valores_categoria(pelicula, campo_lista):
            categoria_normalizada = _normalizar(categoria)
            if categoria_normalizada in categorias_vistas:
                continue
            categorias_vistas.add(categoria_normalizada)

            if categoria_normalizada not in grupos:
                grupos[categoria_normalizada] = [categoria, 0.0, 0]
            grupos[categoria_normalizada][1] += puntuacion
            grupos[categoria_normalizada][2] += 1

    ranking = [
        (categoria[0], categoria[1] / categoria[2])
        for categoria in grupos.values()
        if categoria[2] >= minimo_peliculas
    ]
    ranking.sort(key=lambda elemento: elemento[1], reverse=True)
    return [(categoria, round(promedio, 2)) for categoria, promedio in ranking]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a usar para ordenar
#       (ej. "vote_average", "popularity", "vote_count").
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas con mayor valor en campo_puntuacion,
#       ordenadas de mayor a menor.
def top_peliculas(catalogo: list[dict], campo_puntuacion: str, cantidad: int) -> list[dict]:
    return _ordenar_peliculas(catalogo, campo_puntuacion, cantidad)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   genero (str): genero a filtrar, en ingles o castellano (ej. "Animation"
#       o "animacion").
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese genero (o su traduccion al
#       ingles, si el valor tal cual no encuentra nada) con mayor puntuacion.
def top_por_genero(catalogo: list[dict], genero: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    resultado = _top_por_categoria(catalogo, "genres", genero, campo_puntuacion, cantidad)

    if not resultado:
        genero_en_ingles = busqueda.traducir_categoria_a_ingles(genero)
        if genero_en_ingles is not None:
            resultado = _top_por_categoria(catalogo, "genres", genero_en_ingles, campo_puntuacion, cantidad)

    return resultado


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   actor (str): nombre del actor/actriz a filtrar.
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese actor con mayor puntuacion.
def top_por_actor(catalogo: list[dict], actor: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    return _top_por_categoria(catalogo, "cast", actor, campo_puntuacion, cantidad)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   director (str): nombre del director a filtrar.
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese director con mayor puntuacion.
def top_por_director(catalogo: list[dict], director: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    return _top_por_categoria(catalogo, "directors", director, campo_puntuacion, cantidad)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por genero.
# Retorna:
#   list[tuple[str, float]]: lista de (genero, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_generos(catalogo: list[dict], campo_puntuacion: str) -> list[tuple[str, float]]:
    return _ranking_por_categoria(catalogo, "genres", campo_puntuacion)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por actor.
#   minimo_peliculas (int): cantidad minima de peliculas que debe tener un
#       actor para entrar en el ranking (evita promedios poco representativos).
# Retorna:
#   list[tuple[str, float]]: lista de (actor, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_actores(catalogo: list[dict], campo_puntuacion: str, minimo_peliculas: int) -> list[tuple[str, float]]:
    return _ranking_por_categoria(catalogo, "cast", campo_puntuacion, minimo_peliculas)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por director.
#   minimo_peliculas (int): cantidad minima de peliculas que debe tener un
#       director para entrar en el ranking.
# Retorna:
#   list[tuple[str, float]]: lista de (director, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_directores(catalogo: list[dict], campo_puntuacion: str, minimo_peliculas: int) -> list[tuple[str, float]]:
    return _ranking_por_categoria(catalogo, "directors", campo_puntuacion, minimo_peliculas)
