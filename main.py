"""
main.py

Punto de entrada de la aplicacion. Integra los modulos crud.py, busqueda.py,
rankings.py, estadisticas.py y recomendaciones.py detras de un menu por
consola, organizado en un submenu por modulo. Este archivo no tiene logica de
negocio (eso vive en los otros modulos): solo lee la opcion y los datos que
ingresa el usuario, llama a la funcion correspondiente con sus parametros
reales y muestra el resultado.

Funciones que contiene:
- mostrar_menu
- menu_busqueda
- menu_crud
- menu_rankings
- menu_estadisticas
- menu_recomendaciones
- main

Funciones auxiliares (entrada/salida por consola):
- _pedir_entero
- _pedir_lista
- _mostrar_resultado
- _ordenar_por_valor_desc
- _mostrar_listado_peliculas
- _mostrar_detalle_peliculas
"""

import crud
import busqueda
import rankings
import estadisticas
import recomendaciones


# Ruta del archivo con el catalogo unificado generado por `eda dataset.ipynb`.
RUTA_DATOS = "data/movies_unified.json"

MENU_PRINCIPAL: dict[int, str] = {
    1: "Busqueda",
    2: "CRUD de peliculas",
    3: "Rankings",
    4: "Estadisticas",
    5: "Recomendaciones",
    0: "Salir",
}

# busqueda.py
MENU_BUSQUEDA: dict[int, str] = {
    1: "Buscar por titulo",
    2: "Buscar por actor",
    3: "Buscar por director",
    4: "Buscar por genero",
    5: "Buscar por pais",
    6: "Buscar por idioma",
    7: "Buscar por palabra clave",
    8: "Busqueda combinada (varios filtros)",
    0: "Volver al menu principal",
}

# crud.py
MENU_CRUD: dict[int, str] = {
    1: "Ver pelicula por id",
    2: "Agregar pelicula",
    3: "Editar un campo de una pelicula",
    4: "Eliminar pelicula",
    5: "Agregar valor a una lista (genero, actor, etc.)",
    6: "Quitar valor de una lista (genero, actor, etc.)",
    0: "Volver al menu principal",
}

# rankings.py
MENU_RANKINGS: dict[int, str] = {
    1: "Top peliculas (general)",
    2: "Top peliculas por genero",
    3: "Top peliculas por actor",
    4: "Top peliculas por director",
    5: "Ranking de generos por promedio",
    6: "Ranking de actores por promedio",
    7: "Ranking de directores por promedio",
    0: "Volver al menu principal",
}

# estadisticas.py
MENU_ESTADISTICAS: dict[int, str] = {
    1: "Promedio general de un campo",
    2: "Promedio por genero",
    3: "Promedio por director",
    4: "Promedio por actor",
    5: "Promedio por pais",
    6: "Promedio por idioma",
    7: "Cantidad de peliculas por anio",
    8: "Resumen estadistico general",
    0: "Volver al menu principal",
}

# recomendaciones.py
MENU_RECOMENDACIONES: dict[int, str] = {
    1: "Crear perfil de usuario",
    2: "Ver peliculas afines al perfil (sin ordenar)",
    3: "Recomendacion por ranking",
    4: "Recomendacion al azar",
    0: "Volver al menu principal",
}


# Parametros:
#   mensaje (str): texto que se muestra antes de leer la entrada.
# Retorna:
#   int: numero ingresado por el usuario. Vuelve a preguntar si el valor
#       ingresado no es un entero valido (ValueError).
def _pedir_entero(mensaje: str) -> int:
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Ingrese un numero entero valido.")


# Parametros:
#   mensaje (str): texto que se muestra antes de leer la entrada.
# Retorna:
#   list[str]: valores separados por coma, sin espacios sobrantes ni
#       elementos vacios (ej. "Drama, Accion" -> ["Drama", "Accion"]).
def _pedir_lista(mensaje: str) -> list[str]:
    texto = input(mensaje)
    return [valor.strip() for valor in texto.split(",") if valor.strip()]


# Cantidad maxima de filas que se imprimen por consola en un solo resultado.
# Algunos resultados agrupan por actor o director y pueden tener miles de
# claves (ej. promedio_por_actor sobre el dataset completo), asi que sin este
# limite la consola quedaria inundada de lineas.
_LIMITE_RESULTADOS_MOSTRADOS = 20


