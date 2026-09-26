"""
crud.py

Operaciones CRUD (Create, Read, Update, Delete) sobre el catálogo de películas.
La ruta por defecto (`env.RUTA_DATOS`) esta centralizada en `env.py` junto con
las demas rutas de archivos de la aplicacion.

Cada "pelicula" es un dict con (entre otras) las claves:
    id (int), title (str), original_title (str), overview (str), tagline (str | None),
    status (str), release_date (str), runtime (float), budget (str), revenue (float),
    popularity (str), vote_average (float), vote_count (float), original_language (str),
    collection (str | None), genres (list[str]), production_companies (list[str]),
    production_countries (list[str]), spoken_languages (list[str]), cast (list[str]),
    directors (list[str]), keywords (list[str])

    DISEÑO FINAL DE ARQUITECTURA:
1. Módulo Autosuficiente: Las funciones ya no reciben `catalogo` por parámetro.
   El módulo se encarga internamente de leer, modificar y guardar el archivo JSON.
2. Ejecución Sincrónica Estándar: Sin async/await innecesario. La escritura en
   disco es bloqueante y secuencial, garantizando que el archivo se guarde antes
   de retornar.
3. Retorno del JSON Persistido: Cada operación de modificación retorna la lista 
   actualizada `list[dict]` leída desde el archivo tras la persistencia.
   esto asegura que lo devuelto refleje el estado real del archivo 
   y no un objeto en memoria que podría estar desactualizado.
4. Función `obtener_id_por_titulo`: Permite recuperar el ID de una película a partir 
   de su título (case-insensitive) para facilitar la usabilidad en el menú.

Funciones que contiene:
- cargar_catalogo
- guardar_catalogo
- obtener_pelicula_por_id
- obtener_id_por_titulo
- crear_pelicula
- actualizar_pelicula
- eliminar_pelicula
- agregar_valor_a_lista
- quitar_valor_de_lista
"""

import json

from env import RUTA_DATOS

_CAMPOS_LISTA_VALIDOS = {
    "genres",
    "production_companies",
    "production_countries",
    "spoken_languages",
    "cast",
    "directors",
    "keywords",
}


