import pytest
from flask import Flask, redirect, url_for
from routes.catalog_routes import catalog_bp
import routes.catalog_routes as catalog_module

# --- FIXTURE ---

@pytest.fixture
def client():
    """Create Flask test client with catalog blueprint."""
    app = Flask(__name__)
    app.secret_key = "test"
    app.register_blueprint(catalog_bp)
    return app.test_client()


# --- NORMAL CASES ---

def test_homepage_redirects_to_catalog(client):
    """✅ Root URL redirects to /catalog."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/catalog" in response.location


def test_catalog_display_with_books(monkeypatch, client):
    """✅ Catalog shows books when database has entries."""
    fake_books = [
        {"id": 1, "title": "Book A", "author": "Author A", "isbn": "1234567890123",
         "available_copies": 2, "total_copies": 3},
        {"id": 2, "title": "Book B", "author": "Author B", "isbn": "9876543210987",
         "available_copies": 1, "total_copies": 1},
    ]

    captured = {}

    def fake_render(template, **kwargs):
        captured["template"] = template
        captured["kwargs"] = kwargs
        return "OK"

    monkeypatch.setattr(catalog_module, "get_all_books", lambda: fake_books)
    monkeypatch.setattr(catalog_module, "render_template", fake_render)

    response = client.get("/catalog")
    assert response.status_code == 200
    assert captured["kwargs"]["books"] == fake_books


# --- EDGE CASES ---

def test_catalog_display_empty_list(monkeypatch, client):
    """⚙️ Catalog displays message when no books exist."""
    captured = {}

    def fake_render(template, **kwargs):
        captured["template"] = template
        captured["kwargs"] = kwargs
        return "OK"

    monkeypatch.setattr(catalog_module, "get_all_books", lambda: [])
    monkeypatch.setattr(catalog_module, "render_template", fake_render)

    response = client.get("/catalog")
    assert response.status_code == 200
    assert captured["kwargs"]["books"] == []


def test_catalog_book_with_zero_available(monkeypatch, client):
    """⚙️ Book with 0 available copies should be passed to template correctly."""
    fake_books = [
        {"id": 1, "title": "Book C", "author": "Author C", "isbn": "1234567890123",
         "available_copies": 0, "total_copies": 3}
    ]

    captured = {}

    def fake_render(template, **kwargs):
        captured["template"] = template
        captured["kwargs"] = kwargs
        return "OK"

    monkeypatch.setattr(catalog_module, "get_all_books", lambda: fake_books)
    monkeypatch.setattr(catalog_module, "render_template", fake_render)

    response = client.get("/catalog")
    assert response.status_code == 200
    assert captured["kwargs"]["books"] == fake_books


# --- ERROR CASES ---

def test_catalog_db_failure(monkeypatch, client):
    """❌ Database failure should return 500."""
    monkeypatch.setattr(catalog_module, "get_all_books", lambda: (_ for _ in ()).throw(Exception("DB fail")))
    monkeypatch.setattr(catalog_module, "render_template", lambda template, **kwargs: "OK")

    response = client.get("/catalog")
    # The route catches exceptions and returns 500
    assert response.status_code == 500


def test_catalog_template_render_failure(monkeypatch, client):
    """❌ Template rendering failure should return 500."""
    monkeypatch.setattr(catalog_module, "get_all_books", lambda: [{"id": 1, "title": "Book X"}])
    monkeypatch.setattr(catalog_module, "render_template", lambda *a, **kw: (_ for _ in ()).throw(Exception("Render fail")))

    response = client.get("/catalog")
    assert response.status_code == 500