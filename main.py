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
- _mostrar_listado_peliculas
- _mostrar_detalle_peliculas
- _mostrar_resumen_de_campos
- _mostrar_perfiles
"""

import sys

import crud
import busqueda
import rankings
import estadisticas
import recomendaciones


# Ruta del archivo con el catalogo unificado generado por `eda dataset.ipynb`.
#RUTA_DATOS = "data/movies_unified.json"
RUTA_DATOS = 'data/movies_sample_representativa.json'

# Ruta del archivo con los perfiles de usuario de recomendaciones.py
# (separado del catalogo de peliculas: son entidades distintas).
RUTA_PERFILES = "data/perfiles_usuario.json"

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
    1: "Buscar id por titulo",
    2: "Ver pelicula por id",
    3: "Agregar pelicula",
    4: "Editar un campo de una pelicula",
    5: "Eliminar pelicula",
    6: "Agregar valor a una lista (genero, actor, etc.)",
    7: "Quitar valor de una lista (genero, actor, etc.)",
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
    1: "Genero",
    2: "Director",
    3: "Actor",
    4: "Pais",
    5: "Idioma",
    6: "Anio",
    7: "General (todo el catalogo)",
    0: "Volver al menu principal",
}

# recomendaciones.py
MENU_RECOMENDACIONES: dict[int, str] = {
    1: "Crear perfil de usuario",
    2: "Ver perfiles guardados",
    3: "Usar un perfil guardado",
    4: "Editar perfil guardado",
    5: "Eliminar perfil guardado",
    6: "Ver peliculas afines al perfil activo (sin ordenar)",
    7: "Recomendacion por ranking",
    8: "Recomendacion al azar",
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
#   list[dict]: el catalogo actualizado tras aplicar las operaciones del CRUD.
def menu_crud(catalogo: list[dict]) -> list[dict]:
    while True:
        print("\n--- CRUD de peliculas ---")
        mostrar_menu(MENU_CRUD)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return catalogo

        if opcion == 1:
            titulo = input("Titulo de la pelicula a buscar: ")
            # MODIFICACION: Nueva opcion 1 que consulta la ID usando el modulo crud
            _mostrar_resultado(crud.obtener_id_por_titulo(titulo))
            continue
        
        if opcion == 2:
            id_pelicula = _pedir_entero("Id de la pelicula: ")
            # MODIFICACION: Se elimina el parametro 'catalogo', crud.py consulta directo la fuente
            _mostrar_resultado(crud.obtener_pelicula_por_id(id_pelicula))
            continue

        try:
            if opcion == 3:
                nueva_pelicula = {
                    "id": _pedir_entero("Id de la nueva pelicula: "),
                    "title": input("Titulo: "),
                }
                # MODIFICACION: Se elimina 'catalogo' como primer parametro. 
                # crud.crear_pelicula se encarga de guardar en disco y devuelve el catalogo actualizado.
                catalogo = crud.crear_pelicula(nueva_pelicula)

            elif opcion == 4:
                id_pelicula = _pedir_entero("Id de la pelicula a editar: ")
                campo = input("Campo a modificar (ej. title, vote_average, tagline): ")
                valor = input("Nuevo valor: ")
                # MODIFICACION: Se remueve el parametro 'catalogo'.
                catalogo = crud.actualizar_pelicula(id_pelicula, {campo: valor})

            elif opcion == 5:
                id_pelicula = _pedir_entero("Id de la pelicula a eliminar: ")
                # MODIFICACION: Se remueve el parametro 'catalogo'.
                catalogo = crud.eliminar_pelicula(id_pelicula)

            elif opcion == 6:
                id_pelicula = _pedir_entero("Id de la pelicula: ")
                campo_lista = input("Campo tipo lista (genres, cast, directors, keywords, production_companies, production_countries, spoken_languages): ")
                valor = input("Valor a agregar: ")
                # MODIFICACION: Se remueve el parametro 'catalogo'.
                catalogo = crud.agregar_valor_a_lista(id_pelicula, campo_lista, valor)

            elif opcion == 7:
                id_pelicula = _pedir_entero("Id de la pelicula: ")
                campo_lista = input("Campo tipo lista (genres, cast, directors, keywords, production_companies, production_countries, spoken_languages): ")
                valor = input("Valor a quitar: ")
                # MODIFICACION: Se remueve el parametro 'catalogo'.
                catalogo = crud.quitar_valor_de_lista(id_pelicula, campo_lista, valor)

            else:
                print("Opcion invalida.")
                continue

            print("Operacion realizada y guardada exitosamente.")

        except ValueError as error:
            print(f"No se pudo completar la operacion: {error}")
            continue

        # MODIFICACION: Se elimino la llamada manual 'crud.guardar_catalogo(catalogo, RUTA_DATOS)' 
        # que estaba aqui al final, ya que el modulo crud.py autosuficiente guarda en disco 
        # e integra la persistencia dentro de cada operacion.


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
#   resumen (dict): resultado de estadisticas.resumen_de_campos.
# Retorna:
#   None. Imprime la cantidad de peliculas, la media y mediana de cada campo
#       numerico (estadisticas.CAMPOS_NUMERICOS) y el promedio normalizado
#       combinado (escala 1-10).
def _mostrar_resumen_de_campos(resumen: dict) -> None:
    print(f"Cantidad de peliculas: {resumen['cantidad_peliculas']}")
    for campo in estadisticas.CAMPOS_NUMERICOS:
        media = resumen["medias"][campo]
        mediana = resumen["medianas"][campo]
        print(f"{campo} -> media: {media} | mediana: {mediana}")
    print(f"Promedio normalizado combinado (escala 1-10): {resumen['promedio_normalizado_combinado']}")


# Parametros:
#   perfiles (list[dict]): perfiles de usuario de recomendaciones.py.
# Retorna:
#   None. Imprime id, nombre y preferencias de cada perfil. "No hay perfiles
#       guardados." si la lista esta vacia.
def _mostrar_perfiles(perfiles: list[dict]) -> None:
    if not perfiles:
        print("No hay perfiles guardados.")
        return
    for perfil in perfiles:
        print(
            f"{perfil['id']}: {perfil['nombre']}"
            f" | generos: {perfil['generos']}"
            f" | directores: {perfil['directores']}"
            f" | actores: {perfil['actores']}"
            f" | idiomas: {perfil['idiomas']}"
        )


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Este submenu solo consulta datos (busqueda.py + estadisticas.py),
#       no modifica el catalogo. Las opciones 1 a 6 filtran el catalogo por
#       un valor de esa categoria (via busqueda.py, que ya soporta genero en
#       castellano o ingles) y muestran sus estadisticas
#       (estadisticas.resumen_de_campos); la opcion 7 hace lo mismo sobre el
#       catalogo completo y ademas muestra el top 5 de cada categoria.
def menu_estadisticas(catalogo: list[dict]) -> None:
    while True:
        print("\n--- Estadisticas ---")
        mostrar_menu(MENU_ESTADISTICAS)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            return
        if opcion == 1:
            valor = input("Genero a consultar: ")
            subconjunto = busqueda.buscar_por_genero(catalogo, valor)
        elif opcion == 2:
            valor = input("Director a consultar: ")
            subconjunto = busqueda.buscar_por_director(catalogo, valor)
        elif opcion == 3:
            valor = input("Actor a consultar: ")
            subconjunto = busqueda.buscar_por_actor(catalogo, valor)
        elif opcion == 4:
            valor = input("Pais a consultar: ")
            subconjunto = busqueda.buscar_por_pais(catalogo, valor)
        elif opcion == 5:
            valor = input("Idioma a consultar: ")
            subconjunto = busqueda.buscar_por_idioma(catalogo, valor)
        elif opcion == 6:
            rango_anios = estadisticas.rango_de_anios(catalogo)
            if rango_anios is not None:
                print(f"Anios disponibles: {rango_anios[0]} - {rango_anios[1]}")
            anio = _pedir_entero("Anio a consultar: ")
            subconjunto = busqueda.busqueda_combinada(catalogo, {"anio_desde": anio, "anio_hasta": anio})
        elif opcion == 7:
            subconjunto = catalogo
        else:
            print("Opcion invalida.")
            continue

        _mostrar_resumen_de_campos(estadisticas.resumen_de_campos(catalogo, subconjunto))

        if opcion == 7:
            print("\nTop 5 generos (vote_average):")
            _mostrar_resultado(estadisticas.top5_generos(catalogo))
            print("\nTop 5 directores (vote_average):")
            _mostrar_resultado(estadisticas.top5_directores(catalogo))
            print("\nTop 5 actores (vote_average):")
            _mostrar_resultado(estadisticas.top5_actores(catalogo))
            print("\nTop 5 paises (vote_average):")
            _mostrar_resultado(estadisticas.top5_paises(catalogo))
            print("\nTop 5 idiomas (vote_average):")
            _mostrar_resultado(estadisticas.top5_idiomas(catalogo))
            print("\nTop 5 anios (vote_average):")
            _mostrar_resultado(estadisticas.top5_anios(catalogo))


# Campos de un perfil de usuario que se pueden editar con la opcion "Editar
# perfil guardado" ("id" queda afuera: lo asigna agregar_perfil, no se edita).
_CAMPOS_PERFIL_EDITABLES = {"nombre", "generos", "directores", "actores", "idiomas"}


# Parametros:
#   catalogo (list[dict]): catalogo de peliculas ya cargado en memoria.
# Retorna:
#   None. Los perfiles de usuario se cargan de RUTA_PERFILES al entrar al
#       submenu y se persisten de inmediato con recomendaciones.guardar_perfiles
#       cada vez que se crean/editan/eliminan (igual que menu_crud con el
#       catalogo). El "perfil activo" (con el que se piden recomendaciones)
#       vive solo en memoria durante el submenu: se elige con "Crear perfil
#       de usuario" o "Usar un perfil guardado".
def menu_recomendaciones(catalogo: list[dict]) -> None:
    perfiles = recomendaciones.cargar_perfiles(RUTA_PERFILES)
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
            perfiles = recomendaciones.agregar_perfil(
                perfiles, nombre, generos_preferidos, directores_preferidos, actores_preferidos, idiomas_preferidos
            )
            recomendaciones.guardar_perfiles(perfiles, RUTA_PERFILES)
            perfil_usuario = perfiles[-1]
            print(f"Perfil creado y guardado con id {perfil_usuario['id']}.")
            continue

        if opcion == 2:
            _mostrar_perfiles(perfiles)
            continue

        if opcion == 3:
            id_usuario = _pedir_entero("Id del perfil a usar: ")
            encontrado = recomendaciones.obtener_perfil_por_id(perfiles, id_usuario)
            if encontrado is None:
                print(f"No existe ningun perfil con el id {id_usuario}.")
            else:
                perfil_usuario = encontrado
                print(f"Perfil activo: {perfil_usuario['nombre']} (id {perfil_usuario['id']}).")
            continue

        if opcion in (4, 5):
            try:
                if opcion == 4:
                    id_usuario = _pedir_entero("Id del perfil a editar: ")
                    campo = input("Campo a modificar (nombre, generos, directores, actores, idiomas): ")
                    if campo not in _CAMPOS_PERFIL_EDITABLES:
                        print(f"'{campo}' no es un campo editable de un perfil.")
                        continue
                    nuevo_valor = input("Nuevo nombre: ") if campo == "nombre" else _pedir_lista(f"Nuevos {campo} (separados por coma): ")
                    perfiles = recomendaciones.actualizar_perfil(perfiles, id_usuario, {campo: nuevo_valor})
                    print("Perfil actualizado.")
                else:
                    id_usuario = _pedir_entero("Id del perfil a eliminar: ")
                    perfiles = recomendaciones.eliminar_perfil(perfiles, id_usuario)
                    if perfil_usuario is not None and perfil_usuario.get("id") == id_usuario:
                        perfil_usuario = None
                    print("Perfil eliminado.")
            except ValueError as error:
                print(f"No se pudo completar la operacion: {error}")
                continue
            recomendaciones.guardar_perfiles(perfiles, RUTA_PERFILES)
            continue

        if perfil_usuario is None:
            print("Primero hay que crear o usar un perfil de usuario (opciones 1 o 3).")
            continue

        if opcion == 6:
            resultado = recomendaciones.filtrar_peliculas_por_gustos(catalogo, perfil_usuario)
        elif opcion == 7:
            campo = input("Campo de puntuacion (vote_average, popularity): ")
            cantidad = _pedir_entero("Cantidad de recomendaciones: ")
            resultado = recomendaciones.recomendar_por_ranking(catalogo, perfil_usuario, campo, cantidad)
        elif opcion == 8:
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
#   1. Fuerza la salida estandar a UTF-8: el catalogo tiene texto en idiomas
#      con alfabetos que la consola de Windows (cp1252 por defecto) no puede
#      imprimir (ej. cirilico, bengali), y sin esto la aplicacion se cae con
#      UnicodeEncodeError apenas aparece uno.
#   2. Carga el catalogo una vez con crud.cargar_catalogo(RUTA_DATOS).
#   3. Muestra el menu principal en un bucle y deriva cada opcion al submenu
#      del modulo correspondiente (busqueda, crud, rankings, estadisticas,
#      recomendaciones).
#   4. Al salir (opcion 0), persiste el catalogo con crud.guardar_catalogo.
def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    catalogo = crud.cargar_catalogo(RUTA_DATOS) or []

    while True:
        print("\n=== Catalogo de Peliculas ===")
        mostrar_menu(MENU_PRINCIPAL)
        opcion = _pedir_entero("Opcion: ")

        if opcion == 0:
            # MODIFICACION: Se quito 'crud.guardar_catalogo(catalogo, RUTA_DATOS)' de aqui
            # porque los datos se guardan en tiempo real tras cada operacion en crud.py.
            # Los demas modulos solo leen, no modifican el catalogo, asi que no necesitan persistir nada.
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
