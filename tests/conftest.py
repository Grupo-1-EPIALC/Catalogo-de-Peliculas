"""
conftest.py

Fixtures compartidas por los tests de todo el proyecto. `catalogo_prueba` es
un catalogo chico (5 peliculas) pero variado: distintos generos, directores,
actores, paises, idiomas y keywords, mas una pelicula con casi todos los
campos en None/vacio para forzar el manejo de datos faltantes. Se usa en los
tests de crud, busqueda, rankings y main.

`estadisticas.py` y `recomendaciones.py` usan sus propios catalogos de
prueba mas chicos (con valores elegidos a mano para verificar promedios
exactos), definidos en sus propios archivos de test.
"""

import pytest


@pytest.fixture
def catalogo_prueba() -> list[dict]:
    return [
        {
            "id": 1, "title": "Toy Story", "original_title": "Toy Story",
            "overview": "Juguetes con vida propia.", "tagline": None, "status": "Released",
            "release_date": "1995-10-30", "runtime": 81.0, "budget": "30000000",
            "revenue": 373554033.0, "popularity": "21.9",
            "vote_average": 7.7, "vote_count": 5415.0, "original_language": "en",
            "collection": "Toy Story Collection",
            "genres": ["Animation", "Comedy", "Family"],
            "production_companies": ["Pixar"],
            "production_countries": ["United States of America"],
            "spoken_languages": ["English"],
            "cast": ["Tom Hanks", "Tim Allen"],
            "directors": ["John Lasseter"],
            "keywords": ["toy", "friendship"],
        },
        {
            "id": 2, "title": "Toy Story 2", "original_title": "Toy Story 2",
            "overview": "Secuela de Toy Story.", "tagline": None, "status": "Released",
            "release_date": "1999-11-24", "runtime": 92.0, "budget": "90000000",
            "revenue": 497375942.0, "popularity": "15.3",
            "vote_average": 7.3, "vote_count": 3914.0, "original_language": "en",
            "collection": "Toy Story Collection",
            "genres": ["Animation", "Comedy", "Family"],
            "production_companies": ["Pixar"],
            "production_countries": ["United States of America"],
            "spoken_languages": ["English"],
            "cast": ["Tom Hanks", "Tim Allen"],
            "directors": ["John Lasseter"],
            "keywords": ["toy", "rescue"],
        },
        {
            "id": 3, "title": "Amelie", "original_title": "Le Fabuleux Destin d'Amelie Poulain",
            "overview": "Una joven parisina.", "tagline": None, "status": "Released",
            "release_date": "2001-04-25", "runtime": 122.0, "budget": "10000000",
            "revenue": 173921954.0, "popularity": "12.8",
            "vote_average": 7.8, "vote_count": 3310.0, "original_language": "fr",
            "collection": None,
            "genres": ["Comedy", "Romance"],
            "production_companies": ["UGC"],
            "production_countries": ["France"],
            "spoken_languages": ["French"],
            "cast": ["Audrey Tautou"],
            "directors": ["Jean-Pierre Jeunet"],
            "keywords": ["paris", "romance"],
        },
        {
            "id": 4, "title": "Seven Samurai", "original_title": "Shichinin no Samurai",
            "overview": "Aldeanos contratan samuráis.", "tagline": None, "status": "Released",
            "release_date": "1954-04-26", "runtime": 207.0, "budget": None,
            "revenue": None, "popularity": "9.1",
            "vote_average": 8.6, "vote_count": 1200.0, "original_language": "ja",
            "collection": None,
            "genres": ["Drama", "Action"],
            "production_companies": ["Toho"],
            "production_countries": ["Japan"],
            "spoken_languages": ["Japanese"],
            "cast": ["Toshiro Mifune"],
            "directors": ["Akira Kurosawa"],
            "keywords": ["samurai", "village"],
        },
        {
            "id": 5, "title": "Sin Datos", "original_title": "Sin Datos",
            "overview": None, "tagline": None, "status": "Released",
            "release_date": None, "runtime": None, "budget": None,
            "revenue": None, "popularity": None,
            "vote_average": None, "vote_count": None, "original_language": "en",
            "collection": None,
            "genres": [], "production_companies": [], "production_countries": [],
            "spoken_languages": [], "cast": [], "directors": [], "keywords": [],
        },
    ]
