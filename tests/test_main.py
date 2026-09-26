"""
Tests de main.py.

Unitarios: los helpers de entrada/salida (_pedir_entero, _pedir_lista,
_mostrar_resultado, _ordenar_por_valor_desc, mostrar_menu) no dependen de
crud/busqueda/rankings/recomendaciones, asi que se prueban aislados
(monkeypatch sobre input(), capsys para stdout).

Funcional: corre menu_estadisticas end-to-end, simulando la entrada del
usuario, contra un catalogo en memoria. Usa estadisticas.py real (ya
implementado); no depende de crud.py ni busqueda.py.
"""

import builtins

import pytest

import main


class TestPedirEntero:
    def test_devuelve_el_entero_ingresado(self, monkeypatch):
        monkeypatch.setattr(builtins, "input", lambda _: "7")
        assert main._pedir_entero("Opcion: ") == 7

    def test_reintenta_ante_entrada_invalida(self, monkeypatch, capsys):
        respuestas = iter(["no es un numero", "3"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))
        assert main._pedir_entero("Opcion: ") == 3
        assert "Ingrese un numero entero valido." in capsys.readouterr().out


class TestPedirLista:
    def test_separa_por_coma_y_limpia_espacios(self, monkeypatch):
        monkeypatch.setattr(builtins, "input", lambda _: " Drama, Accion ,Comedy ")
        assert main._pedir_lista("Generos: ") == ["Drama", "Accion", "Comedy"]

    def test_entrada_vacia_devuelve_lista_vacia(self, monkeypatch):
        monkeypatch.setattr(builtins, "input", lambda _: "")
        assert main._pedir_lista("Generos: ") == []

    def test_ignora_comas_sueltas(self, monkeypatch):
        monkeypatch.setattr(builtins, "input", lambda _: "Drama,, ,Comedy")
        assert main._pedir_lista("Generos: ") == ["Drama", "Comedy"]


class TestMostrarResultado:
    def test_resultado_none(self, capsys):
        main._mostrar_resultado(None)
        assert "sin resultado" in capsys.readouterr().out

    def test_lista_de_peliculas_corta_no_se_trunca(self, capsys):
        peliculas = [{"title": "A"}, {"title": "B"}]
        main._mostrar_resultado(peliculas)
        salida = capsys.readouterr().out
        assert "A" in salida and "B" in salida
        assert "mas." not in salida

    def test_lista_de_peliculas_larga_se_trunca(self, capsys):
        peliculas = [{"title": f"Pelicula {i}"} for i in range(30)]
        main._mostrar_resultado(peliculas)
        salida = capsys.readouterr().out
        assert salida.count("Pelicula") == main._LIMITE_RESULTADOS_MOSTRADOS
        assert "... y 10 peliculas mas." in salida

    def test_diccionario_largo_se_trunca(self, capsys):
        diccionario = {f"clave{i}": i for i in range(25)}
        main._mostrar_resultado(diccionario)
        salida = capsys.readouterr().out
        assert "... y 5 mas." in salida

    def test_valor_escalar(self, capsys):
        main._mostrar_resultado(7.35)
        assert "7.35" in capsys.readouterr().out


class TestMostrarMenu:
    def test_imprime_todas_las_opciones(self, capsys):
        main.mostrar_menu({1: "Uno", 2: "Dos", 0: "Salir"})
        salida = capsys.readouterr().out
        assert "1. Uno" in salida
        assert "2. Dos" in salida
        assert "0. Salir" in salida


