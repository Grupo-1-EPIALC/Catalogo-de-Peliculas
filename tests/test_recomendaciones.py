"""
Tests de recomendaciones.py.

Unitarios: `CAMPOS_PREFERENCIA` se reemplaza (monkeypatch) por funciones de
busqueda "fake" (comparacion exacta simple, sin normalizacion de texto), asi
la logica propia de recomendaciones.py se prueba aislada de busqueda.py, sin
importar si busqueda.py ya esta implementado localmente o no. Los promedios
historicos usan estadisticas.py real (ya implementado).

Funcional: corre recomendar_por_ranking/recomendar_al_azar con la
implementacion REAL de busqueda.py (no la fake) y con el dataset completo.
Se salta si busqueda.py local sigue siendo un stub, o si falta el dataset.
"""

import json
from pathlib import Path

import pytest

import busqueda
import estadisticas
import rankings
import recomendaciones

RUTA_DATASET_REAL = Path(__file__).resolve().parent.parent / "data" / "movies_unified.json"


def _busqueda_implementada() -> bool:
    # con catalogo vacio y un texto no vacio, la implementacion real siempre
    # devuelve una lista (vacia); el stub (pass) devuelve None
    return busqueda.buscar_por_titulo([], "cualquier cosa") is not None


def _buscar_por_campo_fake(catalogo: list[dict], campo: str, valor: str) -> list[dict]:
    return [p for p in catalogo if valor in (p.get(campo) or [])]


@pytest.fixture
def campos_preferencia_fake(monkeypatch):
    """Reemplaza las funciones de busqueda.py por una comparacion exacta
    simple, para poder probar recomendaciones.py sin depender de que
    busqueda.py ya este implementado (y sin sus reglas de normalizacion de
    texto, que no son el objeto de estos tests)."""
    fake = {
        "generos": ("genres", lambda cat, v: _buscar_por_campo_fake(cat, "genres", v), estadisticas.promedio_por_genero),
        "directores": ("directors", lambda cat, v: _buscar_por_campo_fake(cat, "directors", v), estadisticas.promedio_por_director),
        "actores": ("cast", lambda cat, v: _buscar_por_campo_fake(cat, "cast", v), estadisticas.promedio_por_actor),
        "idiomas": ("spoken_languages", lambda cat, v: _buscar_por_campo_fake(cat, "spoken_languages", v), estadisticas.promedio_por_idioma),
    }
    monkeypatch.setattr(recomendaciones, "CAMPOS_PREFERENCIA", fake)
    return fake


@pytest.fixture
def catalogo_recomendaciones() -> list[dict]:
    return [
        {
            "id": 1, "title": "Toy Story clon", "genres": ["Animation", "Comedy"],
            "directors": ["DirA"], "cast": ["ActorX", "ActorY"],
            "spoken_languages": ["English"], "vote_average": 8.0, "popularity": "10.0",
        },
        {
            "id": 2, "title": "Drama frances", "genres": ["Drama"],
            "directors": ["DirB"], "cast": ["ActorZ"],
            "spoken_languages": ["French"], "vote_average": 6.0, "popularity": "5.0",
        },
        {
            "id": 3, "title": "Animation solo", "genres": ["Animation"],
            "directors": ["DirC"], "cast": ["ActorW"],
            "spoken_languages": ["Japanese"], "vote_average": 7.0, "popularity": "8.0",
        },
        {
            "id": 4, "title": "Sin relacion", "genres": ["Horror"],
            "directors": ["DirD"], "cast": ["ActorV"],
            "spoken_languages": ["German"], "vote_average": 9.0, "popularity": "20.0",
        },
    ]


@pytest.fixture
def perfil() -> dict:
    return recomendaciones.crear_perfil_usuario(
        "Andres",
        generos_preferidos=["Animation"],
        directores_preferidos=[],
        actores_preferidos=["ActorX"],
        idiomas_preferidos=["English"],
    )


