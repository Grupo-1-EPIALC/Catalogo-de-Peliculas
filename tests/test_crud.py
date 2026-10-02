"""
Tests de crud.py.

crud.py es autosuficiente: sus funciones no reciben el catalogo, sino que leen
y guardan el JSON en `ruta_json`. Por eso cada test escribe `catalogo_prueba`
en un archivo temporal (fixture `ruta_catalogo`) y le pasa esa ruta, asi nunca
se toca el dataset real de `data/`.
"""

import json

import pytest

import crud


@pytest.fixture
def ruta_catalogo(tmp_path, catalogo_prueba) -> str:
    archivo = tmp_path / "catalogo.json"
    archivo.write_text(json.dumps(catalogo_prueba), encoding="utf-8")
    return str(archivo)


class TestCargarCatalogo:
    def test_archivo_inexistente_devuelve_lista_vacia(self):
        assert crud.cargar_catalogo("__archivo_que_no_existe_para_test__.json") == []

    def test_json_mal_formado_devuelve_lista_vacia(self, tmp_path):
        archivo = tmp_path / "corrupto.json"
        archivo.write_text("{ esto no es json valido ", encoding="utf-8")
        assert crud.cargar_catalogo(str(archivo)) == []

    def test_carga_un_catalogo_valido(self, ruta_catalogo, catalogo_prueba):
        assert crud.cargar_catalogo(ruta_catalogo) == catalogo_prueba


class TestGuardarCatalogo:
    def test_guarda_y_se_puede_releer(self, tmp_path, catalogo_prueba):
        archivo = tmp_path / "salida.json"
        crud.guardar_catalogo(catalogo_prueba, str(archivo))
        with open(archivo, encoding="utf-8") as f:
            releido = json.load(f)
        assert releido == catalogo_prueba


class TestObtenerPeliculaPorId:
    def test_encuentra_la_pelicula(self, ruta_catalogo):
        pelicula = crud.obtener_pelicula_por_id(3, ruta_catalogo)
        assert pelicula is not None
        assert pelicula["title"] == "Amelie"

    def test_id_inexistente_devuelve_none(self, ruta_catalogo):
        assert crud.obtener_pelicula_por_id(9999, ruta_catalogo) is None


class TestObtenerIdPorTitulo:
    def test_encuentra_el_id_sin_importar_mayusculas(self, ruta_catalogo):
        assert crud.obtener_id_por_titulo("  toy STORY 2 ", ruta_catalogo) == 2

    def test_titulo_inexistente_devuelve_none(self, ruta_catalogo):
        assert crud.obtener_id_por_titulo("Pelicula Que No Existe", ruta_catalogo) is None


class TestCrearPelicula:
    def test_agrega_la_pelicula_y_la_persiste(self, ruta_catalogo, catalogo_prueba):
        nueva = {"id": 100, "title": "Nueva Pelicula"}
        resultado = crud.crear_pelicula(nueva, ruta_catalogo)
        assert nueva in resultado
        assert len(resultado) == len(catalogo_prueba) + 1
        assert crud.obtener_pelicula_por_id(100, ruta_catalogo) == nueva

    def test_id_duplicado_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.crear_pelicula({"id": 1, "title": "Duplicada"}, ruta_catalogo)

    def test_sin_id_o_title_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.crear_pelicula({"title": "Sin id"}, ruta_catalogo)
        with pytest.raises(ValueError):
            crud.crear_pelicula({"id": 200}, ruta_catalogo)

    def test_no_dict_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.crear_pelicula(["no", "es", "dict"], ruta_catalogo)


class TestActualizarPelicula:
    def test_modifica_un_campo_simple_por_nombre_y_valor(self, ruta_catalogo):
        crud.actualizar_pelicula(1, "vote_average", 9.9, ruta_json=ruta_catalogo)
        assert crud.obtener_pelicula_por_id(1, ruta_catalogo)["vote_average"] == 9.9

    def test_modifica_un_campo_simple_por_dict(self, ruta_catalogo):
        crud.actualizar_pelicula(1, {"tagline": "Nuevo"}, ruta_json=ruta_catalogo)
        assert crud.obtener_pelicula_por_id(1, ruta_catalogo)["tagline"] == "Nuevo"

    def test_id_inexistente_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.actualizar_pelicula(9999, "title", "X", ruta_json=ruta_catalogo)

    def test_campo_lista_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.actualizar_pelicula(1, "genres", "Drama", ruta_json=ruta_catalogo)

    def test_valor_vacio_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.actualizar_pelicula(1, "tagline", "   ", ruta_json=ruta_catalogo)


class TestEliminarPelicula:
    def test_elimina_la_pelicula(self, ruta_catalogo):
        crud.eliminar_pelicula(1, ruta_catalogo)
        assert crud.obtener_pelicula_por_id(1, ruta_catalogo) is None

    def test_id_inexistente_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.eliminar_pelicula(9999, ruta_catalogo)


class TestListasDeCampo:
    def test_agregar_valor_a_lista(self, ruta_catalogo):
        crud.agregar_valor_a_lista(1, "genres", "Adventure", ruta_catalogo)
        assert "Adventure" in crud.obtener_pelicula_por_id(1, ruta_catalogo)["genres"]

    def test_agregar_a_lista_inexistente_la_crea(self, ruta_catalogo):
        crud.agregar_valor_a_lista(1, "premios", "Oscar", ruta_catalogo)
        assert crud.obtener_pelicula_por_id(1, ruta_catalogo)["premios"] == ["Oscar"]

    def test_quitar_valor_de_lista(self, ruta_catalogo):
        crud.quitar_valor_de_lista(1, "genres", "Comedy", ruta_catalogo)
        assert "Comedy" not in crud.obtener_pelicula_por_id(1, ruta_catalogo)["genres"]

    def test_campo_simple_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.agregar_valor_a_lista(1, "title", "no es una lista", ruta_catalogo)

    def test_quitar_valor_no_presente_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.quitar_valor_de_lista(1, "genres", "GeneroQueNoTiene", ruta_catalogo)

    def test_id_inexistente_lanza_value_error(self, ruta_catalogo):
        with pytest.raises(ValueError):
            crud.agregar_valor_a_lista(9999, "genres", "Drama", ruta_catalogo)