# Parametros:
#   diccionario (dict[str, float]): resultado de una funcion de promedios
#       (ej. promedio_por_genero, promedio_por_director).
# Retorna:
#   dict[str, float]: el mismo diccionario ordenado de mayor a menor valor,
#       para que al truncar con _LIMITE_RESULTADOS_MOSTRADOS se muestren
#       primero los promedios mas altos (los mas relevantes) y no un
#       subconjunto arbitrario.
def _ordenar_por_valor_desc(diccionario: dict[str, float]) -> dict[str, float]:
    return dict(sorted(diccionario.items(), key=lambda item: item[1], reverse=True))


# Parametros:
#   resultado (object): valor devuelto por una funcion de crud/busqueda/
#       rankings/estadisticas/recomendaciones (lista de peliculas, dict de
#       promedios, lista de tuplas, numero, etc.).
# Retorna:
#   None. Imprime el resultado por consola con un formato legible segun su
#       tipo, truncando a _LIMITE_RESULTADOS_MOSTRADOS filas cuando el
#       resultado es una lista o un diccionario grande.
def _mostrar_resultado(resultado: object) -> None:
    if resultado is None:
        print("(sin resultado)")
    elif isinstance(resultado, list) and resultado and isinstance(resultado[0], dict):
        for pelicula in resultado[:_LIMITE_RESULTADOS_MOSTRADOS]:
            print("-", pelicula.get("title", pelicula))
        if len(resultado) > _LIMITE_RESULTADOS_MOSTRADOS:
            print(f"... y {len(resultado) - _LIMITE_RESULTADOS_MOSTRADOS} peliculas mas.")
    elif isinstance(resultado, dict):
        items = list(resultado.items())
        for clave, valor in items[:_LIMITE_RESULTADOS_MOSTRADOS]:
            print(f"{clave}: {valor}")
        if len(items) > _LIMITE_RESULTADOS_MOSTRADOS:
            print(f"... y {len(items) - _LIMITE_RESULTADOS_MOSTRADOS} mas.")
    elif isinstance(resultado, list):
        for item in resultado[:_LIMITE_RESULTADOS_MOSTRADOS]:
            print("-", item)
        if len(resultado) > _LIMITE_RESULTADOS_MOSTRADOS:
            print(f"... y {len(resultado) - _LIMITE_RESULTADOS_MOSTRADOS} mas.")
    else:
        print(resultado)


# Parametros:
#   peliculas (list[dict]): peliculas en formato "resumen" (busqueda.
#       resumir_pelicula: claves id, title, anio, genres). Se usa para las
#       busquedas que pueden devolver muchos resultados (todas salvo por
#       titulo), asi el usuario anota el id y ve la ficha completa despues
#       (crud, opcion 1).
# Retorna:
#   None. Imprime "- {title} ({anio}) [id: {id}]" por pelicula (sin el
#       parentesis del anio si no hay fecha), truncado a
#       _LIMITE_RESULTADOS_MOSTRADOS. "(sin resultado)" si la lista esta vacia.
def _mostrar_listado_peliculas(peliculas: list[dict]) -> None:
    if not peliculas:
        print("(sin resultado)")
        return

    for pelicula in peliculas[:_LIMITE_RESULTADOS_MOSTRADOS]:
        anio = pelicula.get("anio")
        sufijo_anio = f" ({anio})" if anio is not None else ""
        print(f"- {pelicula.get('title')}{sufijo_anio} [id: {pelicula.get('id')}]")

    if len(peliculas) > _LIMITE_RESULTADOS_MOSTRADOS:
        print(f"... y {len(peliculas) - _LIMITE_RESULTADOS_MOSTRADOS} peliculas mas.")