class TestPromedioPorCategoriaCombinado:
    """_promedio_por_categoria_combinado combina dos fuentes para actores y
    directores: rankings.py como primaria (mas representativa, con piso
    minimo de peliculas) y estadisticas.py como respaldo. Se monkeypatchea
    `FUNCIONES_RANKING_POR_CATEGORIA` (no `rankings.ranking_actores`
    directamente) porque ese dict ya guarda la referencia a la funcion real
    al importar el modulo; parchear el atributo del modulo `rankings`
    despues no afectaria una referencia ya capturada."""

    def test_usa_rankings_como_fuente_primaria_cuando_esta_disponible(self, monkeypatch):
        monkeypatch.setitem(
            recomendaciones.FUNCIONES_RANKING_POR_CATEGORIA,
            "actores",
            lambda catalogo, campo, minimo: [("ActorA", 99.0)],
        )
        catalogo = [{"id": 1, "cast": ["ActorA"], "vote_average": 5.0}]

        resultado = recomendaciones._promedio_por_categoria_combinado(catalogo, "actores", "vote_average")

        # gana el valor "primario" simulado (99.0), no el crudo de estadisticas.py (5.0)
        assert resultado["ActorA"] == 99.0

    def test_cae_al_promedio_crudo_si_rankings_lo_deja_afuera(self, monkeypatch):
        monkeypatch.setitem(
            recomendaciones.FUNCIONES_RANKING_POR_CATEGORIA,
            "actores",
            lambda catalogo, campo, minimo: [],  # nadie llega al minimo de peliculas
        )
        catalogo = [{"id": 1, "cast": ["ActorB"], "vote_average": 5.0}]

        resultado = recomendaciones._promedio_por_categoria_combinado(catalogo, "actores", "vote_average")

        # como rankings.py no lo incluyo, usa el promedio crudo de estadisticas.py
        assert resultado["ActorB"] == 5.0

    def test_generos_e_idiomas_no_usan_rankings_py(self):
        # rankings.py no tiene ranking de idiomas, y para generos no hay
        # ganancia (pocas categorias); FUNCIONES_RANKING_POR_CATEGORIA
        # deliberadamente no las incluye.
        assert "generos" not in recomendaciones.FUNCIONES_RANKING_POR_CATEGORIA
        assert "idiomas" not in recomendaciones.FUNCIONES_RANKING_POR_CATEGORIA

        catalogo = [{"id": 1, "genres": ["Drama"], "vote_average": 7.0}]
        resultado = recomendaciones._promedio_por_categoria_combinado(catalogo, "generos", "vote_average")
        assert resultado == {"Drama": 7.0}


class TestCrearPerfilUsuario:
    def test_estructura_del_perfil(self):
        perfil = recomendaciones.crear_perfil_usuario("Ana", ["Drama"], ["DirX"], ["ActorY"], ["English"])
        assert perfil == {
            "nombre": "Ana", "generos": ["Drama"], "directores": ["DirX"],
            "actores": ["ActorY"], "idiomas": ["English"],
        }


class TestCalcularAfinidad:
    """calcular_afinidad no llama a busqueda.py (usa su propia comparacion
    normalizada, ver TestComparacionNormalizada), asi que no necesita el
    fixture de mocking."""

    def test_afinidad_con_varias_coincidencias(self, catalogo_recomendaciones, perfil):
        # peli 1: genero Animation + actor ActorX + idioma English = 3
        afinidad = recomendaciones.calcular_afinidad(catalogo_recomendaciones[0], perfil)
        assert afinidad == 3

    def test_afinidad_con_una_coincidencia(self, catalogo_recomendaciones, perfil):
        # peli 3: solo coincide el genero Animation
        afinidad = recomendaciones.calcular_afinidad(catalogo_recomendaciones[2], perfil)
        assert afinidad == 1

    def test_afinidad_sin_coincidencias(self, catalogo_recomendaciones, perfil):
        afinidad = recomendaciones.calcular_afinidad(catalogo_recomendaciones[3], perfil)
        assert afinidad == 0


