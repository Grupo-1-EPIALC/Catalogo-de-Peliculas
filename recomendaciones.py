"""
recomendaciones.py

Funciones para armar un perfil de gustos de un usuario (generos, directores y
actores preferidos) y generar recomendaciones de peliculas del catalogo en
base a ese perfil, de dos formas distintas:
    1. Por ranking: coincidencias ordenadas por puntuacion descendente.
    2. Al azar: coincidencias elegidas aleatoriamente.

Funciones que contiene:
- crear_perfil_usuario
- filtrar_peliculas_por_gustos
- calcular_afinidad
- recomendar_por_ranking
- recomendar_al_azar
"""


# Parametros:
#   nombre (str): nombre o identificador del usuario.
#   generos_preferidos (list[str]): generos favoritos del usuario.
#   directores_preferidos (list[str]): directores favoritos del usuario.
#   actores_preferidos (list[str]): actores/actrices favoritos del usuario.
# Retorna:
#   dict: perfil de usuario, por ejemplo:
#       {"nombre": ..., "generos": [...], "directores": [...], "actores": [...]}
def crear_perfil_usuario(
    nombre: str,
    generos_preferidos: list[str],
    directores_preferidos: list[str],
    actores_preferidos: list[str],
) -> dict:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
# Retorna:
#   list[dict]: peliculas que coinciden con al menos un gusto del usuario
#       (genero, director o actor preferido).
def filtrar_peliculas_por_gustos(catalogo: list[dict], perfil_usuario: dict) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
# Retorna:
#   int: cantidad de coincidencias entre la pelicula y los gustos del usuario
#       (suma de generos, directores y actores en comun).
def calcular_afinidad(pelicula: dict, perfil_usuario: dict) -> int:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
#   campo_puntuacion (str): campo numerico a usar para ordenar
#       (ej. "vote_average", "popularity").
#   cantidad (int): cantidad de peliculas a recomendar.
# Retorna:
#   list[dict]: hasta `cantidad` peliculas afines al perfil, ordenadas de
#       mayor a menor segun campo_puntuacion.
def recomendar_por_ranking(catalogo: list[dict], perfil_usuario: dict, campo_puntuacion: str, cantidad: int) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   perfil_usuario (dict): perfil generado con crear_perfil_usuario.
#   cantidad (int): cantidad de peliculas a recomendar.
# Retorna:
#   list[dict]: hasta `cantidad` peliculas afines al perfil, elegidas al azar
#       (sin repetir) entre las coincidencias.
def recomendar_al_azar(catalogo: list[dict], perfil_usuario: dict, cantidad: int) -> list[dict]:
    pass  # TODO: implementar
