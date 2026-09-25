"""
crud.py

Operaciones CRUD (Create, Read, Update, Delete) sobre el catalogo de peliculas
unificado en `data/movies_unified.json` (ver `eda dataset.ipynb`).

Cada "pelicula" es un dict con (entre otras) las claves:
    id (int), title (str), original_title (str), overview (str), tagline (str | None),
    status (str), release_date (str), runtime (float), budget (str), revenue (float),
    popularity (str), vote_average (float), vote_count (float), original_language (str),
    collection (str | None), genres (list[str]), production_companies (list[str]),
    production_countries (list[str]), spoken_languages (list[str]), cast (list[str]),
    directors (list[str]), keywords (list[str])

Funciones que contiene:
- cargar_catalogo
- guardar_catalogo
- obtener_pelicula_por_id
- crear_pelicula
- actualizar_pelicula
- eliminar_pelicula
- agregar_valor_a_lista
- quitar_valor_de_lista
"""

import json

# Helper interno para validar la existencia y el tipo de un campo tipo lista
_CAMPOS_LISTA_VALIDOS = {
    "genres",
    "production_companies",
    "production_countries",
    "spoken_languages",
    "cast",
    "directors",
    "keywords",
}


# Parametros:
#   ruta_json (str): ruta al archivo JSON con el catalogo de peliculas.
# Retorna:
#   list[dict]: lista de peliculas cargadas desde el archivo.
# Manejo de errores esperado:
#   FileNotFoundError si la ruta no existe, json.JSONDecodeError si el archivo
#   esta mal formado. En ambos casos informar un mensaje claro (no dejar que
#   el programa se caiga) y devolver una lista vacia.
def cargar_catalogo(ruta_json: str) -> list[dict]:
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if not isinstance(datos, list):
                print(f"Error: El archivo '{ruta_json}' no contiene una lista de películas válida.")
                return []
            return datos
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{ruta_json}'.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: El archivo '{ruta_json}' está mal formado o corrupto ({e}).")
        return []


# Parametros:
#   catalogo (list[dict]): lista de peliculas a persistir.
#   ruta_json (str): ruta destino del archivo JSON.
# Retorna:
#   None
# Manejo de errores esperado:
#   OSError si no se puede escribir el archivo (permisos, disco, ruta invalida).
def guardar_catalogo(catalogo: list[dict], ruta_json: str) -> None:
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(catalogo, archivo, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Error de E/S al intentar guardar en '{ruta_json}': {e}")


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   id_pelicula (int): id de la pelicula a buscar.
# Retorna:
#   dict | None: la pelicula encontrada, o None si no existe ese id.
def obtener_pelicula_por_id(catalogo: list[dict], id_pelicula: int) -> dict | None:
    for pelicula in catalogo:
        if pelicula.get("id") == id_pelicula:
            return pelicula
    return None


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   nueva_pelicula (dict): pelicula a agregar (debe incluir al menos "id" y "title").
# Retorna:
#   list[dict]: catalogo actualizado con la nueva pelicula agregada.
# Manejo de errores esperado:
#   ValueError si ya existe una pelicula con el mismo "id".
def crear_pelicula(catalogo: list[dict], nueva_pelicula: dict) -> list[dict]:
    if "id" not in nueva_pelicula or "title" not in nueva_pelicula:
        raise ValueError("La nueva película debe incluir obligatoriamente los campos 'id' y 'title'.")

    id_nueva = nueva_pelicula["id"]
    if obtener_pelicula_por_id(catalogo, id_nueva) is not None:
        raise ValueError(f"Ya existe una película en el catálogo con el id {id_nueva}.")

    catalogo.append(nueva_pelicula)
    return catalogo


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   id_pelicula (int): id de la pelicula a modificar.
#   campos_actualizados (dict): pares clave/valor a sobrescribir en la pelicula
#       (ej. {"vote_average": 8.1, "tagline": "Nuevo tagline"}).
# Retorna:
#   list[dict]: catalogo con la pelicula modificada.
# Manejo de errores esperado:
#   ValueError si no existe una pelicula con ese id.
def actualizar_pelicula(catalogo: list[dict], id_pelicula: int, campos_actualizados: dict) -> list[dict]:
    pelicula = obtener_pelicula_por_id(catalogo, id_pelicula)
    if pelicula is None:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    for clave, valor in campos_actualizados.items():
        pelicula[clave] = valor

    return catalogo


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   id_pelicula (int): id de la pelicula a eliminar.
# Retorna:
#   list[dict]: catalogo sin la pelicula eliminada.
# Manejo de errores esperado:
#   ValueError si no existe una pelicula con ese id.
def eliminar_pelicula(catalogo: list[dict], id_pelicula: int) -> list[dict]:
    pelicula = obtener_pelicula_por_id(catalogo, id_pelicula)
    if pelicula is None:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    catalogo.remove(pelicula)
    return catalogo


# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   id_pelicula (int): id de la pelicula a modificar.
#   campo_lista (str): nombre del campo tipo lista a modificar
#       (ej. "genres", "cast", "directors", "keywords", "production_companies",
#       "production_countries", "spoken_languages").
#   valor (str): elemento a agregar a esa lista.
# Retorna:
#   list[dict]: catalogo actualizado.
# Manejo de errores esperado:
#   ValueError si no existe la pelicula o si campo_lista no es un campo de tipo lista.
def agregar_valor_a_lista(catalogo: list[dict], id_pelicula: int, campo_lista: str, valor: str) -> list[dict]:
    pelicula = obtener_pelicula_por_id(catalogo, id_pelicula)
    if pelicula is None:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    if campo_lista not in _CAMPOS_LISTA_VALIDOS or not isinstance(pelicula.get(campo_lista), list):
        raise ValueError(f"El campo '{campo_lista}' no es un campo válido de tipo lista.")

    pelicula[campo_lista].append(valor)
    return catalogo

# Parametros:
#   catalogo (list[dict]): lista de peliculas del catalogo.
#   id_pelicula (int): id de la pelicula a modificar.
#   campo_lista (str): nombre del campo tipo lista a modificar (ver arriba).
#   valor (str): elemento a quitar de esa lista.
# Retorna:
#   list[dict]: catalogo actualizado.
# Manejo de errores esperado:
#   ValueError si no existe la pelicula, si campo_lista no es una lista, o si
#   el valor no estaba presente en la lista.
def quitar_valor_de_lista(catalogo: list[dict], id_pelicula: int, campo_lista: str, valor: str) -> list[dict]:
    pelicula = obtener_pelicula_por_id(catalogo, id_pelicula)
    if pelicula is None:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    if campo_lista not in _CAMPOS_LISTA_VALIDOS or not isinstance(pelicula.get(campo_lista), list):
        raise ValueError(f"El campo '{campo_lista}' no es un campo válido de tipo lista.")

    lista_campo = pelicula[campo_lista]
    if valor not in lista_campo:
        raise ValueError(f"El valor '{valor}' no está presente en la lista de '{campo_lista}'.")

    lista_campo.remove(valor)
    return catalogo