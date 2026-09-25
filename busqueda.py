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

import unicodedata


# Normaliza un texto para que las comparaciones sean insensibles a
# mayusculas/minusculas, tildes y espacios extra. Ej. " Acción " -> "accion".
# Es un helper privado (no es parte de la API publica del modulo).
def _normalizar(texto: str) -> str:
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().casefold())
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


# Extrae el anio de estreno desde "release_date" (formato "YYYY-MM-DD").
# Devuelve None si la fecha falta o no empieza con un anio valido.
def _anio_estreno(pelicula: dict) -> int | None:
    fecha = pelicula.get("release_date")
    if not isinstance(fecha, str) or len(fecha.strip()) < 4:
        return None
    try:
        return int(fecha.strip()[:4])
    except ValueError:
        return None


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   texto (str): texto (o parte del texto) a buscar en el titulo. Busqueda
#       insensible a mayusculas/minusculas.
# Retorna:
#   list[dict]: peliculas cuyo "title" u "original_title" contienen el texto.
def buscar_por_titulo(catalogo: list[dict], texto: str) -> list[dict]:
    texto_norm = _normalizar(texto)
    if not texto_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if texto_norm in _normalizar(pelicula.get("title") or "")
        or texto_norm in _normalizar(pelicula.get("original_title") or "")
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   nombre_actor (str): nombre (o parte del nombre) de un actor/actriz.
# Retorna:
#   list[dict]: peliculas donde "cast" incluye alguna coincidencia con nombre_actor.
def buscar_por_actor(catalogo: list[dict], nombre_actor: str) -> list[dict]:
    nombre_norm = _normalizar(nombre_actor)
    if not nombre_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("cast"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["cast"])
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   nombre_director (str): nombre (o parte del nombre) de un director.
# Retorna:
#   list[dict]: peliculas donde "directors" incluye alguna coincidencia.
def buscar_por_director(catalogo: list[dict], nombre_director: str) -> list[dict]:
    nombre_norm = _normalizar(nombre_director)
    if not nombre_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("directors"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["directors"])
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   genero (str): nombre del genero (ej. "Comedy", "Drama").
# Retorna:
#   list[dict]: peliculas donde "genres" incluye ese genero.
def buscar_por_genero(catalogo: list[dict], genero: str) -> list[dict]:
    genero_norm = _normalizar(genero)
    if not genero_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("genres"), list)
        and any(genero_norm in _normalizar(nombre or "") for nombre in pelicula["genres"])
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   pais (str): nombre del pais productor (ej. "Argentina").
# Retorna:
#   list[dict]: peliculas donde "production_countries" incluye ese pais.
def buscar_por_pais(catalogo: list[dict], pais: str) -> list[dict]:
    pais_norm = _normalizar(pais)
    if not pais_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("production_countries"), list)
        and any(pais_norm in _normalizar(nombre or "") for nombre in pelicula["production_countries"])
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   idioma (str): idioma hablado (ej. "English") o codigo de "original_language".
# Retorna:
#   list[dict]: peliculas donde "spoken_languages" u "original_language" coinciden.
def buscar_por_idioma(catalogo: list[dict], idioma: str) -> list[dict]:
    idioma_norm = _normalizar(idioma)
    if not idioma_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if _normalizar(pelicula.get("original_language") or "") == idioma_norm
        or (
            isinstance(pelicula.get("spoken_languages"), list)
            and any(idioma_norm in _normalizar(lengua or "") for lengua in pelicula["spoken_languages"])
        )
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   palabra_clave (str): keyword tematica (ej. "friendship", "revenge").
# Retorna:
#   list[dict]: peliculas donde "keywords" incluye esa palabra clave.
def buscar_por_palabra_clave(catalogo: list[dict], palabra_clave: str) -> list[dict]:
    palabra_norm = _normalizar(palabra_clave)
    if not palabra_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("keywords"), list)
        and any(palabra_norm in _normalizar(palabra or "") for palabra in pelicula["keywords"])
    ]


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   filtros (dict): pares campo/valor a combinar con AND, por ejemplo
#       {"genero": "Comedy", "actor": "Tom Hanks", "anio_desde": 1990}.
#       Las claves validas reutilizan los criterios de las funciones anteriores.
#       Claves soportadas: "titulo", "actor", "director", "genero", "pais",
#       "idioma", "keyword" (alias: "palabra_clave"), "anio_desde" y
#       "anio_hasta". Las claves desconocidas se ignoran y los filtros de
#       texto vacios no filtran. Si "filtros" esta vacio, se devuelve una
#       copia del catalogo completo.
# Retorna:
#   list[dict]: peliculas que cumplen todos los filtros indicados a la vez.
def busqueda_combinada(catalogo: list[dict], filtros: dict) -> list[dict]:
    if not isinstance(filtros, dict) or not filtros:
        return list(catalogo)
    resultado = list(catalogo)

    criterios_texto = (
        ("titulo", buscar_por_titulo),
        ("actor", buscar_por_actor),
        ("director", buscar_por_director),
        ("genero", buscar_por_genero),
        ("pais", buscar_por_pais),
        ("idioma", buscar_por_idioma),
    )
    for clave, funcion in criterios_texto:
        valor = filtros.get(clave)
        if isinstance(valor, str) and _normalizar(valor):
            resultado = funcion(resultado, valor)

    palabra = filtros.get("keyword", filtros.get("palabra_clave"))
    if isinstance(palabra, str) and _normalizar(palabra):
        resultado = buscar_por_palabra_clave(resultado, palabra)

    for clave, limite in (("anio_desde", "desde"), ("anio_hasta", "hasta")):
        valor = filtros.get(clave)
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            continue
        try:
            anio = int(valor)
        except (TypeError, ValueError):
            continue
        filtradas = []
        for pelicula in resultado:
            anio_peli = _anio_estreno(pelicula)
            if anio_peli is None:
                continue
            elif limite == "desde" and anio_peli >= anio:
                filtradas.append(pelicula)
            elif limite == "hasta" and anio_peli <= anio:
                filtradas.append(pelicula)
        resultado = filtradas

    return resultado
