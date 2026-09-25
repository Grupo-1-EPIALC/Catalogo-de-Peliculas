"""
Tests de busqueda.py.

busqueda.py ya fue implementado (rama feature/busqueda-peliculas), pero esa
rama todavia no esta mergeada a develop. Estos tests se saltean
automaticamente si el busqueda.py local sigue siendo el stub original (ver
`_busqueda_implementada`), y corren solos apenas se mergee la implementacion
real.
"""

import pytest

import busqueda


def _busqueda_implementada() -> bool:
    # con catalogo vacio y texto no vacio, la implementacion real siempre
    # devuelve una lista (vacia); el stub (pass) devuelve None
    return busqueda.buscar_por_titulo([], "cualquier cosa") is not None


pytestmark = pytest.mark.skipif(
    not _busqueda_implementada(),
    reason="busqueda.py todavia es un stub local (falta mergear feature/busqueda-peliculas)",
)


class TestBuscarPorTitulo:
    def test_encuentra_por_coincidencia_parcial_insensible_a_mayusculas(self, catalogo_prueba):
        resultado = busqueda.buscar_por_titulo(catalogo_prueba, "toy story")
        assert sorted(p["id"] for p in resultado) == [1, 2]

    def test_encuentra_por_original_title_con_tildes(self, catalogo_prueba):
        # "Amelie" tiene original_title "Le Fabuleux Destin d'Amelie Poulain"
        resultado = busqueda.buscar_por_titulo(catalogo_prueba, "amélie")
        assert [p["id"] for p in resultado] == [3]

    def test_texto_vacio_no_devuelve_nada(self, catalogo_prueba):
        assert busqueda.buscar_por_titulo(catalogo_prueba, "") == []

    def test_sin_coincidencias(self, catalogo_prueba):
        assert busqueda.buscar_por_titulo(catalogo_prueba, "no existe esta pelicula") == []


class TestBuscarPorActorDirectorGenero:
    def test_buscar_por_actor(self, catalogo_prueba):
        resultado = busqueda.buscar_por_actor(catalogo_prueba, "Tom Hanks")
        assert sorted(p["id"] for p in resultado) == [1, 2]

    def test_buscar_por_director(self, catalogo_prueba):
        resultado = busqueda.buscar_por_director(catalogo_prueba, "Akira Kurosawa")
        assert [p["id"] for p in resultado] == [4]

    def test_buscar_por_genero(self, catalogo_prueba):
        resultado = busqueda.buscar_por_genero(catalogo_prueba, "Comedy")
        assert sorted(p["id"] for p in resultado) == [1, 2, 3]

    def test_pelicula_con_listas_vacias_nunca_aparece(self, catalogo_prueba):
        # la pelicula 5 tiene cast/directors/genres vacios
        for funcion, valor in [
            (busqueda.buscar_por_actor, "cualquiera"),
            (busqueda.buscar_por_director, "cualquiera"),
            (busqueda.buscar_por_genero, "cualquiera"),
        ]:
            resultado = funcion(catalogo_prueba, valor)
            assert all(p["id"] != 5 for p in resultado)


class TestBuscarPorPaisIdiomaPalabraClave:
    def test_buscar_por_pais(self, catalogo_prueba):
        resultado = busqueda.buscar_por_pais(catalogo_prueba, "Japan")
        assert [p["id"] for p in resultado] == [4]

    def test_buscar_por_idioma_coincide_con_original_language(self, catalogo_prueba):
        resultado = busqueda.buscar_por_idioma(catalogo_prueba, "ja")
        assert [p["id"] for p in resultado] == [4]

    def test_buscar_por_idioma_coincide_con_spoken_languages(self, catalogo_prueba):
        resultado = busqueda.buscar_por_idioma(catalogo_prueba, "French")
        assert [p["id"] for p in resultado] == [3]

    def test_buscar_por_palabra_clave(self, catalogo_prueba):
        resultado = busqueda.buscar_por_palabra_clave(catalogo_prueba, "toy")
        assert sorted(p["id"] for p in resultado) == [1, 2]


