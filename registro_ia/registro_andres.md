# Registro de uso de IA — Andres

Integrante identificado por `git config user.name/email` (Andres Allievi,
garzamorada@gmail.com) y por el reparto de tareas del README (`estadisticas.py`
y `main.py`). Las entradas de sesiones anteriores a 2026-09-24 no estan
reconstruidas aca porque no hay forma de confirmar con certeza que integrante
las escribio (la misma sesion pudo haber sido usada por otro companero); se
completan desde la fecha en que se pidio explicitamente llevar este registro.

---

### Entrada 1 — 2026-09-24

**Prompt del usuario:**
> arma el menu en funcion a la funciones de cada archivo y sus parametros de
> entrada

**Respuesta / propuesta de la IA:**
Se reconstruyo `main.py`, que ya tenia una version con logica real pero con
bugs (un `break` cortaba el bucle apenas se elegia la primera opcion, los
numeros de opcion no coincidian con `MENU_OPCIONES`, y algunas llamadas no
pasaban todos los parametros reales de la funcion, ej. `rankings.top_peliculas`
sin `campo_puntuacion` ni `cantidad`). La nueva version arma un menu principal
con un submenu por modulo (`menu_busqueda`, `menu_crud`, `menu_rankings`,
`menu_estadisticas`, `menu_recomendaciones`), donde cada opcion pide por
consola exactamente los parametros que espera la funcion correspondiente de
`busqueda.py`, `crud.py`, `rankings.py`, `estadisticas.py` y
`recomendaciones.py`. Se agregaron helpers `_pedir_entero` (con reintento ante
`ValueError`), `_pedir_lista` y `_mostrar_resultado` para no repetir el
parseo/impresion en cada rama.

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:** Se corrio `python -m py_compile` sobre los
6 archivos `.py` (sin errores de sintaxis) y se importo el modulo `main` con
Python para confirmar que los imports y la definicion de funciones no rompen.
No se probo la ejecucion interactiva completa porque los modulos que `main.py`
llama (`crud`, `busqueda`, `rankings`, `estadisticas`, `recomendaciones`)
todavia son stubs (`pass # TODO: implementar`) sin logica real.

---

### Entrada 2 — 2026-09-24

**Prompt del usuario:**
> ahora vamos a desarrollar las estadisticas, dame un plan de accion y vemos
> que falta

**Respuesta / propuesta de la IA:**
Se propuso un plan de 6 pasos para implementar `estadisticas.py`:
1. Helper interno `_valor_numerico(pelicula, campo)` para convertir a float
   campos que en el JSON vienen como string (`budget`, `popularity`), a
   diferencia de otros que ya son numericos (`vote_average`, `vote_count`,
   `runtime`, `revenue`).
2. Helper interno `_promedio_por_categoria(catalogo, campo_lista,
   campo_numerico)` compartido por las 5 funciones de promedio por categoria
   (genero, director, actor, pais, idioma), que son estructuralmente
   identicas salvo el campo lista que recorren.
3. `promedio_general` usando el helper (1).
4. `peliculas_por_anio` parseando el año de `release_date`.
5. `resumen_estadistico` componiendo varios `promedio_general`.
6. Plan de pruebas: armar a mano una lista chica de peliculas de prueba
   (sin depender de `crud.py`, que todavia no esta implementado) y verificar
   los promedios contra el calculo esperado, y despues correr contra
   `data/movies_unified.json` completo para confirmar que no rompe con los
   45.433 registros reales.

Quedaron dos preguntas abiertas para el usuario: precision de redondeo de los
promedios, y si esta de acuerdo con compartir el helper `_promedio_por_categoria`
entre las 5 funciones en vez de duplicar la logica.

**Decision del usuario:** Pendiente — el usuario todavia no respondio las
preguntas abiertas ni confirmo el plan; en su lugar pidio primero dejar
registrado este intercambio (ver Entrada 3).

**Como se comprobo que funciona:** No aplica todavia, no se escribio codigo
(la IA se limito a proponer un plan, sin implementar).

---

### Entrada 3 — 2026-09-24

**Prompt del usuario:**
> no te olvides de dejar registro de estos promts y las correcciones desde
> las de hoy al menos

