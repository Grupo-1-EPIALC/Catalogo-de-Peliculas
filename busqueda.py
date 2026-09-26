"""
busqueda.py

Funciones de busqueda y filtrado sobre el catalogo de peliculas (lista de dict,
ver estructura en `crud.py`). Todas reciben el catalogo ya cargado en memoria
(con `crud.cargar_catalogo`) y devuelven un subconjunto de peliculas que
cumplen el criterio pedido.

Las comparaciones de texto ignoran mayusculas/minusculas, tildes y espacios
extra. Un criterio vacio (solo espacios) no coincide con nada y devuelve [].

Formato de los resultados: por defecto cada funcion devuelve el objeto
completo de cada pelicula. Con ``resumen=True`` devuelven un listado compacto
(ver ``resumir_pelicula``): util cuando hay muchas coincidencias y para que el
usuario anote el ``id`` y vea el detalle despues (ej. ``crud`` opcion 1).
``recomendaciones.py`` usa estas funciones con el formato completo (por
defecto), porque necesita leer varios campos de cada pelicula.

Traduccion de categorias: el catalogo tiene los generos en ingles (ej.
``"Comedy"``). ``buscar_por_genero`` primero busca el valor tal cual lo
escribio el usuario; si no encuentra nada, prueba traducirlo de castellano a
ingles con el diccionario de ``categorias_traducciones.json`` (via
``traducir_categoria_a_ingles``) y repite la busqueda con el valor en ingles,
antes de devolver "no encontrado" (lista vacia). Asi ``buscar_por_genero(
catalogo, "terror")`` encuentra las peliculas de ``"Horror"``.

``traducir_categoria_a_ingles`` es publica (sin guion bajo) a proposito:
otros modulos que tambien "eligen" una categoria de genero la importan y la
usan con el mismo criterio (probar la traduccion solo cuando la busqueda
directa no encuentra nada) en vez de reimplementarla:
    - ``rankings.top_por_genero``
    - ``recomendaciones._preferencia_coincide_con_valor`` (usada por
      ``calcular_afinidad`` y ``recomendar_por_ranking`` para los generos
      preferidos del perfil de usuario)

Funciones que contiene:
- resumir_pelicula
- buscar_por_titulo
- buscar_por_actor
- buscar_por_director
- buscar_por_genero
- buscar_por_pais
- buscar_por_idioma
- buscar_por_palabra_clave
- busqueda_combinada
- traducir_categoria_a_ingles

Funciones auxiliares (uso interno del modulo):
- _cargar_traducciones_categorias
- _filtrar_por_genero
"""

import json
import unicodedata
from pathlib import Path

# Diccionario ingles -> castellano de categorias (generos), cargado desde
# categorias_traducciones.json (mismo directorio que este archivo).
_RUTA_TRADUCCIONES_CATEGORIAS = Path(__file__).resolve().parent / "categorias_traducciones.json"


def _normalizar(texto: str) -> str:
    """Normaliza un texto para comparaciones insensibles a forma.

    Quita espacios de los extremos, pasa a minusculas y elimina tildes
    (descomposicion Unicode NFD). Ejemplo: ``" Acción "`` -> ``"accion"``.

    Es un helper privado (no forma parte de la API publica del modulo).

    Parametros:
        texto (str): texto a normalizar. Si no es str, se convierte con ``str()``.

    Retorna:
        str: texto normalizado, listo para comparar con ``in`` o ``==``.
    """
    descompuesto = unicodedata.normalize("NFD", str(texto).strip().casefold())
    return "".join(letra for letra in descompuesto if unicodedata.category(letra) != "Mn")


def _cargar_traducciones_categorias() -> dict[str, str]:
    """Carga el diccionario ingles -> castellano de categorias desde
    ``categorias_traducciones.json``.

    Si el archivo no existe o esta mal formado, devuelve ``{}`` en vez de
    romper: la traduccion es una ayuda extra, no una dependencia critica de
    la busqueda (sin ella, ``buscar_por_genero`` sigue funcionando como
    antes, solo que sin el intento de traduccion).

    Retorna:
        dict[str, str]: ``{categoria_en_ingles: categoria_en_castellano}``.
    """
    try:
        with open(_RUTA_TRADUCCIONES_CATEGORIAS, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, json.JSONDecodeError):
        return {}
    return datos if isinstance(datos, dict) else {}


# Diccionario ingles -> castellano, tal como esta en el JSON.
CATEGORIAS_EN_A_ES: dict[str, str] = _cargar_traducciones_categorias()

# Diccionario castellano (normalizado) -> ingles, derivado del anterior.
# Se normaliza la clave castellana (sin mayusculas ni tildes) para que la
# busqueda de la traduccion sea igual de tolerante que el resto del modulo
# (ej. "terror", "Terror" o "TERROR" deben encontrar lo mismo).
CATEGORIAS_ES_A_EN: dict[str, str] = {
    _normalizar(categoria_es): categoria_en
    for categoria_en, categoria_es in CATEGORIAS_EN_A_ES.items()
}