class TestComparacionNormalizada:
    """Regresion de un bug real: calcular_afinidad (y el promedio historico
    dentro de recomendar_por_ranking) comparaban strings exactos, mientras
    que busqueda.py -y por lo tanto filtrar_peliculas_por_gustos- matchean
    sin importar mayusculas/tildes. Una pelicula que filtrar_peliculas_por_
    gustos encontraba (ej. porque el usuario escribio "tom hanks" en
    minuscula) terminaba con afinidad 0 porque "tom hanks" != "Tom Hanks"."""

    def test_afinidad_ignora_mayusculas(self, catalogo_recomendaciones):
        perfil = recomendaciones.crear_perfil_usuario("Andres", ["animation"], [], [], [])
        assert recomendaciones.calcular_afinidad(catalogo_recomendaciones[0], perfil) == 1

    def test_afinidad_ignora_tildes(self):
        pelicula = {"id": 1, "genres": [], "directors": [], "cast": ["José Rodríguez"], "spoken_languages": []}
        perfil = recomendaciones.crear_perfil_usuario("Andres", [], [], ["jose rodriguez"], [])
        assert recomendaciones.calcular_afinidad(pelicula, perfil) == 1

    def test_preferencia_sin_relacion_no_matchea_por_substring_vacio(self, catalogo_recomendaciones):
        # una preferencia vacia/solo espacios no debe "matchear todo"
        perfil = recomendaciones.crear_perfil_usuario("Andres", ["   "], [], [], [])
        assert recomendaciones.calcular_afinidad(catalogo_recomendaciones[0], perfil) == 0


