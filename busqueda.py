"""
busqueda.py

Funciones de busqueda y filtrado sobre el catalogo de peliculas (lista de dict,
ver estructura en `crud.py`). Todas reciben el catalogo ya cargado en memoria
(con `crud.cargar_catalogo`) y devuelven un subconjunto de peliculas que
cumplen el criterio pedido.

Las comparaciones de texto ignoran mayusculas/minusculas, tildes y espacios
extra. Un criterio vacio (solo espacios) no coincide con nada y devuelve [].

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


def buscar_por_titulo(catalogo: list[dict], texto: str) -> list[dict]:
    """Busca peliculas cuyo titulo contiene el texto indicado.

    Coincide si ``texto`` aparece en ``title`` o en ``original_title``
    (coincidencia parcial).

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        texto (str): texto (o parte del texto) a buscar en el titulo.

    Retorna:
        list[dict]: peliculas cuyo ``title`` u ``original_title`` contienen
            el texto. Lista vacia si ``texto`` queda vacio al normalizar.
    """
    texto_norm = _normalizar(texto)
    if not texto_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if texto_norm in _normalizar(pelicula.get("title") or "")
        or texto_norm in _normalizar(pelicula.get("original_title") or "")
    ]


def buscar_por_actor(catalogo: list[dict], nombre_actor: str) -> list[dict]:
    """Busca peliculas en las que participa un actor o actriz.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        nombre_actor (str): nombre (o parte del nombre) a buscar en ``cast``.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``cast`` contiene
            ``nombre_actor``. Se omiten las que no tienen ``cast`` como lista.
            Lista vacia si ``nombre_actor`` queda vacio al normalizar.
    """
    nombre_norm = _normalizar(nombre_actor)
    if not nombre_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("cast"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["cast"])
    ]


def buscar_por_director(catalogo: list[dict], nombre_director: str) -> list[dict]:
    """Busca peliculas dirigidas por una persona.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        nombre_director (str): nombre (o parte del nombre) a buscar en ``directors``.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``directors`` contiene
            ``nombre_director``. Se omiten las que no tienen ``directors`` como lista.
            Lista vacia si ``nombre_director`` queda vacio al normalizar.
    """
    nombre_norm = _normalizar(nombre_director)
    if not nombre_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("directors"), list)
        and any(nombre_norm in _normalizar(nombre or "") for nombre in pelicula["directors"])
    ]


def buscar_por_genero(catalogo: list[dict], genero: str) -> list[dict]:
    """Busca peliculas de un genero.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        genero (str): nombre del genero (ej. ``"Comedy"``, ``"Drama"``).
            Acepta coincidencia parcial (``"com"`` puede matchear ``"Comedy"``).

    Retorna:
        list[dict]: peliculas donde algun elemento de ``genres`` contiene
            ``genero``. Se omiten las que no tienen ``genres`` como lista.
            Lista vacia si ``genero`` queda vacio al normalizar.
    """
    genero_norm = _normalizar(genero)
    if not genero_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("genres"), list)
        and any(genero_norm in _normalizar(nombre or "") for nombre in pelicula["genres"])
    ]


def buscar_por_pais(catalogo: list[dict], pais: str) -> list[dict]:
    """Busca peliculas producidas en un pais.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        pais (str): nombre del pais productor (ej. ``"Argentina"``).
            Acepta coincidencia parcial.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``production_countries``
            contiene ``pais``. Se omiten las que no tienen esa clave como lista.
            Lista vacia si ``pais`` queda vacio al normalizar.
    """
    pais_norm = _normalizar(pais)
    if not pais_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("production_countries"), list)
        and any(pais_norm in _normalizar(nombre or "") for nombre in pelicula["production_countries"])
    ]


def buscar_por_idioma(catalogo: list[dict], idioma: str) -> list[dict]:
    """Busca peliculas por idioma original o idiomas hablados.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        idioma (str): idioma hablado (ej. ``"English"``) o codigo de
            ``original_language`` (ej. ``"en"``). En ``original_language``
            se exige igualdad exacta (ya normalizada); en ``spoken_languages``
            se admite coincidencia parcial.

    Retorna:
        list[dict]: peliculas cuyo ``original_language`` coincide o cuyo
            ``spoken_languages`` incluye el idioma. Lista vacia si ``idioma``
            queda vacio al normalizar.
    """
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


def buscar_por_palabra_clave(catalogo: list[dict], palabra_clave: str) -> list[dict]:
    """Busca peliculas por keyword tematica.

    Parametros:
        catalogo (list[dict]): lista de peliculas del catalogo.
        palabra_clave (str): keyword (ej. ``"friendship"``, ``"revenge"``).
            Acepta coincidencia parcial.

    Retorna:
        list[dict]: peliculas donde algun elemento de ``keywords`` contiene
            ``palabra_clave``. Se omiten las que no tienen ``keywords`` como lista.
            Lista vacia si ``palabra_clave`` queda vacia al normalizar.
    """
    palabra_norm = _normalizar(palabra_clave)
    if not palabra_norm:
        return []
    return [
        pelicula
        for pelicula in catalogo
        if isinstance(pelicula.get("keywords"), list)
        and any(palabra_norm in _normalizar(palabra or "") for palabra in pelicula["keywords"])
    ]


def busqueda_combinada(catalogo: list[dict], filtros: dict) -> list[dict]:
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

    Retorna:
        list[dict]: peliculas que cumplen todos los filtros indicados.
            Si ``filtros`` no es un dict o esta vacio, se devuelve una copia
            del catalogo completo.
    """
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
