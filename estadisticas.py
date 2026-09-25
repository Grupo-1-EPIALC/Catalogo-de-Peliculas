"""
estadisticas.py

Funciones que calculan indicadores y promedios sobre el catalogo de peliculas,
agrupando por distintas categorias (genero, director, actor, pais, idioma).

Campos numericos tipicos para usar como `campo_numerico`:
    "vote_average", "vote_count", "runtime", "revenue"  -> ya numericos en el JSON
    "budget", "popularity"                              -> vienen como string en
                                                            el JSON, se convierten
                                                            a float internamente

Todos los promedios se devuelven redondeados a 2 decimales.

Funciones que contiene:
- promedio_general
- promedio_por_genero
- promedio_por_director
- promedio_por_actor
- promedio_por_pais
- promedio_por_idioma
- peliculas_por_anio
- resumen_estadistico

Funciones auxiliares (uso interno del modulo):
- _valor_numerico
- _promedio_por_categoria
"""


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
#   campo (str): nombre del campo numerico a leer (ej. "vote_average", "budget").
# Retorna:
#   float | None: el valor del campo convertido a float, o None si el campo
#       no existe, es None, o no se puede convertir (ej. string vacio o texto
#       no numerico en filas corruptas del dataset original).
def _valor_numerico(pelicula: dict, campo: str) -> float | None:
    valor = pelicula.get(campo)
    if valor is None:
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_lista (str): campo de tipo lista por el que agrupar
#       (ej. "genres", "directors", "cast", "production_countries", "spoken_languages").
#   campo_numerico (str): campo numerico a promediar dentro de cada grupo.
# Retorna:
#   dict[str, float]: {valor_de_la_categoria: promedio} para cada valor que
#       aparece en campo_lista, considerando solo peliculas con un valor
#       numerico valido en campo_numerico. Una pelicula con varios valores en
#       campo_lista (ej. varios generos) suma a cada uno de ellos.
def _promedio_por_categoria(catalogo: list[dict], campo_lista: str, campo_numerico: str) -> dict[str, float]:
    sumas: dict[str, float] = {}
    cantidades: dict[str, int] = {}

    for pelicula in catalogo:
        valor = _valor_numerico(pelicula, campo_numerico)
        if valor is None:
            continue
        for categoria in pelicula.get(campo_lista) or []:
            sumas[categoria] = sumas.get(categoria, 0.0) + valor
            cantidades[categoria] = cantidades.get(categoria, 0) + 1

    return {categoria: round(sumas[categoria] / cantidades[categoria], 2) for categoria in sumas}


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar
#       (ej. "vote_average", "runtime", "budget").
# Retorna:
#   float: promedio del campo indicado sobre todas las peliculas del catalogo
#       con valor valido (ignorando faltantes/no numericos), redondeado a 2
#       decimales. 0.0 si ninguna pelicula tiene valor valido.
def promedio_general(catalogo: list[dict], campo_numerico: str) -> float:
    valores = [v for v in (_valor_numerico(p, campo_numerico) for p in catalogo) if v is not None]
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), 2)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {genero: promedio} con el promedio de
#       campo_numerico para las peliculas de cada genero.
def promedio_por_genero(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "genres", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {director: promedio} con el promedio de
#       campo_numerico para las peliculas de cada director.
def promedio_por_director(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "directors", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {actor: promedio} con el promedio de
#       campo_numerico para las peliculas de cada actor.
def promedio_por_actor(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "cast", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {pais: promedio} con el promedio de
#       campo_numerico para las peliculas producidas en cada pais.
def promedio_por_pais(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "production_countries", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {idioma: promedio} con el promedio de
#       campo_numerico para las peliculas de cada idioma hablado.
def promedio_por_idioma(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "spoken_languages", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
# Retorna:
#   dict[int, int]: diccionario {anio: cantidad_de_peliculas} usando el anio
#       extraido de "release_date" (formato "YYYY-MM-DD"). Se ignoran las
#       peliculas sin fecha o con fecha mal formada.
def peliculas_por_anio(catalogo: list[dict]) -> dict[int, int]:
    conteo: dict[int, int] = {}

    for pelicula in catalogo:
        fecha = pelicula.get("release_date")
        if not isinstance(fecha, str) or len(fecha) < 4 or not fecha[:4].isdigit():
            continue
        anio = int(fecha[:4])
        conteo[anio] = conteo.get(anio, 0) + 1

    return conteo


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
# Retorna:
#   dict[str, float]: resumen general con indicadores clave:
#       {"total_peliculas": ..., "promedio_vote_average": ...,
#        "promedio_runtime": ..., "promedio_popularity": ...}
def resumen_estadistico(catalogo: list[dict]) -> dict[str, float]:
    return {
        "total_peliculas": len(catalogo),
        "promedio_vote_average": promedio_general(catalogo, "vote_average"),
        "promedio_runtime": promedio_general(catalogo, "runtime"),
        "promedio_popularity": promedio_general(catalogo, "popularity"),
    }
