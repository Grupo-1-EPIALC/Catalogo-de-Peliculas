"""
Tests de rankings.py.

A diferencia de crud.py y busqueda.py, rankings.py todavia no fue
implementado por nadie del equipo (sigue siendo el stub original en todas
las ramas). Estos tests se escriben en base al contrato documentado en cada
funcion (ver los comentarios "Parametros"/"Retorna" en rankings.py) y se
saltean automaticamente mientras siga siendo un stub.
"""

import pytest

import rankings


def _rankings_implementado() -> bool:
    return rankings.top_peliculas([], "vote_average", 5) is not None


pytestmark = pytest.mark.skipif(
    not _rankings_implementado(),
    reason="rankings.py todavia no esta implementado (sigue siendo el stub original)",
)


@pytest.fixture
def catalogo_rankings() -> list[dict]:
    return [
        {"id": 1, "genres": ["Drama"], "cast": ["A1"], "directors": ["D1"], "vote_average": 9.0},
        {"id": 2, "genres": ["Drama"], "cast": ["A1"], "directors": ["D1"], "vote_average": 7.0},
        {"id": 3, "genres": ["Comedy"], "cast": ["A2"], "directors": ["D2"], "vote_average": 8.0},
        {"id": 4, "genres": ["Comedy"], "cast": ["A3"], "directors": ["D2"], "vote_average": 5.0},
        {"id": 5, "genres": ["Drama"], "cast": ["A1"], "directors": ["D3"], "vote_average": 6.0},
    ]


class TestTopPeliculas:
    def test_respeta_la_cantidad_pedida(self, catalogo_rankings):
        resultado = rankings.top_peliculas(catalogo_rankings, "vote_average", 2)
        assert len(resultado) == 2

    def test_orden_descendente_por_campo_puntuacion(self, catalogo_rankings):
        resultado = rankings.top_peliculas(catalogo_rankings, "vote_average", 3)
        assert [p["id"] for p in resultado] == [1, 3, 2]

    def test_catalogo_vacio(self):
        assert rankings.top_peliculas([], "vote_average", 5) == []


class TestTopPorCategoria:
    def test_top_por_genero_filtra_y_ordena(self, catalogo_rankings):
        resultado = rankings.top_por_genero(catalogo_rankings, "Drama", "vote_average", 2)
        assert [p["id"] for p in resultado] == [1, 2]

    def test_top_por_actor_filtra_y_ordena(self, catalogo_rankings):
        resultado = rankings.top_por_actor(catalogo_rankings, "A1", "vote_average", 3)
        assert [p["id"] for p in resultado] == [1, 2, 5]

    def test_top_por_director_filtra_y_ordena(self, catalogo_rankings):
        resultado = rankings.top_por_director(catalogo_rankings, "D2", "vote_average", 2)
        assert [p["id"] for p in resultado] == [3, 4]

    def test_categoria_sin_coincidencias(self, catalogo_rankings):
        assert rankings.top_por_genero(catalogo_rankings, "GeneroQueNoExiste", "vote_average", 5) == []


class TestRankingGenerosActoresDirectores:
    def test_ranking_generos_ordenado_de_mayor_a_menor_promedio(self, catalogo_rankings):
        # Drama: (9+7+6)/3 = 7.33..., Comedy: (8+5)/2 = 6.5
        resultado = rankings.ranking_generos(catalogo_rankings, "vote_average")
        generos_en_orden = [genero for genero, _ in resultado]
        assert generos_en_orden == ["Drama", "Comedy"]

    def test_ranking_actores_respeta_minimo_peliculas(self, catalogo_rankings):
        # A1 tiene 3 peliculas, A2 y A3 tienen 1 cada uno: con minimo=2 solo debe quedar A1
        resultado = rankings.ranking_actores(catalogo_rankings, "vote_average", minimo_peliculas=2)
        actores_en_resultado = [actor for actor, _ in resultado]
        assert actores_en_resultado == ["A1"]

    def test_ranking_directores_respeta_minimo_peliculas(self, catalogo_rankings):
        # D1 y D2 tienen 2 peliculas cada uno, D3 tiene 1: con minimo=2, D3 queda afuera
        resultado = rankings.ranking_directores(catalogo_rankings, "vote_average", minimo_peliculas=2)
        directores_en_resultado = {director for director, _ in resultado}
        assert directores_en_resultado == {"D1", "D2"}
        assert "D3" not in directores_en_resultado

    def test_catalogo_vacio_devuelve_lista_vacia(self):
        assert rankings.ranking_generos([], "vote_average") == []