class TestFiltrarPeliculasPorGustos:
    def test_devuelve_solo_coincidencias(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        resultado = recomendaciones.filtrar_peliculas_por_gustos(catalogo_recomendaciones, perfil)
        assert sorted(p["id"] for p in resultado) == [1, 3]

    def test_sin_duplicados_si_matchea_varias_preferencias(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        # la pelicula 1 matchea genero, actor e idioma a la vez: debe aparecer una sola vez
        resultado = recomendaciones.filtrar_peliculas_por_gustos(catalogo_recomendaciones, perfil)
        ids = [p["id"] for p in resultado]
        assert ids.count(1) == 1

    def test_perfil_sin_gustos_no_devuelve_nada(self, catalogo_recomendaciones, campos_preferencia_fake):
        perfil_vacio = recomendaciones.crear_perfil_usuario("Nadie", [], [], [], [])
        assert recomendaciones.filtrar_peliculas_por_gustos(catalogo_recomendaciones, perfil_vacio) == []


class TestRecomendarPorRanking:
    def test_respeta_la_cantidad_pedida(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        resultado = recomendaciones.recomendar_por_ranking(catalogo_recomendaciones, perfil, "vote_average", 1)
        assert len(resultado) == 1

    def test_prioriza_mayor_afinidad_sobre_puntaje_crudo(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        # peli 1 (afinidad 3, vote_average 8.0) debe superar a peli 3 (afinidad 1, vote_average 7.0)
        resultado = recomendaciones.recomendar_por_ranking(catalogo_recomendaciones, perfil, "vote_average", 2)
        assert [p["id"] for p in resultado] == [1, 3]

    def test_perfil_sin_gustos_devuelve_lista_vacia(self, catalogo_recomendaciones, campos_preferencia_fake):
        perfil_vacio = recomendaciones.crear_perfil_usuario("Nadie", [], [], [], [])
        assert recomendaciones.recomendar_por_ranking(catalogo_recomendaciones, perfil_vacio, "vote_average", 3) == []


class TestRecomendarAlAzar:
    def test_no_supera_la_cantidad_de_coincidencias(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        # solo hay 2 coincidencias (peliculas 1 y 3); pedir 5 no debe romper ni repetir
        resultado = recomendaciones.recomendar_al_azar(catalogo_recomendaciones, perfil, 5)
        assert len(resultado) == 2

    def test_siempre_elige_entre_las_coincidencias(self, catalogo_recomendaciones, perfil, campos_preferencia_fake):
        resultado = recomendaciones.recomendar_al_azar(catalogo_recomendaciones, perfil, 5)
        assert {p["id"] for p in resultado} <= {1, 3}

    def test_perfil_sin_gustos_devuelve_lista_vacia(self, catalogo_recomendaciones, campos_preferencia_fake):
        perfil_vacio = recomendaciones.crear_perfil_usuario("Nadie", [], [], [], [])
        assert recomendaciones.recomendar_al_azar(catalogo_recomendaciones, perfil_vacio, 3) == []


@pytest.mark.skipif(
    not _busqueda_implementada(),
    reason="busqueda.py todavia es un stub local (falta mergear feature/busqueda-peliculas)",
)
@pytest.mark.skipif(
    not RUTA_DATASET_REAL.exists(),
    reason="data/movies_unified.json no existe: correr eda dataset.ipynb primero",
)
class TestFuncionalConBusquedaYDatasetReales:
    """Igual que los tests unitarios de arriba, pero sin mockear nada:
    ejercita recomendaciones.py + busqueda.py + estadisticas.py juntos,
    contra el catalogo real completo."""

    @classmethod
    @pytest.fixture(scope="class")
    def catalogo_real(cls) -> list[dict]:
        with open(RUTA_DATASET_REAL, encoding="utf-8") as archivo:
            return json.load(archivo)

    def test_recomendaciones_coinciden_con_las_preferencias(self, catalogo_real):
        perfil = recomendaciones.crear_perfil_usuario(
            "Andres",
            generos_preferidos=["Animation"],
            directores_preferidos=["John Lasseter"],
            actores_preferidos=["Tom Hanks"],
            idiomas_preferidos=["English"],
        )
        top = recomendaciones.recomendar_por_ranking(catalogo_real, perfil, "vote_average", 5)
        assert len(top) == 5
        assert all(recomendaciones.calcular_afinidad(p, perfil) >= 1 for p in top)

    def test_genero_inexistente_no_rompe(self, catalogo_real):
        perfil = recomendaciones.crear_perfil_usuario("Nadie", ["GeneroQueNoExiste"], [], [], [])
        assert recomendaciones.recomendar_por_ranking(catalogo_real, perfil, "vote_average", 3) == []

    def test_preferencias_con_distinta_capitalizacion_siguen_matcheando(self, catalogo_real):
        # regresion: el usuario rara vez tipea el nombre exacto tal como esta
        # en el dataset (ej. "Tom Hanks"); antes del fix, esto hacia que
        # calcular_afinidad devolviera 0 aunque la pelicula fuera un match real
        perfil = recomendaciones.crear_perfil_usuario(
            "Andres",
            generos_preferidos=["animation"],
            directores_preferidos=["john lasseter"],
            actores_preferidos=["tom hanks"],
            idiomas_preferidos=["ENGLISH"],
        )
        top = recomendaciones.recomendar_por_ranking(catalogo_real, perfil, "vote_average", 5)
        assert len(top) == 5
        assert all(recomendaciones.calcular_afinidad(p, perfil) >= 1 for p in top)

    def test_actor_con_pocas_peliculas_usa_estadisticas_como_respaldo(self, catalogo_real):
        # un actor con 1 sola pelicula no llega al minimo de rankings.py, asi
        # que _promedio_por_categoria_combinado debe caer al promedio crudo
        # de estadisticas.py (y no quedar afuera del diccionario combinado)
        promedio_crudo = estadisticas.promedio_por_actor(catalogo_real, "vote_average")
        ranking_actores = dict(
            rankings.ranking_actores(catalogo_real, "vote_average", recomendaciones.MINIMO_PELICULAS_RANKING)
        )

        solo_en_estadisticas = next(actor for actor in promedio_crudo if actor not in ranking_actores)

        combinado = recomendaciones._promedio_por_categoria_combinado(catalogo_real, "actores", "vote_average")

        assert combinado[solo_en_estadisticas] == promedio_crudo[solo_en_estadisticas]

    def test_actor_con_varias_peliculas_usa_rankings_como_primaria(self, catalogo_real):
        combinado = recomendaciones._promedio_por_categoria_combinado(catalogo_real, "actores", "vote_average")
        primario = dict(
            rankings.ranking_actores(catalogo_real, "vote_average", recomendaciones.MINIMO_PELICULAS_RANKING)
        )

        assert combinado["Tom Hanks"] == primario["Tom Hanks"]
