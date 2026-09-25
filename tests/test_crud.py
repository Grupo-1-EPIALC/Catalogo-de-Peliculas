"""
Tests de crud.py.

crud.py ya fue implementado (rama feature/implementacion-crud), pero esa rama
todavia no esta mergeada a develop, asi que el crud.py de este working tree
puede seguir siendo el stub original (`pass # TODO: implementar`). Estos
tests se saltean automaticamente en ese caso (ver `_crud_implementado`) y
corren solos apenas se mergee la implementacion real, sin tocar nada aca.
"""

import json

import pytest

import crud


def _crud_implementado() -> bool:
    # con una ruta que no existe, la implementacion real devuelve [] (y
    # avisa por consola); el stub (pass) devuelve None
    return crud.cargar_catalogo("__archivo_que_no_existe_para_test__.json") is not None


pytestmark = pytest.mark.skipif(
    not _crud_implementado(),
    reason="crud.py todavia es un stub local (falta mergear feature/implementacion-crud)",
)


class TestCargarCatalogo:
    def test_archivo_inexistente_devuelve_lista_vacia(self):
        assert crud.cargar_catalogo("__archivo_que_no_existe_para_test__.json") == []

    def test_json_mal_formado_devuelve_lista_vacia(self, tmp_path):
        archivo = tmp_path / "corrupto.json"
        archivo.write_text("{ esto no es json valido ", encoding="utf-8")
        assert crud.cargar_catalogo(str(archivo)) == []

    def test_carga_un_catalogo_valido(self, tmp_path, catalogo_prueba):
        archivo = tmp_path / "catalogo.json"
        archivo.write_text(json.dumps(catalogo_prueba), encoding="utf-8")
        assert crud.cargar_catalogo(str(archivo)) == catalogo_prueba


class TestGuardarCatalogo:
    def test_guarda_y_se_puede_releer(self, tmp_path, catalogo_prueba):
        archivo = tmp_path / "salida.json"
        crud.guardar_catalogo(catalogo_prueba, str(archivo))
        with open(archivo, encoding="utf-8") as f:
            releido = json.load(f)
        assert releido == catalogo_prueba


class TestObtenerPeliculaPorId:
    def test_encuentra_la_pelicula(self, catalogo_prueba):
        pelicula = crud.obtener_pelicula_por_id(catalogo_prueba, 3)
        assert pelicula is not None
        assert pelicula["title"] == "Amelie"

    def test_id_inexistente_devuelve_none(self, catalogo_prueba):
        assert crud.obtener_pelicula_por_id(catalogo_prueba, 9999) is None


class TestCrearPelicula:
    def test_agrega_la_pelicula(self, catalogo_prueba):
        nueva = {"id": 100, "title": "Nueva Pelicula"}
        resultado = crud.crear_pelicula(catalogo_prueba, nueva)
        assert nueva in resultado
        assert len(resultado) == len(catalogo_prueba)  # catalogo_prueba fue mutado in place

    def test_id_duplicado_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.crear_pelicula(catalogo_prueba, {"id": 1, "title": "Duplicada"})

    def test_sin_id_o_title_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.crear_pelicula(catalogo_prueba, {"title": "Sin id"})
        with pytest.raises(ValueError):
            crud.crear_pelicula(catalogo_prueba, {"id": 200})


class TestActualizarPelicula:
    def test_modifica_los_campos_indicados(self, catalogo_prueba):
        crud.actualizar_pelicula(catalogo_prueba, 1, {"vote_average": 9.9, "tagline": "Nuevo"})
        pelicula = crud.obtener_pelicula_por_id(catalogo_prueba, 1)
        assert pelicula["vote_average"] == 9.9
        assert pelicula["tagline"] == "Nuevo"

    def test_id_inexistente_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.actualizar_pelicula(catalogo_prueba, 9999, {"title": "X"})


class TestEliminarPelicula:
    def test_elimina_la_pelicula(self, catalogo_prueba):
        crud.eliminar_pelicula(catalogo_prueba, 1)
        assert crud.obtener_pelicula_por_id(catalogo_prueba, 1) is None

    def test_id_inexistente_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.eliminar_pelicula(catalogo_prueba, 9999)


class TestListasDeCampo:
    def test_agregar_valor_a_lista(self, catalogo_prueba):
        crud.agregar_valor_a_lista(catalogo_prueba, 1, "genres", "Adventure")
        pelicula = crud.obtener_pelicula_por_id(catalogo_prueba, 1)
        assert "Adventure" in pelicula["genres"]

    def test_quitar_valor_de_lista(self, catalogo_prueba):
        crud.quitar_valor_de_lista(catalogo_prueba, 1, "genres", "Comedy")
        pelicula = crud.obtener_pelicula_por_id(catalogo_prueba, 1)
        assert "Comedy" not in pelicula["genres"]

    def test_campo_invalido_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.agregar_valor_a_lista(catalogo_prueba, 1, "title", "no es una lista")

    def test_quitar_valor_no_presente_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.quitar_valor_de_lista(catalogo_prueba, 1, "genres", "GeneroQueNoTiene")

    def test_id_inexistente_lanza_value_error(self, catalogo_prueba):
        with pytest.raises(ValueError):
            crud.agregar_valor_a_lista(catalogo_prueba, 9999, "genres", "Drama")
