"""
estadisticas.py

Funciones que calculan indicadores y promedios sobre el catalogo de peliculas,
agrupando por distintas categorias (genero, director, actor, pais, idioma).

Campos numericos tipicos para usar como `campo_numerico`:
    "vote_average", "vote_count", "popularity", "runtime", "budget", "revenue"

Funciones que contiene:
- promedio_general
- promedio_por_genero
- promedio_por_director
- promedio_por_actor
- promedio_por_pais
- promedio_por_idioma
- peliculas_por_anio
- resumen_estadistico
"""


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar
#       (ej. "vote_average", "runtime", "budget").
# Retorna:
#   float: promedio del campo indicado sobre todas las peliculas del catalogo
#       (ignorando valores nulos/no numericos).
def promedio_general(catalogo: list[dict], campo_numerico: str) -> float:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {genero: promedio} con el promedio de
#       campo_numerico para las peliculas de cada genero.
def promedio_por_genero(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {director: promedio} con el promedio de
#       campo_numerico para las peliculas de cada director.
def promedio_por_director(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {actor: promedio} con el promedio de
#       campo_numerico para las peliculas de cada actor.
def promedio_por_actor(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {pais: promedio} con el promedio de
#       campo_numerico para las peliculas producidas en cada pais.
def promedio_por_pais(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {idioma: promedio} con el promedio de
#       campo_numerico para las peliculas de cada idioma hablado.
def promedio_por_idioma(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
# Retorna:
#   dict[int, int]: diccionario {anio: cantidad_de_peliculas} usando el anio
#       extraido de "release_date".
def peliculas_por_anio(catalogo: list[dict]) -> dict[int, int]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
# Retorna:
#   dict[str, float]: resumen general con indicadores clave, por ejemplo:
#       {"total_peliculas": ..., "promedio_vote_average": ...,
#        "promedio_runtime": ..., "promedio_popularity": ...}
def resumen_estadistico(catalogo: list[dict]) -> dict[str, float]:
    pass  # TODO: implementar
