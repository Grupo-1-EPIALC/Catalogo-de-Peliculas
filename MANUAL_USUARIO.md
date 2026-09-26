# Manual de usuario — Catálogo de Películas

Guía para usar la aplicación de consola del catálogo de películas. Para
instrucciones de instalación del entorno de desarrollo, dataset y tests, ver
[`README.md`](README.md). Este manual asume que ya tenés todo eso funcionando
y explica **cómo usar la aplicación una vez que arranca**.

## 1. Qué hace esta aplicación

Es un catálogo de ~45.000 películas (dataset de Kaggle, ver README) que
permite:

- **Buscar** películas por título, actor, director, género, país, idioma o
  palabra clave.
- **Administrar** el catálogo: ver, agregar, editar y eliminar películas.
- **Ver rankings** de las mejores películas por distintos criterios.
- **Consultar estadísticas**: promedios y totales por categoría.
- **Recibir recomendaciones** personalizadas según tus gustos.

Todo se maneja a través de un menú por consola con opciones numeradas.

## 2. Cómo iniciar la aplicación

Con el entorno virtual activado (ver README) y parado en la carpeta del
proyecto:

```bash
python main.py
```

Si nunca corriste el notebook `eda dataset.ipynb`, hacelo antes: la
aplicación necesita el archivo `data/movies_unified.json` para tener datos
con los cuales trabajar. Sin ese archivo, la aplicación igual arranca, pero
el catálogo queda vacío.

Al arrancar vas a ver el menú principal:

```
=== Catalogo de Peliculas ===
1. Busqueda
2. CRUD de peliculas
3. Rankings
4. Estadisticas
5. Recomendaciones
0. Salir
Opcion:
```

Escribí el número de la opción que querés y presioná Enter. Si escribís algo
que no es un número, la aplicación te lo va a pedir de nuevo sin romperse.

Para volver de cualquier submenú al menú principal, elegí siempre la opción
**0**. Para cerrar la aplicación del todo, elegí **0** en el menú principal
(esto guarda cualquier cambio pendiente en el catálogo antes de cerrar).

## 3. Búsqueda (opción 1)

Busca películas que ya existen en el catálogo. Nunca modifica nada.

```
--- Busqueda ---
1. Buscar por titulo
2. Buscar por actor
3. Buscar por director
4. Buscar por genero
5. Buscar por pais
6. Buscar por idioma
7. Buscar por palabra clave
8. Busqueda combinada (varios filtros)
0. Volver al menu principal
```

Las búsquedas **no distinguen mayúsculas de minúsculas ni tildes**, y
encuentran coincidencias parciales. Por ejemplo, buscar por actor "hanks"
encuentra a "Tom Hanks".

**Buscar por género acepta castellano o inglés.** El dataset tiene los
géneros en inglés ("Comedy", "Horror", etc.), pero si escribís el nombre en
castellano ("comedia", "terror") y no hay coincidencia directa, la
aplicación prueba automáticamente la traducción antes de decir que no
encontró nada (ver `categorias_traducciones.json`). Esto aplica a la opción
4 (Buscar por género) y al filtro "genero" de la búsqueda combinada (opción
8); también a las opciones de género en Rankings y a los géneros preferidos
en Recomendaciones.

Ejemplo — buscar por actor (a partir de la opción 2 en adelante, salvo
título, se muestra un listado compacto con el `id` de cada película, útil
para después verla en detalle con CRUD → opción 1):

```
Opcion: 2
Nombre del actor: tom hanks
- Apollo 13 (1995) [id: 568]
- Forrest Gump (1994) [id: 13]
- Philadelphia (1993) [id: 9800]
... y 51 peliculas mas.
```

Si hay más de 20 resultados, se muestran los primeros 20 y un aviso de
cuántos quedaron afuera (para no inundar la pantalla). La búsqueda por
título (opción 1) es la excepción: muestra la ficha completa de cada
resultado directamente, porque suele haber pocas coincidencias.

La opción 8 (**búsqueda combinada**) te deja combinar varios filtros a la
vez (todos deben cumplirse, no alcanza con uno solo). Dejá vacío cualquier
filtro que no quieras usar, simplemente presionando Enter sin escribir nada:

```
Opcion: 8
Titulo (vacio para omitir):
Genero (vacio para omitir): Comedy
Actor (vacio para omitir): Tom Hanks
Director (vacio para omitir):
Pais (vacio para omitir):
Idioma (vacio para omitir):
Palabra clave (vacio para omitir):
Anio desde (vacio para omitir): 1990
Anio hasta (vacio para omitir): 2000
```

