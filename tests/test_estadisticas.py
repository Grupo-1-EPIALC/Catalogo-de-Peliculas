"""
Tests de estadisticas.py.

Unitarios: catalogo chico armado a mano con valores conocidos, para poder
verificar cada promedio contra el calculo esperado.

Funcional: corre las mismas funciones contra data/movies_unified.json
completo (45.433 peliculas reales). Se salta automaticamente si ese archivo
no existe (no esta versionado, lo genera `eda dataset.ipynb`).
"""

import json
from pathlib import Path

import pytest

import estadisticas

RUTA_DATASET_REAL = Path(__file__).resolve().parent.parent / "data" / "movies_unified.json"


@pytest.fixture
def catalogo_calculado() -> list[dict]:
    return [
        {
            "id": 1, "title": "A",
            "genres": ["Drama", "Comedy"], "directors": ["Dir1"],
            "cast": ["Actor1", "Actor2"], "production_countries": ["USA"],
            "spoken_languages": ["English"],
            "vote_average": 8.0, "runtime": 100.0, "budget": "1000", "popularity": "10.5",
            "release_date": "2000-01-01",
        },
        {
            "id": 2, "title": "B",
            "genres": ["Drama"], "directors": ["Dir1"],
            "cast": ["Actor1"], "production_countries": ["USA"],
            "spoken_languages": ["English"],
            "vote_average": 6.0, "runtime": 120.0, "budget": "2000", "popularity": "20.5",
            "release_date": "2000-05-05",
        },
        {
            "id": 3, "title": "C",
            "genres": ["Comedy"], "directors": ["Dir2"],
            "cast": ["Actor2", "Actor3"], "production_countries": ["France"],
            "spoken_languages": ["French"],
            "vote_average": 7.0, "runtime": 90.0, "budget": None, "popularity": "abc",
            "release_date": None,
        },
        {
            "id": 4, "title": "D",
            "genres": [], "directors": [],
            "cast": [], "production_countries": [],
            "spoken_languages": [],
            "vote_average": None, "runtime": 80.0, "budget": "500", "popularity": "5.0",
            "release_date": "1999-12-31",
        },
    ]


class TestPromedioGeneral:
    def test_vote_average(self, catalogo_calculado):
        assert estadisticas.promedio_general(catalogo_calculado, "vote_average") == 7.0

    def test_runtime(self, catalogo_calculado):
        assert estadisticas.promedio_general(catalogo_calculado, "runtime") == 97.5

    def test_ignora_valores_no_convertibles(self, catalogo_calculado):
        # "popularity" de la pelicula C es el string "abc", no convertible a float
        assert estadisticas.promedio_general(catalogo_calculado, "popularity") == 12.0

    def test_convierte_campos_string_a_float(self, catalogo_calculado):
        # "budget" viene como string en el JSON real; una pelicula tiene budget None
        assert estadisticas.promedio_general(catalogo_calculado, "budget") == round(3500 / 3, 2)

    def test_catalogo_vacio_devuelve_cero(self):
        assert estadisticas.promedio_general([], "vote_average") == 0.0


class TestPromedioPorCategoria:
    def test_por_genero(self, catalogo_calculado):
        assert estadisticas.promedio_por_genero(catalogo_calculado, "vote_average") == {
            "Drama": 7.0, "Comedy": 7.5,
        }

    def test_por_director(self, catalogo_calculado):
        assert estadisticas.promedio_por_director(catalogo_calculado, "vote_average") == {
            "Dir1": 7.0, "Dir2": 7.0,
        }

    def test_por_actor(self, catalogo_calculado):
        assert estadisticas.promedio_por_actor(catalogo_calculado, "vote_average") == {
            "Actor1": 7.0, "Actor2": 7.5, "Actor3": 7.0,
        }

    def test_por_pais(self, catalogo_calculado):
        assert estadisticas.promedio_por_pais(catalogo_calculado, "vote_average") == {
            "USA": 7.0, "France": 7.0,
        }

    def test_por_idioma(self, catalogo_calculado):
        assert estadisticas.promedio_por_idioma(catalogo_calculado, "vote_average") == {
            "English": 7.0, "French": 7.0,
        }

    def test_catalogo_vacio_devuelve_diccionario_vacio(self):
        assert estadisticas.promedio_por_genero([], "vote_average") == {}


class TestPeliculasPorAnio:
    def test_cuenta_por_anio_e_ignora_fechas_faltantes(self, catalogo_calculado):
        # la pelicula C tiene release_date None y se ignora
        assert estadisticas.peliculas_por_anio(catalogo_calculado) == {2000: 2, 1999: 1}

    def test_catalogo_vacio(self):
        assert estadisticas.peliculas_por_anio([]) == {}


class TestResumenEstadistico:
    def test_resumen_completo(self, catalogo_calculado):
        assert estadisticas.resumen_estadistico(catalogo_calculado) == {
            "total_peliculas": 4,
            "promedio_vote_average": 7.0,
            "promedio_runtime": 97.5,
            "promedio_popularity": 12.0,
        }


@pytest.mark.skipif(
    not RUTA_DATASET_REAL.exists(),
    reason="data/movies_unified.json no existe: correr eda dataset.ipynb primero (no esta versionado en git)",
)
class TestFuncionalContraDatasetReal:
    """Corre las funciones de estadisticas.py contra el catalogo real completo
    (45.433 peliculas) para verificar que no rompen con los tipos mixtos del
    dataset original y que los resultados son razonables."""

    @classmethod
    @pytest.fixture(scope="class")
    def catalogo_real(cls) -> list[dict]:
        with open(RUTA_DATASET_REAL, encoding="utf-8") as archivo:
            return json.load(archivo)

    def test_promedio_general_vote_average_en_rango_valido(self, catalogo_real):
        promedio = estadisticas.promedio_general(catalogo_real, "vote_average")
        assert 0.0 <= promedio <= 10.0

    def test_cantidad_generos_distintos_razonable(self, catalogo_real):
        # TMDB usa una taxonomia fija de generos (~20)
        generos = estadisticas.promedio_por_genero(catalogo_real, "vote_average")
        assert 15 <= len(generos) <= 25

    def test_resumen_estadistico_incluye_todas_las_peliculas(self, catalogo_real):
        resumen = estadisticas.resumen_estadistico(catalogo_real)
        assert resumen["total_peliculas"] == len(catalogo_real)

    def test_peliculas_por_anio_no_supera_el_total(self, catalogo_real):
        anios = estadisticas.peliculas_por_anio(catalogo_real)
        assert sum(anios.values()) <= len(catalogo_real)
