import pytest
from routes import (
    catalog_routes
)
from database import get_all_books, get_db_connection
from services.library_service import add_book_to_catalog
from flask import Blueprint, render_template
from app import create_app

app = create_app()
app.config.update({
    "SERVER_NAME": "localhost",
    "APPLICATION_ROOT": "/",
    "PREFERRED_URL_SCHEME": "http",
})

# valid input

def test_catalog_valid_input(mocker):
    mocker.patch("database.get_all_books", return_value=[
        {
            "title": "Test Book",
            "author": "Author",
            "isbn": "1234567890123",
            "total_copies": 3,
            "available_copies": 3
        }
    ])
    with app.app_context():
        with app.test_request_context("/catalog"):
            return_test = catalog_routes.catalog()

            expected = render_template(
                "catalog.html",
                books=get_all_books()
            )

    assert return_test == expected

def test_catalog_new_book(mocker):
    mocker.patch("services.library_service.get_book_by_isbn", return_value=None)
    mocker.patch("services.library_service.insert_book", return_value=True)

    add_true, response = add_book_to_catalog("New Book", "Author", "1111111111111", 1)
    assert add_true
    assert "New Book" in response

    mocker.patch("database.get_all_books", return_value=[
        {
            "title": "New Book",
            "author": "Author",
            "isbn": "1111111111111",
            "total_copies": 1,
            "available_copies": 1
        }
    ])
    with app.app_context():
        with app.test_request_context('/catalog'):
            rendered = catalog_routes.catalog()

    assert "New Book" in rendered
    