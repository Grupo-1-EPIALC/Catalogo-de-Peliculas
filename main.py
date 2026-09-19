"""
main.py

Punto de entrada de la aplicacion. Integra los modulos crud.py, busqueda.py,
rankings.py, estadisticas.py y recomendaciones.py detras de un menu por
consola. Este archivo NO debe tener logica de negocio (eso vive en los otros
modulos); solo debe leer la opcion del usuario, llamar a la(s) funcion(es)
correspondiente(s) y mostrar el resultado.

Funciones que contiene:
- mostrar_menu
- main
"""

import crud
import busqueda
import rankings
import estadisticas
import recomendaciones


# Ruta del archivo con el catalogo unificado generado por `eda dataset.ipynb`.
RUTA_DATOS = "data/movies_unified.json"

# Opciones de menu -> que modulo.funcion se llama en cada una.
# 1. Buscar por titulo         -> busqueda.buscar_por_titulo(catalogo, texto)
# 2. Buscar por actor          -> busqueda.buscar_por_actor(catalogo, nombre_actor)
# 3. Buscar por director       -> busqueda.buscar_por_director(catalogo, nombre_director)
# 4. Buscar por genero         -> busqueda.buscar_por_genero(catalogo, genero)
# 5. Buscar por pais / idioma  -> busqueda.buscar_por_pais / buscar_por_idioma
# 6. Busqueda combinada        -> busqueda.busqueda_combinada(catalogo, filtros)
# 7. Ver pelicula por id       -> crud.obtener_pelicula_por_id(catalogo, id_pelicula)
# 8. Agregar pelicula          -> crud.crear_pelicula(...) y luego crud.guardar_catalogo(...)
# 9. Editar pelicula           -> crud.actualizar_pelicula(...) y luego crud.guardar_catalogo(...)
# 10. Eliminar pelicula        -> crud.eliminar_pelicula(...) y luego crud.guardar_catalogo(...)
# 11. Top peliculas / por genero, actor, director -> rankings.top_peliculas / top_por_*
# 12. Ranking de generos, actores o directores    -> rankings.ranking_generos / ranking_actores / ranking_directores
# 13. Ver estadisticas generales                  -> estadisticas.resumen_estadistico(catalogo)
# 14. Ver promedios por categoria                 -> estadisticas.promedio_por_genero / _director / _actor / _pais / _idioma
# 15. Crear perfil de usuario                     -> recomendaciones.crear_perfil_usuario(...)
# 16. Recomendacion por ranking                   -> recomendaciones.recomendar_por_ranking(catalogo, perfil, campo_puntuacion, cantidad)
# 17. Recomendacion al azar                       -> recomendaciones.recomendar_al_azar(catalogo, perfil, cantidad)
# 0. Salir                                        -> guardar cambios pendientes (crud.guardar_catalogo) y terminar el bucle
MENU_OPCIONES: dict[int, str] = {
    1: "Buscar por titulo",
    2: "Buscar por actor",
    3: "Buscar por director",
    4: "Buscar por genero",
    5: "Buscar por pais / idioma",
    6: "Busqueda combinada (varios filtros)",
    7: "Ver pelicula por id",
    8: "Agregar pelicula",
    9: "Editar pelicula",
    10: "Eliminar pelicula",
    11: "Top peliculas (general / por genero / actor / director)",
    12: "Ranking de generos, actores o directores",
    13: "Ver estadisticas generales",
    14: "Ver promedios por categoria",
    15: "Crear perfil de usuario",
    16: "Recomendacion por ranking",
    17: "Recomendacion al azar",
    0: "Salir",
}


# Parametros: ninguno.
# Retorna:
#   None. Imprime por consola las opciones definidas en MENU_OPCIONES.
def mostrar_menu() -> None:
    pass  # TODO: implementar


# Parametros: ninguno.
# Retorna:
#   None.
# Flujo esperado:
#   1. Cargar el catalogo una vez al inicio con crud.cargar_catalogo(RUTA_DATOS).
#   2. En un bucle (while), mostrar_menu() y leer la opcion elegida (int, con
#      manejo de errores si el usuario ingresa algo no numerico).
#   3. Segun la opcion, pedir los datos adicionales que haga falta (texto de
#      busqueda, id de pelicula, campos a editar, gustos del usuario, etc.) y
#      llamar a la funcion correspondiente del modulo indicado en el
#      comentario de MENU_OPCIONES / mas arriba en este archivo.
#   4. Mostrar el resultado devuelto por esa funcion (lista de peliculas,
#      diccionario de promedios, ranking, recomendaciones, etc.).
#   5. Las operaciones que modifican el catalogo (crear/editar/eliminar
#      pelicula) deben persistirse llamando a crud.guardar_catalogo(catalogo, RUTA_DATOS).
#   6. Terminar el bucle cuando el usuario elija la opcion 0 (Salir).
def main() -> None:
    pass  # TODO: implementar


if __name__ == "__main__":
    main()
