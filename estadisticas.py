"""
estadisticas.py

Estadisticas sobre un conjunto de peliculas del catalogo. `main.py` arma el
submenu de Estadisticas alrededor de una categoria (genero, director, actor,
pais, idioma, anio) o del catalogo completo ("General"): filtra las
peliculas que corresponden (con `busqueda.py`) y le pasa ese subconjunto a
este modulo.

Para cualquier subconjunto (filtrado o el catalogo completo), `resumen_de_campos`
calcula, para cada campo de `CAMPOS_NUMERICOS`, la media y la mediana, mas un
promedio combinado normalizado a una escala comun de 1 a 10 (para poder
comparar/combinar campos de magnitudes muy distintas, ej. "vote_average" de 0
a 10 junto con "revenue" en millones, sin que el de numeros mas grandes
distorsione el resultado), y la cantidad de peliculas del subconjunto. El
combinado solo usa los campos de `CAMPOS_PROMEDIO_COMBINADO` (todos los de
`CAMPOS_NUMERICOS` salvo "runtime": es una duracion, no un score, y no tiene
sentido promediarla junto al resto); "runtime" igual muestra su media/mediana.

La normalizacion usa siempre el minimo y el maximo del campo en el
**catalogo completo** (no en el subconjunto filtrado) como referencia, para
que el promedio normalizado de "Comedy" y el de "Horror", por ejemplo, esten
en la misma escala y se puedan comparar entre si.

Para la vista "General" (sin filtro), ademas se puede pedir el top 5 de cada
categoria segun "vote_average" promedio (`top5_generos`, `top5_directores`,
etc.).

Funciones que contiene:
- promedio_general
- mediana_general
- rango_de_anios
- promedio_normalizado
- resumen_de_campos
- promedio_por_genero
- promedio_por_director
- promedio_por_actor
- promedio_por_pais
- promedio_por_idioma
- top5_generos
- top5_directores
- top5_actores
- top5_paises
- top5_idiomas
- top5_anios

`promedio_por_genero`/`_director`/`_actor`/`_pais`/`_idioma` no tienen una
opcion de menu propia (las usa `recomendaciones.py` internamente para el
promedio historico de las categorias preferidas del usuario), se mantienen
por eso.

Funciones auxiliares (uso interno del modulo):
- _valor_numerico
- _anio_estreno
- _rango_numerico
- _normalizar_a_escala
- _promedio_por_categoria
- _promedio_por_anio
- _top5
"""

# Campos numericos disponibles en una pelicula del catalogo (se les muestra
# media y mediana en el resumen de estadisticas).
#   "vote_average", "vote_count", "runtime", "revenue"  -> ya numericos en el JSON
#   "budget", "popularity"                              -> vienen como string en
#                                                           el JSON, se convierten
#                                                           a float internamente
CAMPOS_NUMERICOS: list[str] = ["vote_average", "vote_count", "runtime", "revenue", "budget", "popularity"]

# Subconjunto de CAMPOS_NUMERICOS que entra al promedio normalizado combinado.
# No incluye "runtime": es una duracion, no un score/medida de exito, y
# promediarla normalizada junto al resto no tiene sentido (una pelicula mas
# larga no es "mejor"). Su media/mediana igual se muestran (ver CAMPOS_NUMERICOS),
# solo se excluye del combinado.
CAMPOS_PROMEDIO_COMBINADO: list[str] = [campo for campo in CAMPOS_NUMERICOS if campo != "runtime"]


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
#   campo (str): nombre del campo numerico a leer (ej. "vote_average", "budget").
# Retorna:
#   float | None: el valor del campo convertido a float, o None si el campo
#       no existe, es None, no se puede convertir (ej. string vacio o texto
#       no numerico en filas corruptas del dataset original), o es 0. En este
#       dataset un 0 en estos campos (revenue, budget, vote_count, vote_average,
#       popularity, runtime) practicamente siempre significa "dato no
#       disponible", no un cero real, asi que se excluye de las estadisticas
#       igual que un valor faltante (si no, arrastra la media/mediana/promedio
#       normalizado hacia abajo sin representar nada real).
def _valor_numerico(pelicula: dict, campo: str) -> float | None:
    valor = pelicula.get(campo)
    if valor is None:
        return None
    try:
        valor_numerico = float(valor)
    except (TypeError, ValueError):
        return None
    if valor_numerico == 0:
        return None
    return valor_numerico


# Parametros:
#   pelicula (dict): una pelicula del catalogo.
# Retorna:
#   int | None: anio de estreno extraido de "release_date" (formato
#       "YYYY-MM-DD"), o None si la fecha falta o esta mal formada.
def _anio_estreno(pelicula: dict) -> int | None:
    fecha = pelicula.get("release_date")
    if not isinstance(fecha, str) or len(fecha) < 4 or not fecha[:4].isdigit():
        return None
    return int(fecha[:4])


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   tuple[int, int] | None: (anio mas antiguo, anio mas reciente) de estreno
#       en `catalogo`, o None si ninguna pelicula tiene un "release_date"
#       valido.
def rango_de_anios(catalogo: list[dict]) -> tuple[int, int] | None:
    anios = [anio for anio in (_anio_estreno(pelicula) for pelicula in catalogo) if anio is not None]
    if not anios:
        return None
    return min(anios), max(anios)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar
