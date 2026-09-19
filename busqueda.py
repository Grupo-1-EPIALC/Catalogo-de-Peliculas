"""
busqueda.py

Funciones de busqueda y filtrado sobre el catalogo de peliculas (lista de dict,
ver estructura en `crud.py`). Todas reciben el catalogo ya cargado en memoria
(con `crud.cargar_catalogo`) y devuelven un subconjunto de peliculas que
cumplen el criterio pedido.

Funciones que contiene:
- buscar_por_titulo
- buscar_por_actor
- buscar_por_director
- buscar_por_genero
- buscar_por_pais
- buscar_por_idioma
- buscar_por_palabra_clave
- busqueda_combinada
"""


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   texto (str): texto (o parte del texto) a buscar en el titulo. Busqueda
#       insensible a mayusculas/minusculas.
# Retorna:
#   list[dict]: peliculas cuyo "title" u "original_title" contienen el texto.
def buscar_por_titulo(catalogo: list[dict], texto: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   nombre_actor (str): nombre (o parte del nombre) de un actor/actriz.
# Retorna:
#   list[dict]: peliculas donde "cast" incluye alguna coincidencia con nombre_actor.
def buscar_por_actor(catalogo: list[dict], nombre_actor: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   nombre_director (str): nombre (o parte del nombre) de un director.
# Retorna:
#   list[dict]: peliculas donde "directors" incluye alguna coincidencia.
def buscar_por_director(catalogo: list[dict], nombre_director: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   genero (str): nombre del genero (ej. "Comedy", "Drama").
# Retorna:
#   list[dict]: peliculas donde "genres" incluye ese genero.
def buscar_por_genero(catalogo: list[dict], genero: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   pais (str): nombre del pais productor (ej. "Argentina").
# Retorna:
#   list[dict]: peliculas donde "production_countries" incluye ese pais.
def buscar_por_pais(catalogo: list[dict], pais: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   idioma (str): idioma hablado (ej. "English") o codigo de "original_language".
# Retorna:
#   list[dict]: peliculas donde "spoken_languages" u "original_language" coinciden.
def buscar_por_idioma(catalogo: list[dict], idioma: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   palabra_clave (str): keyword tematica (ej. "friendship", "revenge").
# Retorna:
#   list[dict]: peliculas donde "keywords" incluye esa palabra clave.
def buscar_por_palabra_clave(catalogo: list[dict], palabra_clave: str) -> list[dict]:
    pass  # TODO: implementar


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   filtros (dict): pares campo/valor a combinar con AND, por ejemplo
#       {"genero": "Comedy", "actor": "Tom Hanks", "anio_desde": 1990}.
#       Las claves validas reutilizan los criterios de las funciones anteriores.
# Retorna:
#   list[dict]: peliculas que cumplen todos los filtros indicados a la vez.
def busqueda_combinada(catalogo: list[dict], filtros: dict) -> list[dict]:
    pass  # TODO: implementar
