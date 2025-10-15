import pytest
from flask import Flask, render_template
from routes import catalog_bp
from database import get_all_books
from library_service import add_book_to_catalog

@pytest.fixture
def client(monkeypatch):
    """Fixture: Create a Flask test client with catalog blueprint registered."""
    app = Flask(__name__)
    app.secret_key = "test"
    app.register_blueprint(catalog_bp)
    return app.test_client()


# --- NORMAL CASES ---

def test_catalog_display_with_books(monkeypatch, client):
    """✅ Normal case: Catalog page shows books when database has entries."""
    fake_books = [
        {"id": 1, "title": "Book A", "author": "Author A", "isbn": "1234567890123", "available_copies": 2, "total_copies": 3},
        {"id": 2, "title": "Book B", "author": "Author B", "isbn": "9876543210987", "available_copies": 1, "total_copies": 1},
    ]
    monkeypatch.setattr("database.get_all_books", lambda: fake_books)

    response = client.get("/catalog")
    assert response.status_code == 200
    assert b"Book A" in response.data
    assert b"Book B" in response.data


def test_homepage_redirects_to_catalog(client):
    """✅ Normal case: Root URL redirects to /catalog."""
    response = client.get("/")
    assert response.status_code == 302  # Redirect
    assert "/catalog" in response.location


# --- EDGE CASES ---

def test_catalog_display_empty_list(monkeypatch, client):
    """⚙️ Edge case: Catalog displays message when no books exist."""
    monkeypatch.setattr("database.get_all_books", lambda: [])

    response = client.get("/catalog")
    assert response.status_code == 200
    # Check that some placeholder or table still renders
    assert b"No books" in response.data or b"catalog" in response.data


def test_catalog_book_with_zero_available(monkeypatch, client):
    """⚙️ Edge case: Book with 0 available copies should not show 'Borrow' button."""
    fake_books = [
        {"id": 1, "title": "Book C", "author": "Author C", "isbn": "1234567890123", "available_copies": 0, "total_copies": 3}
    ]
    monkeypatch.setattr("database.get_all_books", lambda: fake_books)

    response = client.get("/catalog")
    assert response.status_code == 200
    assert b"Book C" in response.data
    assert b"Borrow" not in response.data


# --- INVALID / ERROR CASES ---

def test_catalog_db_failure(monkeypatch, client):
    """❌ Invalid case: Database failure when fetching books should return 500."""
    def fake_get_all_books():
        raise Exception("DB connection failed")

    monkeypatch.setattr("database.get_all_books", fake_get_all_books)

    response = client.get("/catalog")
    # Flask by default will return a 500 error for unhandled exceptions
    assert response.status_code == 500


def test_catalog_template_render(monkeypatch, client):
    """❌ Invalid case: Template rendering failure should be handled."""
    
    # Patch the database call
    import database
    monkeypatch.setattr(database, "get_all_books", lambda: [
        {"id": 1, "title": "Book X", "author": "A", "isbn": "1111111111111", "available_copies": 1, "total_copies": 1}
    ])
    
    # Patch render_template where it is used
    from routes import catalog as routes
    from flask import render_template as original_render_template
    
    def fail_render(*args, **kwargs):
        raise Exception("Render fail")
    
    monkeypatch.setattr(routes.catalog, "render_template", fail_render)

    # Make request
    response = client.get("/catalog")
    assert response.status_code == 500