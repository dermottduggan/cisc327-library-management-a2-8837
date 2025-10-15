import pytest
from library_service import search_books_in_catalog
from database import get_db_connection, get_all_books, get_patron_borrow_count, get_patron_borrowed_books, get_book_by_isbn


@pytest.fixture
def mock_db(monkeypatch):
    """Utility fixture to mock DB and helper functions for search tests."""
    class MockConn:
        def __init__(self, data):
            self.data = data
        def execute(self, query, params):
            search = params[0].strip("%").lower()
            # Simulate LIKE matching for title/author
            if "title" in query:
                return MockCursor([b for b in self.data if search in b["title"].lower()])
            elif "author" in query:
                return MockCursor([b for b in self.data if search in b["author"].lower()])
            return MockCursor([])
        def close(self): pass

    class MockCursor:
        def __init__(self, rows): self.rows = rows
        def fetchall(self): return self.rows

    def _mock_conn(data):
        def mock_function():
            return MockConn(data)
        monkeypatch.setattr("database.get_db_connection", mock_function)
    return _mock_conn


def test_search_by_title_case_insensitive(mock_db):
    data = [
        {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
        {"id": 2, "title": "Great Expectations", "author": "Charles Dickens"}
    ]
    mock_db(data)
    result = search_books_in_catalog("great", "title")
    assert len(result) == 2
    assert all("great" in book["title"].lower() for book in result)


def test_search_by_author_case_insensitive(mock_db):
    data = [
        {"id": 1, "title": "Hamlet", "author": "William Shakespeare"},
        {"id": 2, "title": "Othello", "author": "William Shakespeare"},
    ]
    mock_db(data)
    result = search_books_in_catalog("shakespeare", "author")
    assert len(result) == 2


def test_search_by_isbn_exact(monkeypatch):
    # Mock helper
    def mock_get_book_by_isbn(isbn):
        if isbn == "1234567890":
            return {"id": 1, "title": "1984", "author": "George Orwell", "isbn": isbn}
        return None
    monkeypatch.setattr("database.get_book_by_isbn", mock_get_book_by_isbn)
    result = search_books_in_catalog("1234567890", "isbn")
    assert len(result) == 1
    assert result[0]["title"] == "1984"


def test_search_title_no_match(mock_db):
    mock_db([{"id": 1, "title": "Moby Dick", "author": "Melville"}])
    result = search_books_in_catalog("gatsby", "title")
    assert result == []


def test_search_author_no_match(mock_db):
    mock_db([{"id": 1, "title": "Pride and Prejudice", "author": "Austen"}])
    result = search_books_in_catalog("tolkien", "author")
    assert result == []


def test_search_invalid_type_returns_empty(monkeypatch):
    monkeypatch.setattr("database.get_db_connection", lambda: None)
    result = search_books_in_catalog("anything", "unknown_type")
    assert result == []