def traducir_categoria_a_ingles(categoria: str) -> str | None:
    """Traduce una categoria de castellano a ingles usando
    ``categorias_traducciones.json``.

    Funcion publica: ademas de usarla ``buscar_por_genero`` en este modulo,
    la importan otros modulos que tambien comparan/filtran por genero
    (``rankings.py``, ``recomendaciones.py``), para que el criterio de
    traduccion sea el mismo en todos lados (ver el docstring del modulo).

    Parametros:
        categoria (str): nombre de categoria, presumiblemente en castellano
            (ej. ``"terror"``, ``"Ciencia ficcion"``). La comparacion ignora
            mayusculas, tildes y espacios en las puntas.

    Retorna:
        str | None: el nombre en ingles tal como aparece en el catalogo
            (ej. ``"Horror"``), o ``None`` si ``categoria`` no coincide con
            ninguna traduccion conocida.
    """
    return CATEGORIAS_ES_A_EN.get(_normalizar(categoria))


def _anio_estreno(pelicula: dict) -> int | None:
    """Obtiene el anio de estreno a partir de ``release_date``.

    Parametros:
        pelicula (dict): pelicula del catalogo. Se espera ``release_date``
            en formato ``"YYYY-MM-DD"`` (o al menos los cuatro digitos del anio).

    Retorna:
        int | None: anio de estreno, o ``None`` si la fecha falta, no es str
            o los primeros cuatro caracteres no son un entero valido.
    """
    fecha = pelicula.get("release_date")
    if not isinstance(fecha, str) or len(fecha.strip()) < 4:
        return None
    try:
        return int(fecha.strip()[:4])
    except ValueError:
        return None


def resumir_pelicula(pelicula: dict) -> dict:
    """Arma la ficha compacta de una pelicula para mostrar listados.

    Se usa con ``resumen=True`` en las funciones de busqueda, cuando hay
    muchas coincidencias y el objeto completo inundaria la pantalla. El
    ``id`` permite ver el detalle completo despues (ej. ``crud`` opcion 1,
    "Ver pelicula por id").

    Parametros:
        pelicula (dict): pelicula del catalogo (objeto completo).

    Retorna:
        dict: ``{"id": ..., "title": ..., "anio": ... | None,
            "genres": [...]}``. ``anio`` sale de ``release_date`` (``None``
            si no hay fecha valida) y ``genres`` es una copia de la lista
            original (no un alias); si no es una lista, queda ``[]``.
    """
    generos = pelicula.get("genres")
    return {
        "id": pelicula.get("id"),
        "title": pelicula.get("title"),
        "anio": _anio_estreno(pelicula),
        "genres": list(generos) if isinstance(generos, list) else [],
    }


