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
encuentra a "Tom Hanks", y buscar género "comedia" no encontraría nada
porque el dataset usa los nombres en inglés ("Comedy").

Ejemplo — buscar por actor:

```
Opcion: 2
Nombre del actor: tom hanks
- Toy Story
- Apollo 13
- Forrest Gump
... y 51 peliculas mas.
```

Si hay más de 20 resultados, se muestran los primeros 20 y un aviso de
cuántos quedaron afuera (para no inundar la pantalla).

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

> **Estado actual: pendiente de implementación.** El submenú de Rankings
> existe y se puede navegar, pero por ahora todas sus opciones devuelven
> `(sin resultado)` porque la lógica en `rankings.py` todavía no está
> escrita. Cuando se implemente, esta sección del manual se va a actualizar.

Cuando esté implementado, vas a poder ver:

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

## 6. Estadísticas (opción 4)

Calcula promedios e indicadores sobre el catálogo completo. No modifica
nada.

```
--- Estadisticas ---
1. Promedio general de un campo
2. Promedio por genero
3. Promedio por director
4. Promedio por actor
5. Promedio por pais
6. Promedio por idioma
7. Cantidad de peliculas por anio
8. Resumen estadistico general
0. Volver al menu principal
```

Los campos numéricos válidos son `vote_average`, `vote_count`, `runtime`,
`revenue`, `budget` y `popularity`.

Las opciones de promedio por categoría (2 a 6) muestran los resultados
**ordenados de mayor a menor promedio**, cortados a los primeros 20 (con
aviso de cuántos quedaron afuera), ya que hay categorías con miles de
valores distintos (por ejemplo, hay más de 19.000 directores distintos en
el catálogo).

Ejemplo — resumen general:

```
Opcion: 8
total_peliculas: 45433
promedio_vote_average: 5.62
promedio_runtime: 94.12
promedio_popularity: 2.92
```

## 7. Recomendaciones (opción 5)

Arma un perfil de gustos y recomienda películas en base a él.

```
--- Recomendaciones ---
1. Crear perfil de usuario
2. Ver peliculas afines al perfil (sin ordenar)
3. Recomendacion por ranking
4. Recomendacion al azar
0. Volver al menu principal
```

**Primero hay que crear un perfil (opción 1)**; las demás opciones no van a
funcionar hasta que lo hagas (la aplicación te lo va a recordar si intentás
saltearlo). El perfil se guarda solo mientras dura la sesión en este
submenú: si volvés al menú principal y volvés a entrar a Recomendaciones,
hay que crearlo de nuevo.

```
Opcion: 1
Nombre del usuario: Andres
Generos preferidos (separados por coma): Animation, Comedy
Directores preferidos (separados por coma): John Lasseter
Actores preferidos (separados por coma): Tom Hanks
Idiomas preferidos (separados por coma): English
Perfil creado.
```

Podés dejar cualquiera de las listas vacía (presionando Enter sin escribir
nada) si no tenés preferencia en esa categoría.

Las preferencias **no distinguen mayúsculas de minúsculas ni tildes**
(escribir "tom hanks" funciona igual que "Tom Hanks").

- **Opción 2** muestra todas las películas que coinciden con al menos una
  preferencia, sin ningún orden particular.
- **Opción 3** ("por ranking") pide un campo de puntuación (`vote_average`
  o `popularity`) y una cantidad, y devuelve las películas más afines
  ordenadas por un puntaje que combina el puntaje propio de la película, el
  promedio histórico de tus categorías preferidas, y cuántas preferencias
  coinciden.
- **Opción 4** ("al azar") devuelve una selección aleatoria entre las
  películas afines.

## 8. Guardado de cambios

Los cambios hechos en el **CRUD** (agregar/editar/eliminar películas, o
modificar listas) se guardan automáticamente en
`data/movies_unified.json` apenas se completan con éxito. No hace falta
ninguna acción extra para persistirlos.

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
que coincida (o, en el caso de Rankings, la funcionalidad todavía no está
implementada — ver sección 5).

**"Ingrese un numero entero valido."** — Se esperaba un número (por
ejemplo, un id o una cantidad) y se escribió otra cosa. Volvé a escribir
solo el número.

**El catálogo aparece vacío al arrancar** — Falta el archivo
`data/movies_unified.json`. Correlo generando con el notebook
`eda dataset.ipynb` (ver README, sección Dataset).