#       (ej. "vote_average", "runtime", "budget").
# Retorna:
#   float: promedio del campo indicado sobre todas las peliculas de
#       `catalogo` con valor valido (ignorando faltantes/no numericos),
#       redondeado a 2 decimales. 0.0 si ninguna pelicula tiene valor valido.
def promedio_general(catalogo: list[dict], campo_numerico: str) -> float:
    valores = [v for v in (_valor_numerico(p, campo_numerico) for p in catalogo) if v is not None]
    if not valores:
        return 0.0
    return round(sum(valores) / len(valores), 2)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a analizar.
# Retorna:
#   float: mediana del campo indicado sobre las peliculas de `catalogo` con
#       valor valido, redondeada a 2 decimales. Con cantidad par de valores,
#       promedia los dos centrales. 0.0 si ninguna pelicula tiene valor valido.
def mediana_general(catalogo: list[dict], campo_numerico: str) -> float:
    valores = sorted(v for v in (_valor_numerico(p, campo_numerico) for p in catalogo) if v is not None)
    if not valores:
        return 0.0
    cantidad = len(valores)
    medio = cantidad // 2
    if cantidad % 2 == 1:
        mediana = valores[medio]
    else:
        mediana = (valores[medio - 1] + valores[medio]) / 2
    return round(mediana, 2)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a inspeccionar.
# Retorna:
#   tuple[float, float] | None: (minimo, maximo) de los valores validos de
#       ese campo en `catalogo`, o None si ninguna pelicula tiene un valor
#       numerico valido.
def _rango_numerico(catalogo: list[dict], campo_numerico: str) -> tuple[float, float] | None:
    valores = [v for v in (_valor_numerico(p, campo_numerico) for p in catalogo) if v is not None]
    if not valores:
        return None
    return min(valores), max(valores)


# Parametros:
#   valor (float): valor a reescalar.
#   minimo (float): valor que se debe mapear a 1.
#   maximo (float): valor que se debe mapear a 10.
# Retorna:
#   float: `valor` reescalado linealmente al rango [1, 10]. Si `minimo` y
#       `maximo` son iguales (todos los valores del campo son identicos, no
#       hay variacion que reescalar), devuelve 5.5 (el punto medio de la
#       escala) en vez de forzar un extremo.
def _normalizar_a_escala(valor: float, minimo: float, maximo: float) -> float:
    if maximo == minimo:
        return 5.5
    return round(1 + 9 * (valor - minimo) / (maximo - minimo), 2)


# Parametros:
#   catalogo_referencia (list[dict]): catalogo completo, usado solo para
#       sacar el minimo/maximo de referencia de `campo_numerico` (para que
#       distintos filtros queden en la misma escala y se puedan comparar).
#   subconjunto (list[dict]): peliculas sobre las que se calcula el promedio
#       (puede ser el mismo `catalogo_referencia`, o un filtro de el).
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   float: promedio de los valores de `campo_numerico` en `subconjunto`, cada
#       uno reescalado individualmente a una escala comun de 1 a 10 segun el
#       minimo/maximo de `catalogo_referencia` (ver `_normalizar_a_escala`)
#       *antes* de promediarlos. 0.0 si `catalogo_referencia` no tiene ningun
#       valor valido para ese campo, o si `subconjunto` no tiene ninguno.
def promedio_normalizado(catalogo_referencia: list[dict], subconjunto: list[dict], campo_numerico: str) -> float:
    rango = _rango_numerico(catalogo_referencia, campo_numerico)
    if rango is None:
        return 0.0
    minimo, maximo = rango

    valores_normalizados = [
        _normalizar_a_escala(valor, minimo, maximo)
        for valor in (_valor_numerico(pelicula, campo_numerico) for pelicula in subconjunto)
        if valor is not None
    ]
    if not valores_normalizados:
        return 0.0
    return round(sum(valores_normalizados) / len(valores_normalizados), 2)