def buscar_por_titulo(catalogo: list[dict], texto: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas cuyo titulo contiene el texto indicado.

    Coincide si ``texto`` aparece en ``title`` o en ``original_title``
    (coincidencia parcial). Es la busqueda que devuelve el objeto completo
    de cada pelicula, para mostrar su ficha detallada.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        texto (str): texto (o parte del texto) a buscar en el titulo.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas cuyo ``title`` u ``original_title`` contienen
            el texto. Lista vacia si ``texto`` queda vacio al normalizar.
    """
    texto_norm = _normalizar(texto)
    if not texto_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if texto_norm in _normalizar(pelicula.get("title") or "")
        or texto_norm in _normalizar(pelicula.get("original_title") or "")
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def buscar_por_actor(catalogo: list[dict], nombre_actor: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas en las que participa un actor o actriz.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        nombre_actor (str): nombre (o parte del nombre) a buscar en ``cast``.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``cast`` contiene
            ``nombre_actor``. Se omiten las que no tienen ``cast`` como lista.
            Lista vacia si ``nombre_actor`` queda vacio al normalizar.
    """
    nombre_norm = _normalizar(nombre_actor)
    if not nombre_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("cast"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["cast"])
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def buscar_por_director(catalogo: list[dict], nombre_director: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas dirigidas por una persona.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        nombre_director (str): nombre (o parte del nombre) a buscar en ``directors``.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``directors`` contiene
            ``nombre_director``. Se omiten las que no tienen ``directors`` como lista.
            Lista vacia si ``nombre_director`` queda vacio al normalizar.
    """
    nombre_norm = _normalizar(nombre_director)
    if not nombre_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("directors"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["directors"])
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def _filtrar_por_genero(catalogo: list[dict], genero_norm: str) -> list[dict]:
    """Filtra ``catalogo`` por un genero ya normalizado (helper interno de
    ``buscar_por_genero``, para no repetir el filtro en el intento original
    y en el reintento con el genero traducido)."""
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("genres"), list)
        and any(genero_norm in _normalizar(nombre or "") for nombre in pelicula["genres"])
    ]


def buscar_por_genero(catalogo: list[dict], genero: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas de un genero.

    El catalogo tiene los generos en ingles. Si ``genero`` no encuentra
    nada tal como se escribio, se intenta traducirlo de castellano a ingles
    (``categorias_traducciones.json``, via ``traducir_categoria_a_ingles``)
    y se repite la busqueda con el valor en ingles antes de devolver "no
    encontrado". Ej.: ``buscar_por_genero(catalogo, "terror")`` encuentra
    las peliculas de ``"Horror"``.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        genero (str): nombre del genero, en ingles o castellano (ej.
            ``"Comedy"`` o ``"comedia"``). Acepta coincidencia parcial
            (``"com"`` puede matchear ``"Comedy"``).
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``genres`` contiene
            ``genero`` (o su traduccion al ingles). Se omiten las que no
            tienen ``genres`` como lista. Lista vacia si ``genero`` queda
            vacio al normalizar, o si no hay coincidencias ni traduccion.
    """
    genero_norm = _normalizar(genero)
    if not genero_norm:
        return []

    encontradas = _filtrar_por_genero(catalogo, genero_norm)

    if not encontradas:
        genero_en_ingles = traducir_categoria_a_ingles(genero)
        if genero_en_ingles is not None:
            encontradas = _filtrar_por_genero(catalogo, _normalizar(genero_en_ingles))

    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def buscar_por_pais(catalogo: list[dict], pais: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas producidas en un pais.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        pais (str): nombre del pais productor (ej. ``"Argentina"``).
            Acepta coincidencia parcial.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``production_countries``
            contiene ``pais``. Se omiten las que no tienen esa clave como lista.
            Lista vacia si ``pais`` queda vacio al normalizar.
    """
    pais_norm = _normalizar(pais)
    if not pais_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("production_countries"), list)
        and any(pais_norm in _normalizar(nombre or "") for nombre in pelicula["production_countries"])
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def buscar_por_idioma(catalogo: list[dict], idioma: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas por idioma original o idiomas hablados.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        idioma (str): idioma hablado (ej. ``"English"``) o codigo de
            ``original_language`` (ej. ``"en"``). En ``original_language``
            se exige igualdad exacta (ya normalizada); en ``spoken_languages``
            se admite coincidencia parcial.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas cuyo ``original_language`` coincide o cuyo
            ``spoken_languages`` incluye el idioma. Lista vacia si ``idioma``
            queda vacio al normalizar.
    """
    idioma_norm = _normalizar(idioma)
    if not idioma_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if _normalizar(pelicula.get("original_language") or "") == idioma_norm
        or (
            isinstance(pelicula.get("spoken_languages"), list)
            and any(idioma_norm in _normalizar(lengua or "") for lengua in pelicula["spoken_languages"])
        )
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def buscar_por_palabra_clave(catalogo: list[dict], palabra_clave: str, resumen: bool = False) -> list[dict]:
    """Busca peliculas por keyword tematica.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        palabra_clave (str): keyword (ej. ``"friendship"``, ``"revenge"``).
            Acepta coincidencia parcial.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``keywords`` contiene
            ``palabra_clave``. Se omiten las que no tienen ``keywords`` como lista.
            Lista vacia si ``palabra_clave`` queda vacia al normalizar.
    """
    palabra_norm = _normalizar(palabra_clave)
    if not palabra_norm:
        return []
    encontradas = [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("keywords"), list)
        and any(palabra_norm in _normalizar(palabra or "") for palabra in pelicula["keywords"])
    ]
    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in encontradas]
    return encontradas


def busqueda_combinada(catalogo: list[dict], filtros: dict, resumen: bool = False) -> list[dict]:
    """Filtra el catalogo aplicando varios criterios a la vez (AND).

    Cada clave de ``filtros`` reutiliza una funcion de busqueda de este modulo.
    Las claves desconocidas se ignoran. Los filtros de texto vacios no se
    aplican. Los anios que no se pueden convertir a ``int`` se ignoran.
    Las peliculas sin anio de estreno valido quedan fuera si hay filtro de anio.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        filtros (dict): pares campo/valor, por ejemplo
            ``{"genero": "Comedy", "actor": "Tom Hanks", "anio_desde": 1990}``.

            Claves soportadas:
                - ``titulo``, ``actor``, ``director``, ``genero``, ``pais``,
                  ``idioma``: texto, coincidencia parcial.
                - ``keyword`` (alias: ``palabra_clave``): keyword tematica.
                - ``anio_desde`` / ``anio_hasta``: inclusive, segun
                  ``release_date``. Aceptan int o str convertible a int.
        resumen (bool): si es True, devuelve el listado compacto de
            ``resumir_pelicula`` en vez del objeto completo. Por defecto False.
            Los filtros siempre se aplican sobre el objeto completo.

    Retorna:
        list[dict]: peliculas que cumplen todos los filtros indicados.
            Si ``filtros`` no es un dict o esta vacio, se devuelve una copia
            del catalogo completo.
    """
    if not isinstance(filtros, dict) or not filtros:
        if resumen:
            return [resumir_pelicula(pelicula) for pelicula in catalogo]
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

    if resumen:
        return [resumir_pelicula(pelicula) for pelicula in resultado]
    return resultado