# Parametros:
#   peliculas (list[dict]): peliculas en formato completo (objeto de
#       pelicula tal cual esta en el catalogo, no el "resumen"). Se usa para
#       la busqueda por titulo, que suele devolver pocos resultados y donde
#       tiene sentido mostrar la ficha completa directamente.
# Retorna:
#   None. Imprime, por pelicula: encabezado "[{id}] {title} ({anio})",
#       generos, director/es y sinopsis (cuando estan disponibles), truncado
#       a _LIMITE_RESULTADOS_MOSTRADOS. "(sin resultado)" si la lista esta vacia.
def _mostrar_detalle_peliculas(peliculas: list[dict]) -> None:
    if not peliculas:
        print("(sin resultado)")
        return

    for pelicula in peliculas[:_LIMITE_RESULTADOS_MOSTRADOS]:
        anio = busqueda.resumir_pelicula(pelicula).get("anio")
        sufijo_anio = f" ({anio})" if anio is not None else ""
        print(f"[{pelicula.get('id')}] {pelicula.get('title')}{sufijo_anio}")

        generos = pelicula.get("genres") or []
        if generos:
            print(f"Generos: {', '.join(generos)}")

        directores = pelicula.get("directors") or []
        if directores:
            print(f"Director/es: {', '.join(directores)}")

        overview = pelicula.get("overview")
        if overview:
            print(overview)
        print()

    if len(peliculas) > _LIMITE_RESULTADOS_MOSTRADOS:
        print(f"... y {len(peliculas) - _LIMITE_RESULTADOS_MOSTRADOS} peliculas mas.")