# Parametros:
#   catalogo_referencia (list[dict]): catalogo completo (ver promedio_normalizado).
#   subconjunto (list[dict]): peliculas a resumir (un filtro por categoria,
#       o el mismo `catalogo_referencia` para la vista general).
# Retorna:
#   dict: {
#     "cantidad_peliculas": cantidad de peliculas en `subconjunto`,
#     "medias": {campo: media en sus unidades originales, ...} (CAMPOS_NUMERICOS),
#     "medianas": {campo: mediana en sus unidades originales, ...} (CAMPOS_NUMERICOS),
#     "promedio_normalizado_combinado": promedio simple de los promedios ya
#         reescalados a 1-10 de cada campo de CAMPOS_PROMEDIO_COMBINADO (no
#         incluye "runtime", ver esa constante). 0.0 si esta vacia.
#   }
def resumen_de_campos(catalogo_referencia: list[dict], subconjunto: list[dict]) -> dict:
    medias = {campo: promedio_general(subconjunto, campo) for campo in CAMPOS_NUMERICOS}
    medianas = {campo: mediana_general(subconjunto, campo) for campo in CAMPOS_NUMERICOS}
    normalizados = {
        campo: promedio_normalizado(catalogo_referencia, subconjunto, campo) for campo in CAMPOS_PROMEDIO_COMBINADO
    }

    if normalizados:
        promedio_combinado = round(sum(normalizados.values()) / len(normalizados), 2)
    else:
        promedio_combinado = 0.0

    return {
        "cantidad_peliculas": len(subconjunto),
        "medias": medias,
        "medianas": medianas,
        "promedio_normalizado_combinado": promedio_combinado,
    }


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
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
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): campo numerico a promediar por anio de estreno.
# Retorna:
#   dict[int, float]: {anio: promedio} para cada anio de estreno presente,
#       considerando solo peliculas con anio y valor numerico validos.
def _promedio_por_anio(catalogo: list[dict], campo_numerico: str) -> dict[int, float]:
    sumas: dict[int, float] = {}
    cantidades: dict[int, int] = {}

    for pelicula in catalogo:
        valor = _valor_numerico(pelicula, campo_numerico)
        anio = _anio_estreno(pelicula)
        if valor is None or anio is None:
            continue
        sumas[anio] = sumas.get(anio, 0.0) + valor
        cantidades[anio] = cantidades.get(anio, 0) + 1

    return {anio: round(sumas[anio] / cantidades[anio], 2) for anio in sumas}


# Parametros:
#   promedios (dict): resultado de `_promedio_por_categoria` o `_promedio_por_anio`.
# Retorna:
#   list[tuple]: los 5 pares (categoria, promedio) con mayor promedio,
#       ordenados de mayor a menor.
def _top5(promedios: dict) -> list[tuple]:
    return sorted(promedios.items(), key=lambda item: item[1], reverse=True)[:5]


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {genero: promedio} con el promedio de
#       campo_numerico para las peliculas de cada genero.
def promedio_por_genero(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "genres", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {director: promedio} con el promedio de
#       campo_numerico para las peliculas de cada director.
def promedio_por_director(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "directors", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {actor: promedio} con el promedio de
#       campo_numerico para las peliculas de cada actor.
def promedio_por_actor(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "cast", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {pais: promedio} con el promedio de
#       campo_numerico para las peliculas producidas en cada pais.
def promedio_por_pais(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "production_countries", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
#   campo_numerico (str): nombre del campo numerico a promediar.
# Retorna:
#   dict[str, float]: diccionario {idioma: promedio} con el promedio de
#       campo_numerico para las peliculas de cada idioma hablado.
def promedio_por_idioma(catalogo: list[dict], campo_numerico: str) -> dict[str, float]:
    return _promedio_por_categoria(catalogo, "spoken_languages", campo_numerico)


# Parametros:
#   catalogo (list[dict]): lista de peliculas (tipicamente el catalogo
#       completo, para la vista "General").
# Retorna:
#   list[tuple[str, float]]: los 5 generos con mayor "vote_average" promedio,
#       ordenados de mayor a menor.
def top5_generos(catalogo: list[dict]) -> list[tuple[str, float]]:
    return _top5(promedio_por_genero(catalogo, "vote_average"))


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   list[tuple[str, float]]: los 5 directores con mayor "vote_average"
#       promedio, ordenados de mayor a menor.
def top5_directores(catalogo: list[dict]) -> list[tuple[str, float]]:
    return _top5(promedio_por_director(catalogo, "vote_average"))


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   list[tuple[str, float]]: los 5 actores con mayor "vote_average" promedio,
#       ordenados de mayor a menor.
def top5_actores(catalogo: list[dict]) -> list[tuple[str, float]]:
    return _top5(promedio_por_actor(catalogo, "vote_average"))


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   list[tuple[str, float]]: los 5 paises con mayor "vote_average" promedio,
#       ordenados de mayor a menor.
def top5_paises(catalogo: list[dict]) -> list[tuple[str, float]]:
    return _top5(promedio_por_pais(catalogo, "vote_average"))


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   list[tuple[str, float]]: los 5 idiomas con mayor "vote_average" promedio,
#       ordenados de mayor a menor.
def top5_idiomas(catalogo: list[dict]) -> list[tuple[str, float]]:
    return _top5(promedio_por_idioma(catalogo, "vote_average"))


# Parametros:
#   catalogo (list[dict]): lista de peliculas.
# Retorna:
#   list[tuple[int, float]]: los 5 anios de estreno con mayor "vote_average"
#       promedio, ordenados de mayor a menor.
def top5_anios(catalogo: list[dict]) -> list[tuple[int, float]]:
    return _top5(_promedio_por_anio(catalogo, "vote_average"))