class TestEstructuraDeMenus:
    """Todo submenu debe tener una opcion 0 para volver/salir, y las demas
    opciones numeradas de forma consecutiva desde 1 (para que no haya huecos
    ni numeros repetidos, algo que ya causo bugs en una version anterior de
    main.py)."""

    @pytest.mark.parametrize(
        "menu",
        [main.MENU_PRINCIPAL, main.MENU_BUSQUEDA, main.MENU_CRUD, main.MENU_RANKINGS,
         main.MENU_ESTADISTICAS, main.MENU_RECOMENDACIONES],
    )
    def test_tiene_opcion_cero(self, menu):
        assert 0 in menu

    @pytest.mark.parametrize(
        "menu",
        [main.MENU_PRINCIPAL, main.MENU_BUSQUEDA, main.MENU_CRUD, main.MENU_RANKINGS,
         main.MENU_ESTADISTICAS, main.MENU_RECOMENDACIONES],
    )
    def test_numeracion_consecutiva_sin_huecos(self, menu):
        opciones_distintas_de_cero = sorted(k for k in menu if k != 0)
        assert opciones_distintas_de_cero == list(range(1, len(opciones_distintas_de_cero) + 1))


class TestMenuEstadisticasFuncional:
    """Smoke test funcional: simula al usuario navegando el submenu de
    estadisticas (que filtra con busqueda.py real y resume con
    estadisticas.py real) contra un catalogo en memoria. No depende de
    crud.py ni de leer ningun archivo."""

    @pytest.fixture
    def catalogo(self) -> list[dict]:
        return [
            {"id": 1, "title": "A", "vote_average": 8.0, "runtime": 100.0,
             "popularity": "10.0", "genres": ["Comedy"], "directors": ["DirX"], "cast": ["ActorX"],
             "production_countries": ["USA"], "spoken_languages": ["English"], "release_date": "2000-01-01"},
            {"id": 2, "title": "B", "vote_average": 6.0, "runtime": 120.0,
             "popularity": "20.0", "genres": ["Drama"], "directors": ["DirY"], "cast": ["ActorY"],
             "production_countries": ["France"], "spoken_languages": ["French"], "release_date": "2001-01-01"},
        ]

    def test_opcion_genero_filtra_y_muestra_resumen(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["1", "Comedy", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_estadisticas(catalogo)

        salida = capsys.readouterr().out
        assert "Cantidad de peliculas: 1" in salida
        assert "vote_average -> media: 8.0" in salida

    def test_opcion_anio_muestra_el_rango_disponible_y_filtra(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["6", "2000", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_estadisticas(catalogo)

        salida = capsys.readouterr().out
        assert "Anios disponibles: 2000 - 2001" in salida
        assert "Cantidad de peliculas: 1" in salida

    def test_opcion_general_no_pide_ningun_valor_y_muestra_top5(self, catalogo, monkeypatch, capsys):
        # la opcion 7 no filtra nada (a diferencia de 1 a 6): solo hacen
        # falta 2 respuestas (elegir la opcion, y despues volver al menu)
        respuestas = iter(["7", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_estadisticas(catalogo)

        salida = capsys.readouterr().out
        assert "Cantidad de peliculas: 2" in salida
        assert "Promedio normalizado combinado (escala 1-10):" in salida
        assert "Top 5 generos (vote_average):" in salida
        assert "Top 5 directores (vote_average):" in salida
        assert "Top 5 actores (vote_average):" in salida
        assert "Top 5 paises (vote_average):" in salida
        assert "Top 5 idiomas (vote_average):" in salida
        assert "Top 5 anios (vote_average):" in salida

    def test_opcion_invalida_no_rompe_y_vuelve_a_mostrar_el_menu(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["99", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_estadisticas(catalogo)

        assert "Opcion invalida." in capsys.readouterr().out


class TestMenuCrudFuncional:
    """menu_crud contra crud.py real: crud.py levanta ValueError ante id
    duplicado/inexistente, campo de lista invalido, etc. Estos tests son
    regresion de un bug real: antes de agregar el try/except en menu_crud,
    cualquiera de estos casos (perfectamente esperables por un uso normal)
    tumbaba toda la aplicacion con una excepcion sin capturar."""

    @pytest.fixture
    def catalogo(self) -> list[dict]:
        return [{"id": 1, "title": "Existente", "genres": ["Drama"]}]

    def test_id_duplicado_al_crear_no_rompe_y_no_modifica_el_catalogo(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["2", "1", "Titulo Duplicado", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        resultado = main.menu_crud(catalogo)

        assert len(resultado) == 1
        assert "No se pudo completar la operacion" in capsys.readouterr().out

    def test_id_inexistente_al_editar_no_rompe(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["3", "9999", "title", "Nuevo Titulo", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        resultado = main.menu_crud(catalogo)

        assert resultado[0]["title"] == "Existente"
        assert "No se pudo completar la operacion" in capsys.readouterr().out

    def test_id_inexistente_al_eliminar_no_rompe(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["4", "9999", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        resultado = main.menu_crud(catalogo)

        assert len(resultado) == 1
        assert "No se pudo completar la operacion" in capsys.readouterr().out

    def test_campo_lista_invalido_no_rompe(self, catalogo, monkeypatch, capsys):
        respuestas = iter(["5", "1", "title", "no es una lista", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_crud(catalogo)

        assert "No se pudo completar la operacion" in capsys.readouterr().out

    def test_operacion_valida_sigue_funcionando(self, catalogo, monkeypatch, tmp_path):
        # RUTA_DATOS apunta a un archivo temporal para no pisar data/movies_unified.json;
        # monkeypatch restaura el valor original solo al terminar el test.
        monkeypatch.setattr(main, "RUTA_DATOS", str(tmp_path / "catalogo_test.json"))
        respuestas = iter(["2", "2", "Pelicula Nueva", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        resultado = main.menu_crud(catalogo)

        assert len(resultado) == 2
        assert any(p["id"] == 2 and p["title"] == "Pelicula Nueva" for p in resultado)


class TestMostrarListadoYDetallePeliculas:
    """Helpers futuros del submenu de busqueda: el listado compacto (con id)
    y la ficha detallada de la busqueda por titulo."""

    def test_listado_muestra_titulo_anio_e_id(self, capsys):
        main._mostrar_listado_peliculas([
            {"id": 1, "title": "Toy Story", "anio": 1995, "genres": ["Comedy"]},
        ])
        assert "- Toy Story (1995) [id: 1]" in capsys.readouterr().out

    def test_listado_sin_anio_omite_el_parentesis(self, capsys):
        main._mostrar_listado_peliculas([
            {"id": 5, "title": "Sin Datos", "anio": None, "genres": []},
        ])
        assert "- Sin Datos [id: 5]" in capsys.readouterr().out

    def test_listado_vacio(self, capsys):
        main._mostrar_listado_peliculas([])
        assert "sin resultado" in capsys.readouterr().out

    def test_detalle_muestra_ficha_completa(self, catalogo_prueba, capsys):
        main._mostrar_detalle_peliculas([catalogo_prueba[0]])
        salida = capsys.readouterr().out
        assert "[1] Toy Story (1995)" in salida
        assert "Animation, Comedy, Family" in salida
        assert "John Lasseter" in salida
        assert "Juguetes con vida propia." in salida

    def test_detalle_sin_resultado(self, capsys):
        main._mostrar_detalle_peliculas([])
        assert "sin resultado" in capsys.readouterr().out


class TestMenuBusquedaFuncional:
    """menu_busqueda end-to-end contra busqueda.py real: la opcion 1 (titulo)
    muestra la ficha detallada y la opcion 2 (actor) el listado con id."""

    def test_buscar_por_titulo_muestra_detalle(self, catalogo_prueba, monkeypatch, capsys):
        respuestas = iter(["1", "toy story", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_busqueda(catalogo_prueba)

        salida = capsys.readouterr().out
        assert "[1] Toy Story (1995)" in salida
        assert "Juguetes con vida propia." in salida

    def test_buscar_por_actor_muestra_listado_con_id(self, catalogo_prueba, monkeypatch, capsys):
        respuestas = iter(["2", "tom hanks", "0"])
        monkeypatch.setattr(builtins, "input", lambda _: next(respuestas))

        main.menu_busqueda(catalogo_prueba)

        salida = capsys.readouterr().out
        assert "- Toy Story (1995) [id: 1]" in salida
        assert "- Toy Story 2 (1999) [id: 2]" in salida
