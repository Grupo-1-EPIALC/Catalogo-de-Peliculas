"""
env.py

Rutas de los archivos de datos usados en toda la aplicacion, centralizadas
en un solo lugar. Antes cada modulo tenia su propia constante (main.py y
crud.py llegaron a tener defaults distintos entre si, apuntando a archivos
diferentes sin que nada lo avisara); importar las rutas desde aca asegura
que crud.py, recomendaciones.py y main.py siempre esten de acuerdo.

Variables que contiene:
- RUTA_DATOS
- RUTA_PERFILES
"""

# Catalogo de peliculas. Se usa la muestra representativa (mas liviana que
# el dataset completo) como archivo por defecto de la aplicacion.
RUTA_DATOS = "data/movies_sample_representativa.json"

# Perfiles de usuario de recomendaciones.py (ver el docstring de ese modulo).
RUTA_PERFILES = "data/perfiles_usuario.json"