# Parametros:
#   opciones (dict[int, str]): mapa numero de opcion -> descripcion.
# Retorna:
#   None. Imprime cada opcion por consola.
def mostrar_menu(opciones: dict[int, str]) -> None:
    for numero, descripcion in opciones.items():
        print(f"{numero}. {descripcion}")


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Este submenu solo consulta datos (busqueda.py), no modifica el
#       catalogo. La busqueda por titulo (opcion 1) muestra la ficha
#       completa de cada resultado (suele haber pocos); el resto pide el
#       listado compacto (resumen=True) porque puede haber muchas
#       coincidencias (ej. un actor con decenas de peliculas).
def menu_busqueda(catalogo: list[dict]) -> None:
    while True:
        print("\n--- Busqueda ---")
        mostrar_menu(MENU_BUSQUEDA)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return
        if opcion == 1:
            resultado = busqueda.buscar_por_titulo(catalogo, input("Titulo a buscar: "))
            _mostrar_detalle_peliculas(resultado)
            continue
        if opcion == 2:
            resultado = busqueda.buscar_por_actor(catalogo, input("Nombre del actor: "), resumen=True)
        elif opcion == 3:
            resultado = busqueda.buscar_por_director(catalogo, input("Nombre del director: "), resumen=True)
        elif opcion == 4:
            resultado = busqueda.buscar_por_genero(catalogo, input("Genero: "), resumen=True)
        elif opcion == 5:
            resultado = busqueda.buscar_por_pais(catalogo, input("Pais: "), resumen=True)
        elif opcion == 6:
            resultado = busqueda.buscar_por_idioma(catalogo, input("Idioma: "), resumen=True)
        elif opcion == 7:
            resultado = busqueda.buscar_por_palabra_clave(catalogo, input("Palabra clave: "), resumen=True)
        elif opcion == 8:
            filtros = {
                "titulo": input("Titulo (vacio para omitir): ") or None,
                "genero": input("Genero (vacio para omitir): ") or None,
                "actor": input("Actor (vacio para omitir): ") or None,
                "director": input("Director (vacio para omitir): ") or None,
                "pais": input("Pais (vacio para omitir): ") or None,
                "idioma": input("Idioma (vacio para omitir): ") or None,
                "palabra_clave": input("Palabra clave (vacio para omitir): ") or None,
                "anio_desde": input("Anio desde (vacio para omitir): ") or None,
                "anio_hasta": input("Anio hasta (vacio para omitir): ") or None,
            }
            resultado = busqueda.busqueda_combinada(catalogo, filtros, resumen=True)
        else:
            print("Opcion invalida.")
            continue

        _mostrar_listado_peliculas(resultado)


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   list[dict]: el catalogo, actualizado si el usuario creo/edito/elimino
#       alguna pelicula (crud.py). Cada cambio se persiste de inmediato con
#       crud.guardar_catalogo.
def menu_crud(catalogo: list[dict]) -> list[dict]:
    while True:
        print("\n--- CRUD de peliculas ---")
        mostrar_menu(MENU_CRUD)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return catalogo
        if opcion == 1:
            id_pelicula = _pedir_entero("Id de la pelicula: ")
            _mostrar_resultado(crud.obtener_pelicula_por_id(catalogo, id_pelicula))
            continue

        # Las operaciones que modifican el catalogo (2 a 6) pueden fallar por
        # motivos esperables del usuario (id duplicado, id inexistente, campo
        # de lista invalido, valor no presente): crud.py las señala con
        # ValueError. Sin este try/except, cualquiera de esos casos tumbaba
        # toda la aplicacion.
        try:
            if opcion == 2:
                nueva_pelicula = {
                    "id": _pedir_entero("Id de la nueva pelicula: "),
                    "title": input("Titulo: "),
                }
                catalogo = crud.crear_pelicula(catalogo, nueva_pelicula)
            elif opcion == 3:
                id_pelicula = _pedir_entero("Id de la pelicula a editar: ")
                campo = input("Campo a modificar (ej. title, vote_average, tagline): ")
                valor = input("Nuevo valor: ")
                catalogo = crud.actualizar_pelicula(catalogo, id_pelicula, {campo: valor})
            elif opcion == 4:
                id_pelicula = _pedir_entero("Id de la pelicula a eliminar: ")
                catalogo = crud.eliminar_pelicula(catalogo, id_pelicula)
            elif opcion == 5:
                id_pelicula = _pedir_entero("Id de la pelicula: ")
                campo_lista = input("Campo tipo lista (genres, cast, directors, keywords, production_companies, production_countries, spoken_languages): ")
                valor = input("Valor a agregar: ")
                catalogo = crud.agregar_valor_a_lista(catalogo, id_pelicula, campo_lista, valor)
            elif opcion == 6:
                id_pelicula = _pedir_entero("Id de la pelicula: ")
                campo_lista = input("Campo tipo lista (genres, cast, directors, keywords, production_companies, production_countries, spoken_languages): ")
                valor = input("Valor a quitar: ")
                catalogo = crud.quitar_valor_de_lista(catalogo, id_pelicula, campo_lista, valor)
            else:
                print("Opcion invalida.")
                continue
        except ValueError as error:
            print(f"No se pudo completar la operacion: {error}")
            continue

        crud.guardar_catalogo(catalogo, RUTA_DATOS)


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Este submenu solo consulta datos (rankings.py).
def menu_rankings(catalogo: list[dict]) -> None:
    while True:
        print("\n--- Rankings ---")
        mostrar_menu(MENU_RANKINGS)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return
        if opcion == 1:
            campo = input("Campo de puntuacion (vote_average, popularity, vote_count): ")
            cantidad = _pedir_entero("Cantidad de peliculas: ")
            resultado = rankings.top_peliculas(catalogo, campo, cantidad)
        elif opcion == 2:
            genero = input("Genero: ")
            campo = input("Campo de puntuacion: ")
            cantidad = _pedir_entero("Cantidad de peliculas: ")
            resultado = rankings.top_por_genero(catalogo, genero, campo, cantidad)
        elif opcion == 3:
            actor = input("Actor: ")
            campo = input("Campo de puntuacion: ")
            cantidad = _pedir_entero("Cantidad de peliculas: ")
            resultado = rankings.top_por_actor(catalogo, actor, campo, cantidad)
        elif opcion == 4:
            director = input("Director: ")
            campo = input("Campo de puntuacion: ")
            cantidad = _pedir_entero("Cantidad de peliculas: ")
            resultado = rankings.top_por_director(catalogo, director, campo, cantidad)
        elif opcion == 5:
            campo = input("Campo de puntuacion: ")
            resultado = rankings.ranking_generos(catalogo, campo)
        elif opcion == 6:
            campo = input("Campo de puntuacion: ")
            minimo = _pedir_entero("Minimo de peliculas por actor: ")
            resultado = rankings.ranking_actores(catalogo, campo, minimo)
        elif opcion == 7:
            campo = input("Campo de puntuacion: ")
            minimo = _pedir_entero("Minimo de peliculas por director: ")
            resultado = rankings.ranking_directores(catalogo, campo, minimo)
        else:
            print("Opcion invalida.")
            continue

        _mostrar_resultado(resultado)


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Este submenu solo consulta datos (estadisticas.py).
def menu_estadisticas(catalogo: list[dict]) -> None:
    while True:
        print("\n--- Estadisticas ---")
        mostrar_menu(MENU_ESTADISTICAS)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return
        if opcion == 1:
            campo = input("Campo numerico (vote_average, runtime, budget, revenue, popularity): ")
            resultado = estadisticas.promedio_general(catalogo, campo)
        elif opcion == 2:
            campo = input("Campo numerico: ")
            resultado = _ordenar_por_valor_desc(estadisticas.promedio_por_genero(catalogo, campo))
        elif opcion == 3:
            campo = input("Campo numerico: ")
            resultado = _ordenar_por_valor_desc(estadisticas.promedio_por_director(catalogo, campo))
        elif opcion == 4:
            campo = input("Campo numerico: ")
            resultado = _ordenar_por_valor_desc(estadisticas.promedio_por_actor(catalogo, campo))
        elif opcion == 5:
            campo = input("Campo numerico: ")
            resultado = _ordenar_por_valor_desc(estadisticas.promedio_por_pais(catalogo, campo))
        elif opcion == 6:
            campo = input("Campo numerico: ")
            resultado = _ordenar_por_valor_desc(estadisticas.promedio_por_idioma(catalogo, campo))
        elif opcion == 7:
            resultado = dict(sorted(estadisticas.peliculas_por_anio(catalogo).items()))
        elif opcion == 8:
            resultado = estadisticas.resumen_estadistico(catalogo)
        else:
            print("Opcion invalida.")
            continue

        _mostrar_resultado(resultado)


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Este submenu solo consulta datos (recomendaciones.py); el perfil de
#   usuario se guarda en memoria mientras dura el submenu (no se persiste).
def menu_recomendaciones(catalogo: list[dict]) -> None:
    perfil_usuario: dict | None = None

    while True:
        print("\n--- Recomendaciones ---")
        mostrar_menu(MENU_RECOMENDACIONES)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return
        if opcion == 1:
            nombre = input("Nombre del usuario: ")
            generos_preferidos = _pedir_lista("Generos preferidos (separados por coma): ")
            directores_preferidos = _pedir_lista("Directores preferidos (separados por coma): ")
            actores_preferidos = _pedir_lista("Actores preferidos (separados por coma): ")
            idiomas_preferidos = _pedir_lista("Idiomas preferidos (separados por coma): ")
            perfil_usuario = recomendaciones.crear_perfil_usuario(
                nombre, generos_preferidos, directores_preferidos, actores_preferidos, idiomas_preferidos
            )
            print("Perfil creado.")
            continue

        if perfil_usuario is None:
            print("Primero hay que crear un perfil de usuario (opcion 1).")
            continue

        if opcion == 2:
            resultado = recomendaciones.filtrar_peliculas_por_gustos(catalogo, perfil_usuario)
        elif opcion == 3:
            campo = input("Campo de puntuacion (vote_average, popularity): ")
            cantidad = _pedir_entero("Cantidad de recomendaciones: ")
            resultado = recomendaciones.recomendar_por_ranking(catalogo, perfil_usuario, campo, cantidad)
        elif opcion == 4:
            cantidad = _pedir_entero("Cantidad de recomendaciones: ")
            resultado = recomendaciones.recomendar_al_azar(catalogo, perfil_usuario, cantidad)
        else:
            print("Opcion invalida.")
            continue

        _mostrar_resultado(resultado)


# Parametros: ninguno.
# Retorna:
#   None.
# Flujo:
#   1. Carga el catalogo una vez con crud.cargar_catalogo(RUTA_DATOS).
#   2. Muestra el menu principal en un bucle y deriva cada opcion al submenu
#      del modulo correspondiente (busqueda, crud, rankings, estadisticas,
#      recomendaciones).
#   3. Al salir (opcion 0), persiste el catalogo con crud.guardar_catalogo.
def main() -> None:
    catalogo = crud.cargar_catalogo(RUTA_DATOS) or []

    while True:
        print("\n=== Catalogo de Peliculas ===")
        mostrar_menu(MENU_PRINCIPAL)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            crud.guardar_catalogo(catalogo, RUTA_DATOS)
            print("Hasta la proxima.")
            break
        elif opcion == 1:
            menu_busqueda(catalogo)
        elif opcion == 2:
            catalogo = menu_crud(catalogo)
        elif opcion == 3:
            menu_rankings(catalogo)
        elif opcion == 4:
            menu_estadisticas(catalogo)
        elif opcion == 5:
            menu_recomendaciones(catalogo)
        else:
            print("Opcion invalida.")


if __name__ == "__main__":
    main()