**Respuesta / propuesta de la IA:**
Se creo la carpeta `registro_ia/` y este archivo (`registro_andres.md`), con
las entradas correspondientes a los intercambios de hoy (2026-09-24) usando
la plantilla exacta de `GUIA_TP.md`. Se explicito que las sesiones de dias
anteriores no se reconstruyen por no poder confirmar con certeza el
integrante activo en cada una.

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:** Se releyo el archivo generado contra la
plantilla y la lista de requisitos de la seccion 6 de `GUIA_TP.md` (identificar
integrante, registrar cada intercambio relevante, no sobrescribir, no inventar
decisiones del usuario).

---

### Entrada 4 — 2026-09-24

**Prompt del usuario:**
> perfecto con 2 decimales

**Respuesta / propuesta de la IA:**
Confirmada la precision de redondeo (2 decimales) que quedaba pendiente de la
Entrada 2, se implemento `estadisticas.py` completo:
- `_valor_numerico(pelicula, campo)`: convierte a float campos que en el JSON
  vienen como string (`budget`, `popularity`), devolviendo `None` ante datos
  faltantes o no convertibles.
- `_promedio_por_categoria(catalogo, campo_lista, campo_numerico)`: helper
  compartido por las 5 funciones de promedio por categoria (evita repetir la
  misma logica de agrupacion 5 veces).
- `promedio_general`, `promedio_por_genero`, `promedio_por_director`,
  `promedio_por_actor`, `promedio_por_pais`, `promedio_por_idioma`,
  `peliculas_por_anio` y `resumen_estadistico`, todos redondeando promedios a
  2 decimales.

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:**
1. Se armo un catalogo de prueba a mano (4 peliculas con valores conocidos,
   incluyendo casos borde: un `budget` en `None`, un `popularity` invalido
   ("abc"), una pelicula sin genero/actor/director/pais/idioma, y una fecha
   `None`) y se corrieron 14 verificaciones comparando el resultado de cada
   funcion contra el calculo esperado a mano. Las 14 pasaron.
2. Se ejecutaron las mismas funciones contra `data/movies_unified.json`
   completo (45.433 peliculas reales) para confirmar que no rompen con los
   tipos mixtos del dataset original. Resultados verificados como razonables:
   promedio de `vote_average` 5.62/10, `runtime` promedio ~94 minutos, 20
   generos distintos (coincide con la taxonomia de TMDB), 135 anios distintos,
   19.739 directores distintos, tiempo de ejecucion total 0.28 segundos.

---

### Entrada 5 — 2026-09-24

**Prompt del usuario:**
> revisa el menu para ver si hay que cambiar algo

**Respuesta / propuesta de la IA:**
Se reviso `main.py` ahora que `estadisticas.py` esta implementado (y que
`crud.py`/`busqueda.py` ya fueron implementados por companeros en ramas
`feature/implementacion-crud` y `feature/busqueda-peliculas`, todavia sin
mergear a `develop`). Se encontraron y corrigieron dos problemas:
1. `_mostrar_resultado` imprimia diccionarios completos sin limite: contra el
   dataset real, `promedio_por_director` devuelve 19.739 entradas (y
   `promedio_por_actor` seguramente mas), lo que hubiera inundado la consola.
   Se agrego `_LIMITE_RESULTADOS_MOSTRADOS = 20` con aviso "... y N mas.", y
   un helper `_ordenar_por_valor_desc` para que las opciones de promedio por
   categoria (2 a 6 del submenu de estadisticas) muestren primero los valores
   mas altos en vez de un subconjunto arbitrario (orden de insercion). La
   opcion 7 (peliculas por anio) se ordena por anio ascendente.
2. La opcion 8 del submenu de busqueda ("Busqueda combinada") solo pedia
   genero/actor/director, pero la implementacion real de
   `busqueda_combinada` (rama de Elian) soporta ademas titulo, pais, idioma,
   palabra clave y rango de anios (`anio_desde`/`anio_hasta`). Se amplio el
   menu para pedir los 9 filtros.