class TestBusquedaCombinada:
    def test_filtros_vacios_devuelve_todo_el_catalogo(self, catalogo_prueba):
        resultado = busqueda.busqueda_combinada(catalogo_prueba, {})
        assert len(resultado) == len(catalogo_prueba)

    def test_combina_varios_filtros_con_and(self, catalogo_prueba):
        # genero Comedy Y pais France -> solo Amelie
        resultado = busqueda.busqueda_combinada(catalogo_prueba, {"genero": "Comedy", "pais": "France"})
        assert [p["id"] for p in resultado] == [3]

    def test_combinacion_sin_resultados(self, catalogo_prueba):
        resultado = busqueda.busqueda_combinada(catalogo_prueba, {"genero": "Comedy", "pais": "Japan"})
        assert resultado == []

    def test_filtro_por_rango_de_anios(self, catalogo_prueba):
        resultado = busqueda.busqueda_combinada(catalogo_prueba, {"anio_desde": "1990", "anio_hasta": "2000"})
        assert sorted(p["id"] for p in resultado) == [1, 2]

    def test_alias_palabra_clave_y_keyword(self, catalogo_prueba):
        por_alias = busqueda.busqueda_combinada(catalogo_prueba, {"palabra_clave": "samurai"})
        por_keyword = busqueda.busqueda_combinada(catalogo_prueba, {"keyword": "samurai"})
        assert por_alias == por_keyword == [catalogo_prueba[3]]


class TestResumirPelicula:
    def test_devuelve_id_titulo_anio_y_generos(self, catalogo_prueba):
        assert busqueda.resumir_pelicula(catalogo_prueba[0]) == {
            "id": 1, "title": "Toy Story", "anio": 1995,
            "genres": ["Animation", "Comedy", "Family"],
        }

    def test_datos_faltantes(self, catalogo_prueba):
        # la pelicula 5 no tiene fecha ni generos
        assert busqueda.resumir_pelicula(catalogo_prueba[4]) == {
            "id": 5, "title": "Sin Datos", "anio": None, "genres": [],
        }

    def test_generos_es_copia_no_alias(self, catalogo_prueba):
        resumen = busqueda.resumir_pelicula(catalogo_prueba[0])
        resumen["genres"].append("Terror")
        assert "Terror" not in catalogo_prueba[0]["genres"]


class TestFlagResumen:
    def test_actor_con_resumen_devuelve_listado(self, catalogo_prueba):
        resultado = busqueda.buscar_por_actor(catalogo_prueba, "Tom Hanks", resumen=True)
        assert resultado == [
            {"id": 1, "title": "Toy Story", "anio": 1995,
             "genres": ["Animation", "Comedy", "Family"]},
            {"id": 2, "title": "Toy Story 2", "anio": 1999,
             "genres": ["Animation", "Comedy", "Family"]},
        ]

    def test_por_defecto_sigue_devolviendo_objeto_completo(self, catalogo_prueba):
        resultado = busqueda.buscar_por_actor(catalogo_prueba, "Tom Hanks")
        assert resultado == [catalogo_prueba[0], catalogo_prueba[1]]
        assert "cast" in resultado[0]

    def test_titulo_con_resumen(self, catalogo_prueba):
        resultado = busqueda.buscar_por_titulo(catalogo_prueba, "toy story", resumen=True)
        assert [resumen["id"] for resumen in resultado] == [1, 2]
        assert set(resultado[0]) == {"id", "title", "anio", "genres"}

    def test_combinada_con_resumen_filtra_en_completo_y_resume_al_final(self, catalogo_prueba):
        resultado = busqueda.busqueda_combinada(
            catalogo_prueba, {"genero": "Comedy", "pais": "France"}, resumen=True
        )
        assert resultado == [
            {"id": 3, "title": "Amelie", "anio": 2001, "genres": ["Comedy", "Romance"]}
        ]

    def test_combinada_vacia_con_resumen_devuelve_todo_resumido(self, catalogo_prueba):
        resultado = busqueda.busqueda_combinada(catalogo_prueba, {}, resumen=True)
        assert len(resultado) == len(catalogo_prueba)
        assert all(set(resumen) == {"id", "title", "anio", "genres"} for resumen in resultado)
