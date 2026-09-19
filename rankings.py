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
"""


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a usar para ordenar
#       (ej. "vote_average", "popularity", "vote_count").
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas con mayor valor en campo_puntuacion,
#       ordenadas de mayor a menor.
def top_peliculas(catalogo: list[dict], campo_puntuacion: str, cantidad: int) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   genero (str): genero a filtrar (ej. "Animation").
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese genero con mayor puntuacion.
def top_por_genero(catalogo: list[dict], genero: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   actor (str): nombre del actor/actriz a filtrar.
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese actor con mayor puntuacion.
def top_por_actor(catalogo: list[dict], actor: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   director (str): nombre del director a filtrar.
#   campo_puntuacion (str): campo numerico a usar para ordenar.
#   cantidad (int): cantidad maxima de peliculas a devolver.
# Retorna:
#   list[dict]: las `cantidad` peliculas de ese director con mayor puntuacion.
def top_por_director(catalogo: list[dict], director: str, campo_puntuacion: str, cantidad: int) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por genero.
# Retorna:
#   list[tuple[str, float]]: lista de (genero, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_generos(catalogo: list[dict], campo_puntuacion: str) -> list[tuple[str, float]]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por actor.
#   minimo_peliculas (int): cantidad minima de peliculas que debe tener un
#       actor para entrar en el ranking (evita promedios poco representativos).
# Retorna:
#   list[tuple[str, float]]: lista de (actor, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_actores(catalogo: list[dict], campo_puntuacion: str, minimo_peliculas: int) -> list[tuple[str, float]]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_puntuacion (str): campo numerico a promediar por director.
#   minimo_peliculas (int): cantidad minima de peliculas que debe tener un
#       director para entrar en el ranking.
# Retorna:
#   list[tuple[str, float]]: lista de (director, puntuacion_promedio) ordenada
#       de mayor a menor promedio.
def ranking_directores(catalogo: list[dict], campo_puntuacion: str, minimo_peliculas: int) -> list[tuple[str, float]]:
    pass  # TODO: implementar
