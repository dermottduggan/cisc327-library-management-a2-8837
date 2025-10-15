import pytest
from routes import (
    catalog_routes
)
from database import get_all_books, get_db_connection
from library_service import add_book_to_catalog
from flask import Blueprint, render_template
from app import create_app

app = create_app()

# valid input

def test_catalog_valid_input():
    return_test = catalog_routes.catalog()
    books = get_all_books()
    assert (return_test == render_template('catalog.html', books=books))

def test_catalog_new_book():
    add_true, response = add_book_to_catalog("New Book", "Author", "1111111111111", 1)
    return_test = catalog_routes.catalog()
    assert add_true
    assert "New Book" in return_test

    with app.app_context():
        with app.test_request_context('/catalog'):
            rendered = catalog_routes.catalog()

    assert "New Book" in rendered
    