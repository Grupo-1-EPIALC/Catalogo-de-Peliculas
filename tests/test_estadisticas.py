"""
Tests de estadisticas.py.

Unitarios: catalogo chico armado a mano con valores conocidos, para poder
verificar cada calculo contra el resultado esperado.

Funcional: corre las mismas funciones contra data/movies_unified.json
completo (45.432 peliculas reales). Se salta automaticamente si ese archivo
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

    def test_excluye_valores_en_cero_por_no_ser_datos_reales(self):
        # revenue/budget/vote_count en 0 en este dataset significan "sin
        # dato", no un cero real: no deben contar en el promedio.
        catalogo = [
            {"revenue": 0}, {"revenue": "0"}, {"revenue": 100.0}, {"revenue": 200.0},
        ]
        assert estadisticas.promedio_general(catalogo, "revenue") == 150.0


class TestMedianaGeneral:
    def test_cantidad_impar_de_valores(self, catalogo_calculado):
        # vote_average validos: [8.0, 6.0, 7.0] (D excluida) -> ordenados [6,7,8] -> mediana 7.0
        assert estadisticas.mediana_general(catalogo_calculado, "vote_average") == 7.0

    def test_cantidad_par_de_valores(self, catalogo_calculado):
        # runtime: [100, 120, 90, 80] -> ordenados [80,90,100,120] -> mediana (90+100)/2 = 95.0
        assert estadisticas.mediana_general(catalogo_calculado, "runtime") == 95.0

    def test_ignora_valores_no_convertibles(self, catalogo_calculado):
        assert estadisticas.mediana_general(catalogo_calculado, "popularity") == 10.5

    def test_catalogo_vacio_devuelve_cero(self):
        assert estadisticas.mediana_general([], "vote_average") == 0.0


class TestRangoDeAnios:
    def test_devuelve_minimo_y_maximo(self, catalogo_calculado):
        # release_date validos: 2000-01-01, 2000-05-05, 1999-12-31 (C no tiene)
        assert estadisticas.rango_de_anios(catalogo_calculado) == (1999, 2000)

    def test_catalogo_vacio_devuelve_none(self):
        assert estadisticas.rango_de_anios([]) is None

    def test_sin_release_date_validos_devuelve_none(self):
        assert estadisticas.rango_de_anios([{"release_date": None}, {"release_date": "abc"}]) is None


class TestNormalizarAEscala:
    def test_extremos_mapean_a_1_y_10(self):
        assert estadisticas._normalizar_a_escala(6.0, minimo=6.0, maximo=8.0) == 1.0
        assert estadisticas._normalizar_a_escala(8.0, minimo=6.0, maximo=8.0) == 10.0

    def test_punto_medio_mapea_al_medio_de_la_escala(self):
        assert estadisticas._normalizar_a_escala(7.0, minimo=6.0, maximo=8.0) == 5.5

    def test_sin_variacion_devuelve_punto_medio(self):
        # si minimo == maximo, todos los valores son iguales: no hay forma de
        # decir si es "alto" o "bajo", asi que no se fuerza a un extremo
        assert estadisticas._normalizar_a_escala(5.0, minimo=5.0, maximo=5.0) == 5.5


class TestPromedioNormalizado:
    """promedio_normalizado(catalogo_referencia, subconjunto, campo) reescala
    el promedio de `subconjunto` usando el minimo/maximo de
    `catalogo_referencia`, no el de `subconjunto` — para que dos filtros
    distintos (ej. genero "Comedy" vs genero "Horror") queden en la misma
    escala y se puedan comparar entre si."""

    def test_referencia_y_subconjunto_iguales(self, catalogo_calculado):
        # vote_average: promedio 7.0, min 6.0, max 8.0 -> 1 + 9*(7-6)/(8-6) = 5.5
        resultado = estadisticas.promedio_normalizado(catalogo_calculado, catalogo_calculado, "vote_average")
        assert resultado == 5.5

    def test_usa_el_rango_de_la_referencia_no_del_subconjunto(self, catalogo_calculado):
        # subconjunto de una sola pelicula (vote_average 8.0): si se usara el
        # rango del subconjunto (min == max == 8.0) darian 5.5 (punto medio).
        # Usando el rango del catalogo completo (min 6.0, max 8.0), 8.0 es el
        # maximo -> debe dar 10.0.
        subconjunto = [catalogo_calculado[0]]
        resultado = estadisticas.promedio_normalizado(catalogo_calculado, subconjunto, "vote_average")
        assert resultado == 10.0

    def test_referencia_sin_datos_validos_devuelve_cero(self, catalogo_calculado):
        assert estadisticas.promedio_normalizado([], catalogo_calculado, "vote_average") == 0.0


class TestResumenDeCampos:
    def test_incluye_cantidad_medias_medianas_y_combinado(self, catalogo_calculado):
        resultado = estadisticas.resumen_de_campos(catalogo_calculado, catalogo_calculado)

        assert resultado["cantidad_peliculas"] == 4
        assert resultado["medias"] == {
            "vote_average": 7.0, "vote_count": 0.0, "runtime": 97.5,
            "revenue": 0.0, "budget": 1166.67, "popularity": 12.0,
        }
        assert resultado["medianas"] == {
            "vote_average": 7.0, "vote_count": 0.0, "runtime": 95.0,
            "revenue": 0.0, "budget": 1000.0, "popularity": 10.5,
        }
        assert resultado["promedio_normalizado_combinado"] == 3.11

    def test_subconjunto_filtrado_usa_su_propia_cantidad_y_medias(self, catalogo_calculado):
        subconjunto = catalogo_calculado[:2]  # peliculas A y B
        resultado = estadisticas.resumen_de_campos(catalogo_calculado, subconjunto)

        assert resultado["cantidad_peliculas"] == 2
        assert resultado["medias"]["vote_average"] == 7.0  # (8.0 + 6.0) / 2
        assert resultado["medianas"]["vote_average"] == 7.0

    def test_catalogo_vacio(self):
        resultado = estadisticas.resumen_de_campos([], [])
        assert resultado["cantidad_peliculas"] == 0
        assert all(valor == 0.0 for valor in resultado["medias"].values())
        assert resultado["promedio_normalizado_combinado"] == 0.0

    def test_runtime_se_muestra_pero_no_entra_al_combinado(self, catalogo_calculado):
        # runtime no es un score (es una duracion), no debe afectar el
        # promedio normalizado combinado aunque su media/mediana se muestren.
        resultado = estadisticas.resumen_de_campos(catalogo_calculado, catalogo_calculado)
        assert "runtime" in resultado["medias"]
        assert "runtime" in resultado["medianas"]
        assert "runtime" not in estadisticas.CAMPOS_PROMEDIO_COMBINADO

        catalogo_runtime_extremo = [dict(p, runtime=999999.0) for p in catalogo_calculado]
        resultado_extremo = estadisticas.resumen_de_campos(catalogo_runtime_extremo, catalogo_runtime_extremo)
        assert resultado_extremo["promedio_normalizado_combinado"] == resultado["promedio_normalizado_combinado"]


class TestPromedioPorCategoria:
    """promedio_por_genero/_director/_actor/_pais/_idioma ya no tienen una
    opcion de menu propia, pero recomendaciones.py las sigue usando
    internamente (CAMPOS_PREFERENCIA) para el promedio historico de las
    categorias preferidas del usuario."""

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


class TestTop5:
    def test_top5_generos_ordenado_de_mayor_a_menor(self, catalogo_calculado):
        # Comedy: (8.0+7.0)/2 = 7.5, Drama: (8.0+6.0)/2 = 7.0
        assert estadisticas.top5_generos(catalogo_calculado) == [("Comedy", 7.5), ("Drama", 7.0)]

    def test_top5_directores(self, catalogo_calculado):
        assert estadisticas.top5_directores(catalogo_calculado) == [("Dir1", 7.0), ("Dir2", 7.0)]

    def test_top5_actores(self, catalogo_calculado):
        resultado = estadisticas.top5_actores(catalogo_calculado)
        assert resultado[0] == ("Actor2", 7.5)

    def test_top5_paises(self, catalogo_calculado):
        assert estadisticas.top5_paises(catalogo_calculado) == [("USA", 7.0), ("France", 7.0)]

    def test_top5_idiomas(self, catalogo_calculado):
        assert estadisticas.top5_idiomas(catalogo_calculado) == [("English", 7.0), ("French", 7.0)]

    def test_top5_anios(self, catalogo_calculado):
        # 2000: peliculas A (8.0) y B (6.0) -> promedio 7.0; 1999: pelicula D, sin vote_average -> no cuenta
        assert estadisticas.top5_anios(catalogo_calculado) == [(2000, 7.0)]

    def test_top5_devuelve_como_maximo_5(self):
        catalogo_muchos_generos = [
            {"id": i, "genres": [f"Genero{i}"], "vote_average": float(i)}
            for i in range(10)
        ]
        assert len(estadisticas.top5_generos(catalogo_muchos_generos)) == 5

    def test_top5_catalogo_vacio(self):
        assert estadisticas.top5_generos([]) == []


@pytest.mark.skipif(
    not RUTA_DATASET_REAL.exists(),
    reason="data/movies_unified.json no existe: correr eda dataset.ipynb primero (no esta versionado en git)",
)
class TestFuncionalContraDatasetReal:
    """Corre las funciones de estadisticas.py contra el catalogo real completo
    para verificar que no rompen con los tipos mixtos del dataset original y
    que los resultados son razonables."""

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

    def test_resumen_de_campos_sobre_el_catalogo_completo(self, catalogo_real):
        resumen = estadisticas.resumen_de_campos(catalogo_real, catalogo_real)
        assert resumen["cantidad_peliculas"] == len(catalogo_real)
        assert set(resumen["medias"]) == set(estadisticas.CAMPOS_NUMERICOS)
        assert set(resumen["medianas"]) == set(estadisticas.CAMPOS_NUMERICOS)
        assert 1.0 <= resumen["promedio_normalizado_combinado"] <= 10.0

    def test_resumen_de_campos_de_un_filtro_usa_la_misma_escala_de_referencia(self, catalogo_real):
        # dos subconjuntos distintos, normalizados contra el mismo catalogo
        # completo: sus valores normalizados tienen que caer dentro de 1-10
        # igual (no cada uno con su propia escala relativa)
        subconjunto_a = [p for p in catalogo_real if "Animation" in (p.get("genres") or [])]
        subconjunto_b = [p for p in catalogo_real if "Horror" in (p.get("genres") or [])]

        resumen_a = estadisticas.resumen_de_campos(catalogo_real, subconjunto_a)
        resumen_b = estadisticas.resumen_de_campos(catalogo_real, subconjunto_b)

        assert 1.0 <= resumen_a["promedio_normalizado_combinado"] <= 10.0
        assert 1.0 <= resumen_b["promedio_normalizado_combinado"] <= 10.0

    def test_top5_generos_son_generos_reales_del_catalogo(self, catalogo_real):
        generos_reales = {g for p in catalogo_real for g in (p.get("genres") or [])}
        top5 = estadisticas.top5_generos(catalogo_real)
        assert len(top5) == 5
        assert all(genero in generos_reales for genero, _ in top5)

    def test_top5_anios_son_anios_razonables(self, catalogo_real):
        top5 = estadisticas.top5_anios(catalogo_real)
        assert len(top5) == 5
        assert all(1870 <= anio <= 2026 for anio, _ in top5)