No se modificaron `crud.py` ni `busqueda.py` (son de otros integrantes); solo
se ajusto `main.py`, que es el archivo de este integrante.

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:**
1. Se corrio `py_compile` sobre `main.py` (sin errores de sintaxis).
2. Se probo `_mostrar_resultado`/`_ordenar_por_valor_desc` contra
   `estadisticas.promedio_por_director` y `peliculas_por_anio` sobre el
   dataset real: el resultado quedo truncado a 20 filas con el aviso "... y
   19719 mas.", ordenado de mayor a menor promedio; los anios quedaron
   ordenados cronologicamente.
3. Como `busqueda.py` local todavia es un stub, se exporto temporalmente el
   contenido de `busqueda.py` de la rama `feature/busqueda-peliculas` (con
   `git show`) a un archivo aparte en el scratchpad (sin tocar el working
   tree del repo) y se probo que el dict de filtros que arma `main.py`
   (`titulo`, `genero`, `actor`, `director`, `pais`, `idioma`,
   `palabra_clave`, `anio_desde`, `anio_hasta`) produce los resultados
   esperados contra esa implementacion real. El archivo temporal se borro
   despues de la prueba.

**Nota de proceso:** siguiendo el guardrail de `CLAUDE.md` (no commitear
directo a `develop`), antes de este cambio se creo la rama
`feature/estadisticas-y-menu` a partir de `develop` (que ya tenia cambios sin
commitear de las Entradas 1 a 4). Los cambios de esta sesion quedaron en esa
rama, sin commitear ni pushear todavia.

---

### Entrada 6 — 2026-09-24

**Prompt del usuario:**
> ahora usando las estadisticas y mas preferencias vamaos a avanzar con las
> recomendaciones. arma una propuesta y vemos si hay que corregir algo

**Respuesta / propuesta de la IA:**
Se propuso un diseño para `recomendaciones.py` y se dejaron dos decisiones de
diseño abiertas al usuario (via preguntas de opcion multiple):
1. Que preferencias nuevas sumar al perfil ademas de genero/director/actor
   (opciones: idioma, pais, palabra clave, rango de anios).
2. Como usar `estadisticas.py` en `recomendar_por_ranking` (simple con
   afinidad como desempate / compuesto combinando puntaje + afinidad +
   promedio historico / informativo aparte sin afectar el orden).

El usuario eligio: sumar solo **idioma** como preferencia nueva (no pais, no
palabra clave, no rango de anios), y el criterio **compuesto**.

Con esa decision se implemento `recomendaciones.py` completo:
- `crear_perfil_usuario` ahora tambien recibe `idiomas_preferidos`.
- `CAMPOS_PREFERENCIA`: tabla que mapea cada preferencia (generos/directores/
  actores/idiomas) con el campo de la pelicula, la funcion de `busqueda.py`
  para filtrar y la funcion de `estadisticas.py` para el promedio historico;
  evita repetir la misma logica 4 veces en las 3 funciones que la usan.
- `filtrar_peliculas_por_gustos`: delega en `busqueda.py` (union de
  resultados por cada preferencia, sin duplicados) en vez de reimplementar
  el matching de texto.
- `calcular_afinidad`: cuenta coincidencias en las 4 categorias.
- `recomendar_por_ranking`: puntaje compuesto = (puntaje propio de la
  pelicula + promedio historico de sus categorias preferidas coincidentes) /
  2, mas `PESO_AFINIDAD` (0.5) por cada coincidencia. Los 4 promedios por
  categoria se calculan una sola vez por catalogo (no por pelicula) para que
  no sea demasiado lento con miles de peliculas.
- `recomendar_al_azar`: `random.sample` sobre las coincidencias.

Tambien se actualizo `main.py` (opcion 1 del submenu de recomendaciones) para
pedir el idioma preferido y pasar los 5 parametros en el orden correcto.

No se modifico `busqueda.py` ni `estadisticas.py` en su logica interna, solo
se importan y usan desde `recomendaciones.py`.

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:**
1. Como `busqueda.py` local sigue siendo un stub, se armo una carpeta
   aislada en el scratchpad con copias de `recomendaciones.py` y
   `estadisticas.py` del repo mas el `busqueda.py` real exportado de la rama
   `feature/busqueda-peliculas` (via `git show`), sin tocar el working tree
   del repo.
2. Se corrieron 11 pruebas con un catalogo de 4 peliculas de prueba
   (`crear_perfil_usuario`, `filtrar_peliculas_por_gustos`,
   `calcular_afinidad`, `recomendar_por_ranking`, `recomendar_al_azar`, y
   casos borde con perfil sin gustos). Las 11 pasaron.