# Parámetros:
#   ruta_json (str): ruta al archivo JSON con el catálogo de películas.
# Retorna:
#   list[dict]: lista de películas cargadas desde el archivo.
# Manejo de errores esperado:
#   FileNotFoundError si la ruta no existe, json.JSONDecodeError si el archivo
#   está mal formado. En ambos casos informar un mensaje claro (no dejar que
#   el programa se caiga) y devolver una lista vacía.
def cargar_catalogo(ruta_json: str = RUTA_DATOS) -> list[dict]:
    try:
        with open(ruta_json, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            if not isinstance(datos, list):
                print(f"Error: El archivo '{ruta_json}' no contiene una lista válida.")
                return []
            return datos
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta '{ruta_json}'.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error: El archivo '{ruta_json}' está mal formado o corrupto ({e}).")
        return []


# Parámetros:
#   catalogo (list[dict]): lista de películas a persistir.
#   ruta_json (str): ruta destino del archivo JSON.
# Retorna:
#   None
# Manejo de errores esperado:
#   OSError si no se puede escribir el archivo (permisos, disco, ruta inválida).
def guardar_catalogo(catalogo: list[dict], ruta_json: str = RUTA_DATOS) -> None:
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(catalogo, archivo, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Error de E/S al intentar guardar en '{ruta_json}': {e}")


# Parámetros:
#   id_pelicula (int): id de la película a buscar.
#   ruta_json (str): ruta al archivo JSON con el catálogo.
# Retorna:
#   dict | None: la película encontrada, o None si no existe ese id.
def obtener_pelicula_por_id(id_pelicula: int, ruta_json: str = RUTA_DATOS) -> dict | None:
    catalogo = cargar_catalogo(ruta_json)
    try:
        return next(pelicula for pelicula in catalogo if pelicula.get("id") == id_pelicula)
    except StopIteration:
        return None


# Parámetros:
#   titulo (str): título de la película a buscar.
#   ruta_json (str): ruta al archivo JSON con el catálogo.
# Retorna:
#   int | None: el ID de la película encontrada (coincidencia exacta case-insensitive), o None si no existe.
def obtener_id_por_titulo(titulo: str, ruta_json: str = RUTA_DATOS) -> int | None:
    catalogo = cargar_catalogo(ruta_json)
    titulo_normalizado = titulo.strip().lower()
    try:
        pelicula = next(
            p for p in catalogo if str(p.get("title", "")).strip().lower() == titulo_normalizado
        )
        return pelicula.get("id")
    except StopIteration:
        return None


# Parámetros:
#   nueva_pelicula (dict): película a agregar (debe incluir al menos "id" y "title").
#   ruta_json (str): ruta al archivo JSON con el catálogo a actualizar.
# Retorna:
#   list[dict]: catálogo actualizado y persistido leídos desde el archivo.
# Manejo de errores esperado:
#   ValueError si no incluye campos obligatorios o si ya existe una película con el mismo "id".
def crear_pelicula(nueva_pelicula: dict, ruta_json: str = RUTA_DATOS) -> list[dict]:
    try:
        id_nueva = nueva_pelicula["id"]
        _ = nueva_pelicula["title"]
    except KeyError as e:
        raise ValueError(f"La nueva película debe incluir obligatoriamente la clave {e}.")

    catalogo = cargar_catalogo(ruta_json)

    if any(p.get("id") == id_nueva for p in catalogo):
        raise ValueError(f"Ya existe una película en el catálogo con el id {id_nueva}.")

    catalogo.append(nueva_pelicula)
    guardar_catalogo(catalogo, ruta_json)
    return cargar_catalogo(ruta_json)


# Parámetros:
#   id_pelicula (int): id de la película a modificar.
#   campos_actualizados (dict): pares clave/valor a sobrescribir en la película
#       (ej. {"vote_average": 8.1, "tagline": "Nuevo tagline"}).
#   ruta_json (str): ruta al archivo JSON con el catálogo a actualizar.
# Retorna:
#   list[dict]: catálogo actualizado con la película modificada.
# Manejo de errores esperado:
#   ValueError si no existe una película con ese id.
def actualizar_pelicula(
    id_pelicula: int, campos_actualizados: dict, ruta_json: str = RUTA_DATOS
) -> list[dict]:
    catalogo = cargar_catalogo(ruta_json)
    try:
        pelicula = next(p for p in catalogo if p.get("id") == id_pelicula)
    except StopIteration:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    pelicula.update(campos_actualizados)
    guardar_catalogo(catalogo, ruta_json)
    return cargar_catalogo(ruta_json)

# Parámetros:
#   id_pelicula (int): id de la película a eliminar.
#   ruta_json (str): ruta al archivo JSON con el catálogo a actualizar.
# Retorna:
#   list[dict]: catálogo actualizado sin la película eliminada.
# Manejo de errores esperado:
#   ValueError si no existe una película con ese id.
def eliminar_pelicula(id_pelicula: int, ruta_json: str = RUTA_DATOS) -> list[dict]:
    catalogo = cargar_catalogo(ruta_json)
    try:
        pelicula = next(p for p in catalogo if p.get("id") == id_pelicula)
        catalogo.remove(pelicula)
    except StopIteration:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")

    guardar_catalogo(catalogo, ruta_json)
    return cargar_catalogo(ruta_json)

# Parámetros:
#   id_pelicula (int): id de la película a modificar.
#   campo_lista (str): nombre del campo tipo lista a modificar
#       (ej. "genres", "cast", "directors", "keywords", "production_companies",
#       "production_countries", "spoken_languages").
#   valor (str): elemento a agregar a esa lista.
#   ruta_json (str): ruta al archivo JSON con el catálogo a actualizar.
# Retorna:
#   list[dict]: catálogo actualizado.
# Manejo de errores esperado:
#   ValueError si no existe la película o si campo_lista no es un campo de tipo lista.
def agregar_valor_a_lista(
    id_pelicula: int, campo_lista: str, valor: str, ruta_json: str = RUTA_DATOS
) -> list[dict]:
    if campo_lista not in _CAMPOS_LISTA_VALIDOS:
        raise ValueError(f"El campo '{campo_lista}' no es un campo válido de tipo lista.")

    catalogo = cargar_catalogo(ruta_json)
    try:
        pelicula = next(p for p in catalogo if p.get("id") == id_pelicula)
        pelicula[campo_lista].append(valor)
    except StopIteration:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")
    except (KeyError, AttributeError):
        raise ValueError(f"El campo '{campo_lista}' no existe o no es una lista válida en la película.")

    guardar_catalogo(catalogo, ruta_json)
    return cargar_catalogo(ruta_json)


# Parámetros:
#   id_pelicula (int): id de la película a modificar.
#   campo_lista (str): nombre del campo tipo lista a modificar (ver arriba).
#   valor (str): elemento a quitar de esa lista.
#   ruta_json (str): ruta al archivo JSON con el catálogo a actualizar.
# Retorna:
#   list[dict]: catálogo actualizado.
# Manejo de errores esperado:
#   ValueError si no existe la película, si campo_lista no es una lista, o si
#   el valor no estaba presente en la lista.
def quitar_valor_de_lista(
    id_pelicula: int, campo_lista: str, valor: str, ruta_json: str = RUTA_DATOS
) -> list[dict]:
    if campo_lista not in _CAMPOS_LISTA_VALIDOS:
        raise ValueError(f"El campo '{campo_lista}' no es un campo válido de tipo lista.")

    catalogo = cargar_catalogo(ruta_json)
    try:
        pelicula = next(p for p in catalogo if p.get("id") == id_pelicula)
        pelicula[campo_lista].remove(valor)
    except StopIteration:
        raise ValueError(f"No existe ninguna película con el id {id_pelicula}.")
    except (KeyError, AttributeError):
        raise ValueError(f"El campo '{campo_lista}' no es una lista válida en la película.")
    except ValueError:
        raise ValueError(f"El valor '{valor}' no está presente en la lista de '{campo_lista}'.")

    guardar_catalogo(catalogo, ruta_json)
    return cargar_catalogo(ruta_json)