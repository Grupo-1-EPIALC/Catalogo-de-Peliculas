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

## Estado / TODO

- [x] Definir fuente de datos del catalogo (The Movies Dataset - Kaggle)
- [x] Descarga y unificacion de CSVs en JSON por pelicula
- [ ] Exploracion de datos (EDA)
- [ ] Limpieza y transformacion adicional
- [ ] Analisis / modelo
- [ ] Conclusiones