Esto busca comedias con Tom Hanks estrenadas entre 1990 y 2000.

## 4. CRUD de películas (opción 2)

Permite ver, crear, editar y eliminar películas del catálogo. **A
diferencia de Búsqueda, estas operaciones modifican el catálogo** y se
guardan automáticamente en `data/movies_unified.json` después de cada
cambio exitoso.

```
--- CRUD de peliculas ---
1. Ver pelicula por id
2. Agregar pelicula
3. Editar un campo de una pelicula
4. Eliminar pelicula
5. Agregar valor a una lista (genero, actor, etc.)
6. Quitar valor de una lista (genero, actor, etc.)
0. Volver al menu principal
```

### Ver película por id (opción 1)

Te pide el `id` numérico de la película y muestra todos sus datos (título,
sinopsis, género, reparto, etc.). Si no existe una película con ese id, se
muestra `(sin resultado)`.

### Agregar película (opción 2)

Pide un `id` (numérico, tiene que ser único) y un título. La película se
agrega con esos dos datos únicamente; los demás campos (sinopsis, género,
reparto, etc.) quedan vacíos y se pueden completar después con las opciones
3, 5 y 6.

Si el `id` ya existe, la aplicación **no rompe**: muestra un mensaje de
error y vuelve al menú sin modificar nada.

```
Opcion: 2
Id de la nueva pelicula: 862
Titulo: Toy Story
No se pudo completar la operacion: Ya existe una película en el catálogo con el id 862.
```

### Editar un campo de una película (opción 3)

Pide el `id`, el nombre del campo a modificar (por ejemplo `title`,
`vote_average`, `tagline`, `runtime`) y el nuevo valor. Solo modifica ese
campo puntual, el resto de la película queda igual. Si el `id` no existe,
muestra un error y no cambia nada.

> Nota: el valor se guarda siempre como texto. Para campos numéricos
> (`vote_average`, `runtime`, etc.) esto no afecta a las estadísticas ni
> rankings, que convierten el valor automáticamente.

### Eliminar película (opción 4)

Pide el `id` y la elimina del catálogo. Si no existe, muestra un error y no
cambia nada.

### Agregar / quitar valor de una lista (opciones 5 y 6)

Algunos campos de una película son listas (géneros, reparto, directores,
keywords, compañías/países productores, idiomas hablados). Estas opciones
agregan o quitan un valor puntual de una de esas listas, pidiendo el `id`
de la película, el nombre del campo, y el valor.

Campos de lista válidos: `genres`, `cast`, `directors`, `keywords`,
`production_companies`, `production_countries`, `spoken_languages`.

```
Opcion: 5
Id de la pelicula: 862
Campo tipo lista (genres, cast, directors, keywords, production_companies, production_countries, spoken_languages): genres
Valor a agregar: Adventure
```

Si el campo no es válido, si la película no existe, o si al quitar un valor
este no estaba presente en la lista, se muestra un mensaje de error y no se
modifica nada.

## 5. Rankings (opción 3)

Muestra las mejores películas (o categorías) según distintos criterios de
puntuación. No modifica nada.

```
--- Rankings ---
1. Top peliculas (general)
2. Top peliculas por genero
3. Top peliculas por actor
4. Top peliculas por director
5. Ranking de generos por promedio
6. Ranking de actores por promedio
7. Ranking de directores por promedio
0. Volver al menu principal
```

Los campos de puntuación válidos para estas opciones son `vote_average`
(puntaje 0 a 10), `popularity` (índice de popularidad) y `vote_count`
(cantidad de votos).

Las opciones **1 a 4** ("Top películas...") devuelven películas individuales
ordenadas de mayor a menor puntaje. La opción 2 (por género) acepta el
género en castellano o inglés, igual que en Búsqueda.

```
Opcion: 1
Campo de puntuacion (vote_average, popularity, vote_count): vote_average
Cantidad de peliculas: 3
- Reckless
- Girl in the Cadillac
- The Haunted World of Edward D. Wood, Jr.
```

Las opciones **5 a 7** ("Ranking de...") no devuelven películas sino un
promedio por categoría (género, actor o director), ordenado de mayor a
menor. Para actor y director hay que indicar un **mínimo de películas**: una
persona con menos películas que ese mínimo no entra en el ranking, para que
un actor con una sola película puntuada 10 no aparezca primero.

