# Catalogo de Peliculas

Catalogo de Peliculas para TP de Elementos de Programacion IA & Low Code.

> Proyecto en construccion: este README se ira completando a medida que avance el trabajo.

## Entorno de desarrollo

El proyecto usa un entorno virtual de Python (`.venv`) con las siguientes librerias base:

- pandas
- numpy
- matplotlib
- requests
- kagglehub

### Crear el entorno

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En Bash/Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

### Actualizar dependencias

Si instalas una libreria nueva dentro del entorno, actualiza `requirements.txt`:

```bash
pip freeze > requirements.txt
```

## Dataset

Se usa [The Movies Dataset](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset) de Kaggle, descargado con `kagglehub` desde el notebook `eda dataset.ipynb`.

`kagglehub` requiere credenciales de Kaggle configuradas en la maquina (`~/.kaggle/kaggle.json` o las variables de entorno `KAGGLE_USERNAME` / `KAGGLE_KEY`).

El notebook unifica `movies_metadata.csv`, `credits.csv` y `keywords.csv` en un unico objeto JSON por pelicula, parseando las columnas anidadas (generos, reparto, directores, keywords, compañias/paises productores) a listas de valores y descartando los ids internos de esas entidades. Solo se conserva el `id` de la pelicula como referencia. El resultado se guarda en `data/movies_unified.json` (carpeta no versionada).

## Estructura del proyecto

- `eda dataset.ipynb`: descarga y unificacion del dataset.
- `data/`: dataset crudo y unificado (generado localmente, ignorado por git).
- `crud.py`: alta, baja, modificacion y consulta de peliculas.
- `busqueda.py`: busqueda y filtrado (titulo, actor, director, genero, pais, idioma).
- `rankings.py`: top peliculas y rankings por genero/actor/director.
- `estadisticas.py`: promedios e indicadores por categoria.
- `recomendaciones.py`: perfil de usuario y recomendaciones (ranking / al azar).
- `main.py`: punto de entrada, integra todos los modulos en un menu por consola.

Todos los archivos `.py` de arriba estan armados como **estructura** (firmas de
funciones con tipos y docstrings, sin logica todavia: `pass  # TODO: implementar`).
Cada funcion documenta arriba sus parametros y su valor de retorno.

## Nivel de complejidad por archivo

Guia orientativa para que cada integrante elija que modulo implementar segun
el desafio que busca. La escala va de 1 (mas simple) a 5 (mas complejo).

| Archivo               | Complejidad | Por que |
|------------------------|:-----------:|---------|
| `crud.py`              | ⭐⭐ (2/5)   | Manejo basico de listas/diccionarios, validaciones y `try/except`. Es la base que usan los demas modulos, conviene implementarlo primero. |
| `busqueda.py`           | ⭐⭐ (2/5)   | Filtrado con comprension de listas y comparacion de texto. `busqueda_combinada` suma un poco mas al combinar varios criterios. |
| `estadisticas.py`       | ⭐⭐⭐ (3/5) | Requiere agrupar peliculas por categoria (un genero/actor aparece en muchas peliculas a la vez) y calcular promedios; `peliculas_por_anio` suma parseo de fechas. |
| `main.py`               | ⭐⭐⭐ (3/5) | No tiene logica de negocio propia, pero exige integrar todos los modulos, manejar la entrada del usuario con errores (opciones invalidas, datos mal ingresados) y armar un menu interactivo completo. |
| `rankings.py`           | ⭐⭐⭐⭐ (4/5) | Combina agrupamiento, ordenamiento por puntuacion y un umbral minimo de peliculas para que los rankings de actor/director sean representativos. |
| `recomendaciones.py`    | ⭐⭐⭐⭐ (4/5) | Integra filtrado por gustos, un calculo de afinidad propio y dos estrategias de recomendacion distintas (ranking vs. aleatoria con `random`). |

Orden sugerido de implementacion: `crud.py` → `busqueda.py` → `estadisticas.py`
→ `rankings.py` → `recomendaciones.py`, y `main.py` al final (o en paralelo,
una vez que las funciones que va a llamar ya existen).

## Estado / TODO

- [x] Definir fuente de datos del catalogo (The Movies Dataset - Kaggle)
- [x] Descarga y unificacion de CSVs en JSON por pelicula
- [x] Estructura de modulos (`crud.py`, `busqueda.py`, `rankings.py`, `estadisticas.py`, `recomendaciones.py`, `main.py`) sin implementar
- [ ] Implementacion de cada modulo (ver tabla de complejidad arriba)
- [ ] Exploracion de datos (EDA)
- [ ] Limpieza y transformacion adicional
- [ ] Analisis / modelo
- [ ] Conclusiones


Escribo texto para probar mr por rama nueva