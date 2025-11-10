import pytest
from services import library_service

# --- FIXTURE TO MOCK DATABASE CONNECTION ---
@pytest.fixture
def mock_db(mocker):
    """
    Fixture to mock the database connection and allow injecting test data.
    Returns the list to which tests can append books.
    """
    test_data = []

    class MockCursor:
        def __init__(self, rows):
            self.rows = rows

        def fetchall(self):
            return self.rows

    class MockConn:
        def execute(self, query, params):
            # Case-insensitive search simulation
            search = params[0].strip("%").lower()
            if "title" in query.lower():
                results = [b for b in test_data if search in b.get("title", "").lower()]
            elif "author" in query.lower():
                results = [b for b in test_data if search in b.get("author", "").lower()]
            else:
                results = []
            return MockCursor(results)

        def close(self):
            pass

    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())
    return test_data


# --- TESTS FOR TITLE SEARCH ---
def test_search_by_title_case_insensitive(mock_db):
    mock_db.extend([
        {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald"},
        {"id": 2, "title": "Great Expectations", "author": "Charles Dickens"},
        {"id": 3, "title": "Moby Dick", "author": "Melville"}
    ])
    result = library_service.search_books_in_catalog("great", "title")
    assert len(result) == 2
    assert all("great" in book["title"].lower() for book in result)


def test_search_title_no_match(mock_db):
    mock_db.extend([
        {"id": 1, "title": "Moby Dick", "author": "Melville"}
    ])
    result = library_service.search_books_in_catalog("gatsby", "title")
    assert result == []


# --- TESTS FOR AUTHOR SEARCH ---
def test_search_by_author_case_insensitive(mock_db):
    mock_db.extend([
        {"id": 1, "title": "Hamlet", "author": "William Shakespeare"},
        {"id": 2, "title": "Othello", "author": "William Shakespeare"}
    ])
    result = library_service.search_books_in_catalog("shakespeare", "author")
    assert len(result) == 2
    assert all("shakespeare" in book["author"].lower() for book in result)


def test_search_author_no_match(mock_db):
    mock_db.extend([
        {"id": 1, "title": "Pride and Prejudice", "author": "Austen"}
    ])
    result = library_service.search_books_in_catalog("tolkien", "author")
    assert result == []


# --- TESTS FOR ISBN SEARCH ---
def test_search_by_isbn_exact(mocker):
    mocker.patch(
        "services.library_service.get_book_by_isbn",
        return_value={"id": 1, "title": "1984", "author": "George Orwell", "isbn": "1234567890"}
    )
    result = library_service.search_books_in_catalog("1234567890", "isbn")
    assert len(result) == 1
    assert result[0]["title"] == "1984"


def test_search_isbn_no_match(mocker):
    mocker.patch(
        "services.library_service.get_book_by_isbn",
        return_value=None
    )
    result = library_service.search_books_in_catalog("9999999999", "isbn")
    assert result == []


# --- TEST INVALID SEARCH TYPE ---
def test_search_invalid_type_returns_empty(mocker):
    mocker.patch("services.library_service.get_db_connection", return_value=None)
    result = library_service.search_books_in_catalog("anything", "unknown_type")
    assert result == []