```
Opcion: 5
Campo de puntuacion: vote_average
- ('Animation', 6.28)
- ('History', 6.15)
- ('War', 6.04)
- ('Drama', 5.91)
- ('Music', 5.88)
...
```

> El formato de esta lista (`- (genero, promedio)`) es el que muestra la
> aplicación tal cual hoy; es un poco crudo (tupla de Python sin formatear)
> pero es fiel a lo que vas a ver en pantalla.

## 6. Estadísticas (opción 4)

Calcula indicadores sobre un grupo de películas: elegís una categoría
(género, director, actor, país, idioma o año) y un valor dentro de ella, o
"General" para el catálogo completo. No modifica nada.

```
--- Estadisticas ---
1. Genero
2. Director
3. Actor
4. Pais
5. Idioma
6. Anio
7. General (todo el catalogo)
0. Volver al menu principal
```

Las opciones 1 a 5 (género, director, actor, país, idioma) piden el valor a
consultar; la búsqueda funciona igual que en Búsqueda (sin distinguir
mayúsculas/tildes, y género acepta castellano o inglés). La opción 6 (año)
pide un número. Ninguna de las opciones 1 a 6 acepta dejar el valor vacío
sin sentido: si no hay películas que coincidan, vas a ver "Cantidad de
peliculas: 0" y el resto de los indicadores en 0.0.

Para cualquiera de las 7 opciones vas a ver:
- **Cantidad de películas** en ese grupo.
- **Media y mediana** de cada campo numérico (`vote_average`, `vote_count`,
  `runtime`, `revenue`, `budget`, `popularity`), en sus unidades originales.
  Un valor en 0 en estos campos se descarta antes de calcular (no cuenta ni
  para la media ni para la mediana ni para el promedio normalizado): en este
  dataset un 0 en, por ejemplo, `revenue` o `budget` casi siempre significa
  "dato no disponible", no que la película haya costado o recaudado
  literalmente cero.
- **Promedio normalizado combinado**: cada valor individual (ya sin los
  ceros) de `vote_average`, `vote_count`, `revenue`, `budget` y `popularity`
  se reescala primero a una escala común de 1 a 10 (según el mínimo/máximo de
  cada campo en **todo el catálogo**, no solo en el grupo filtrado, para que
  el número de género "Comedy" se pueda comparar con el de "Horror"), se
  promedian los valores ya normalizados de cada campo, y esos 5 promedios se
  promedian entre sí. `runtime` no entra en esta cuenta: es una duración, no
  un score, y promediarla junto al resto no tendría sentido (una película más
  larga no es "mejor") — pero su media/mediana se sigue mostrando arriba.

Ejemplo — género "Comedy":

```
Opcion: 1
Genero a consultar: Comedy
Cantidad de peliculas: 13176
vote_average -> media: 5.98 | mediana: 6.0
vote_count -> media: 113.89 | mediana: 14.0
runtime -> media: 94.43 | mediana: 95.0
revenue -> media: 64054854.8 | mediana: 19322135.0
budget -> media: 21569629.55 | mediana: 10000000.0
popularity -> media: 3.23 | mediana: 1.42
Promedio normalizado combinado (escala 1-10): 2.21
```

> El promedio normalizado combinado suele salir bajo (cerca de 1-2) para la
> mayoría de los grupos incluso despues de excluir los ceros: campos como
> `revenue`, `budget`, `vote_count` y `popularity` tienen distribuciones muy
> desparejas (unas pocas películas con números gigantes empujan el máximo del
> catálogo), asi que la mayoría de los grupos quedan cerca del piso de esa
> escala. Es el comportamiento esperado del cálculo, no un error.

La opción **7 (General)** muestra lo mismo sobre el catálogo completo, y
además el top 5 de cada categoría según `vote_average` promedio:

```
Opcion: 7
Cantidad de peliculas: 45433
vote_average -> media: 6.01 | mediana: 6.1
...
Promedio normalizado combinado (escala 1-10): 2.21

Top 5 generos (vote_average):
- ('Documentary', 6.67)
- ('Animation', 6.45)
...

Top 5 anios (vote_average):
- (1902, 6.9)
...
```

> Igual que en Rankings, el formato de estas listas (`- (categoria,
> promedio)`) es la tupla de Python sin formatear; es fiel a lo que vas a
> ver en pantalla.

## 7. Recomendaciones (opción 5)