3. Se corrio contra `data/movies_unified.json` completo (45.433 peliculas):
   con un perfil de generos `["Animation", "Comedy"]`, director `"John
   Lasseter"`, actor `"Tom Hanks"` e idioma `"English"`, las primeras
   recomendadas fueron "Toy Story" y "Toy Story 2" (afinidad 5, coinciden en
   las 4 categorias), por encima de peliculas con `vote_average` 10.0 pero
   afinidad mas baja — el orden compuesto se comporta como se esperaba. Un
   perfil con un genero inventado devolvio `[]` sin romper. Tiempos: ~1.3s
   filtrar, ~2s ordenar por ranking, sobre el dataset completo. Se borraron
   los archivos temporales de prueba al terminar.

---

### Entrada 7 — 2026-09-25

**Prompt del usuario:**
> arma test unitarios y funcionales para todas los archivos y ejecuta las de
> lo que esta terminado

**Respuesta / propuesta de la IA:**
Se instalo `pytest` y se armo una suite completa en `tests/` (mas
`pytest.ini` con `pythonpath = .` para que los tests puedan importar los
modulos del repo) y `tests/conftest.py` con un catalogo de prueba compartido
(5 peliculas, con casos borde de datos faltantes). Un archivo de test por
modulo:
- `test_estadisticas.py` y `test_recomendaciones.py`: tests unitarios reales
  (corren siempre) mas una clase de tests funcionales contra
  `data/movies_unified.json` completo.
- `test_main.py`: tests de los helpers propios de `main.py` que no dependen
  de otros modulos (`_pedir_entero`, `_pedir_lista`, `_mostrar_resultado`,
  `_ordenar_por_valor_desc`, `mostrar_menu`), tests de estructura de los
  `MENU_*` (deben tener opcion 0 y numeracion consecutiva sin huecos), y un
  test funcional que simula al usuario navegando `menu_estadisticas`.
- `test_crud.py` y `test_busqueda.py`: tests reales basados en el codigo de
  las ramas `feature/implementacion-crud` y `feature/busqueda-peliculas`
  (todavia sin mergear a `develop`). Cada archivo detecta en tiempo de
  ejecucion si el modulo local sigue siendo el stub original (llamando a una
  funcion con datos triviales y viendo si devuelve `None`) y si es asi se
  saltean automaticamente (`pytest.mark.skipif`), sin marcar el test como
  fallido.
- `test_rankings.py`: mismo patron de auto-skip, pero como nadie del equipo
  implemento `rankings.py` todavia, los tests se basan solo en el contrato
  documentado en los comentarios del stub (no en una implementacion real).

**Decision del usuario:** Aceptado

**Como se comprobo que funciona:**
1. `pytest` sobre todo el repo: **58 passed, 48 skipped** (los que corren son
   `estadisticas.py`, `recomendaciones.py` y `main.py`, que son los modulos
   terminados en esta rama; los de `crud.py`, `busqueda.py` y `rankings.py`
   se saltean solos porque siguen siendo stubs localmente).
2. Se corrigio un warning de deprecacion de pytest (fixture de scope "class"
   definida como metodo de instancia) en los dos archivos que lo tenian.
3. Para no dejar los 48 tests salteados "a ciegas", se los valido
   temporalmente: se pisaron `crud.py` y `busqueda.py` con el contenido real
   de las ramas de Dario y Elian (`git show origin/<rama>:archivo.py >
   archivo.py`) y se corrio la suite: **50/50 pasaron**, incluido el test
   funcional de recomendaciones que ahora usa busqueda real + dataset
   completo. Para `rankings.py`, al no existir una implementacion real
   todavia, se escribio una implementacion de referencia minima solo para
   validar el archivo de test (no la logica "correcta", solo que el test no
   tenga bugs propios): **11/11 pasaron**. En los tres casos se restauro el
   stub original con `git checkout -- archivo.py` inmediatamente despues
   (`git status` confirmo que quedaron sin cambios).
4. Se agrego una seccion "Tests" al `README.md` explicando como correrlos y
   el comportamiento de auto-skip, y se actualizo el TODO.