Arma un perfil de gustos y recomienda películas en base a él. Los perfiles
de usuario se guardan en `data/perfiles_usuario.json` (un archivo aparte del
catálogo de películas) y persisten entre sesiones.

```
--- Recomendaciones ---
1. Crear perfil de usuario
2. Ver perfiles guardados
3. Usar un perfil guardado
4. Editar perfil guardado
5. Eliminar perfil guardado
6. Ver peliculas afines al perfil activo (sin ordenar)
7. Recomendacion por ranking
8. Recomendacion al azar
0. Volver al menu principal
```

**Primero hay que crear un perfil (opción 1) o elegir uno ya guardado
(opción 3)**; las opciones 6 a 8 no van a funcionar hasta que haya un
"perfil activo" (la aplicación te lo va a recordar si intentás saltearlo).
El perfil activo (con el que se piden recomendaciones) dura solo mientras
estás en este submenú; si volvés al menú principal y volvés a entrar, hay
que crearlo o elegirlo de nuevo con la opción 3 — pero los perfiles en sí
ya están guardados, no hace falta volver a tipear las preferencias.

```
Opcion: 1
Nombre del usuario: Andres
Generos preferidos (separados por coma): Animation, Comedy
Directores preferidos (separados por coma): John Lasseter
Actores preferidos (separados por coma): Tom Hanks
Idiomas preferidos (separados por coma): English
Perfil creado y guardado con id 1.
```

Podés dejar cualquiera de las listas vacía (presionando Enter sin escribir
nada) si no tenés preferencia en esa categoría.

Cada perfil recibe un **id numérico** además del nombre (se asigna solo, no
se pide): como dos usuarios pueden llamarse igual, el id es lo que identifica
sin ambigüedad a cuál perfil te referís en las opciones 3, 4 y 5.

- **Opción 2** lista todos los perfiles guardados (id, nombre y
  preferencias).
- **Opción 3** pide un id y lo marca como perfil activo.
- **Opción 4** pide un id, el campo a modificar (`nombre`, `generos`,
  `directores`, `actores` o `idiomas`) y el nuevo valor, y guarda el cambio.
- **Opción 5** pide un id y elimina ese perfil (si era el perfil activo,
  dejás de tener uno activo).
- **Opción 6** muestra todas las películas que coinciden con al menos una
  preferencia del perfil activo, sin ningún orden particular.
- **Opción 7** ("por ranking") pide un campo de puntuación (`vote_average`
  o `popularity`) y una cantidad, y devuelve las películas más afines al
  perfil activo ordenadas por un puntaje que combina el puntaje propio de la
  película, el promedio histórico de tus categorías preferidas, y cuántas
  preferencias coinciden.
- **Opción 8** ("al azar") devuelve una selección aleatoria entre las
  películas afines al perfil activo.

Las preferencias **no distinguen mayúsculas de minúsculas ni tildes**
(escribir "tom hanks" funciona igual que "Tom Hanks").

## 8. Guardado de cambios

Los cambios hechos en el **CRUD de películas** (agregar/editar/eliminar
películas, o modificar listas) se guardan automáticamente en
`data/movies_unified.json` apenas se completan con éxito. Los cambios en
los **perfiles de usuario** (crear/editar/eliminar, en Recomendaciones) se
guardan igual de inmediato en `data/perfiles_usuario.json`. En ningún caso
hace falta una acción extra para persistirlos.

Al salir de la aplicación (opción 0 del menú principal) se guarda el
catálogo una vez más, por las dudas.

Búsqueda, Rankings, Estadísticas y Recomendaciones **nunca modifican el
catálogo**; solo lo consultan.

## 9. Problemas comunes

**"No se pudo completar la operacion: ..."** — Apareció al usar el CRUD.
Significa que la operación no se pudo hacer por un motivo esperable (id
duplicado al crear, id inexistente al editar/eliminar, nombre de campo de
lista inválido, o valor que no estaba en la lista al querer quitarlo). El
mensaje después de los dos puntos explica exactamente qué pasó. El catálogo
no se modificó; podés volver a intentar con otro id o valor.

**"(sin resultado)"** — La búsqueda, ranking o consulta no encontró nada
que coincida con lo que pediste.

**"Ingrese un numero entero valido."** — Se esperaba un número (por
ejemplo, un id o una cantidad) y se escribió otra cosa. Volvé a escribir
solo el número.

**El catálogo aparece vacío al arrancar** — Falta el archivo
`data/movies_unified.json`. Correlo generando con el notebook
`eda dataset.ipynb` (ver README, sección Dataset).
