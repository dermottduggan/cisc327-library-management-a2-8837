import pytest
from datetime import datetime, timedelta
from services.library_service import get_patron_status_report 
from database import get_db_connection, get_all_books, get_patron_borrow_count, get_patron_borrowed_books

# --- MOCK FIXTURES ---
@pytest.fixture
def mock_functions(monkeypatch):
    """Patch DB and helper functions for patron status report tests."""
    # Default: empty patron
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: [])
    monkeypatch.setattr("database.get_patron_borrow_count", lambda pid: 0)
    
    class MockConn:
        def execute(self, query, params):
            return []
        def close(self): pass
    
    monkeypatch.setattr("database.get_db_connection", lambda: MockConn())
    monkeypatch.setattr("services.library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0})
    return monkeypatch


# --- NORMAL CASES ---

def test_patron_with_current_books(mocker):
    borrowed_books = [
        {"book_id": 1, "title": "Book A", "author": "Author A", "due_date": datetime.now() - timedelta(days=2)},
        {"book_id": 2, "title": "Book B", "author": "Author B", "due_date": datetime.now() + timedelta(days=5)},
    ]

    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=borrowed_books)
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=2)
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        side_effect=lambda pid, bid: {"fee_amount": 1.0 if bid == 1 else 0.0}
    )

    class MockCursor:
        def fetchall(self):
            return []
    class MockConn:
        def execute(self, query, params=None):
            return MockCursor()
        def close(self):
            pass
    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())

    report = get_patron_status_report("123456")
    assert report["status"] == "Success"
    assert len(report["borrowed_books"]) == 2
    assert report["total_late_fees"] == 1.0
    assert report["total_books_borrowed"] == 2


# --- EDGE CASES ---

def test_patron_no_current_books_but_has_history(mocker):
    """Edge case: Patron has no current books but has borrowing history."""
    history_records = [
        {"book_id": 3, "title": "Book C", "author": "Author C", "borrow_date": "2025-01-01T00:00:00"}
    ]

    class MockCursor:
        def fetchall(self):
            return history_records

    class MockConn:
        def execute(self, query, params=None):
            return MockCursor()
        def close(self):
            pass

    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())

    report = get_patron_status_report("222222")
    assert report["status"] == "Success"
    assert report["borrowed_books"] == []
    assert report["borrowing_history"] == history_records


def test_patron_not_found(mocker):
    """Edge case: Patron not found (no borrowed books, no history)."""
    class MockCursor:
        def fetchall(self):
            return []

    class MockConn:
        def execute(self, query, params=None):
            return MockCursor()
        def close(self):
            pass

    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())

    report = get_patron_status_report("999999")
    assert report["status"] == "Patron not found"
    assert report["borrowed_books"] == []
    assert report["total_books_borrowed"] == 0
    assert report["borrowing_history"] == []
    assert report["total_late_fees"] == 0.0


def test_patron_all_books_returned_late_fee(mocker):
    """Edge case: Patron has no current books but late fees calculated from borrowed books."""
    history_records = [
        {"book_id": 1, "title": "Book D", "author": "Author D", "borrow_date": "2025-01-01T00:00:00"}
    ]

    class MockCursor:
        def fetchall(self):
            return history_records

    class MockConn:
        def execute(self, query, params=None):
            return MockCursor()
        def close(self):
            pass

    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.calculate_late_fee_for_book", side_effect=lambda pid, bid: {"fee_amount": 5.0})
    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())

    report = get_patron_status_report("333333")
    assert report["status"] == "Success"
    assert report["borrowed_books"] == []
    assert report["total_late_fees"] == 0.0
    assert len(report["borrowing_history"]) == 1


def test_patron_invalid_id_format(mocker):
    """Invalid case: Patron ID is incorrectly formatted (non-digit)."""
    class MockCursor:
        def fetchall(self):
            return []

    class MockConn:
        def execute(self, query, params=None):
            return MockCursor()
        def close(self):
            pass

    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)
    mocker.patch("services.library_service.get_db_connection", return_value=MockConn())

    report = get_patron_status_report("abc123")
    assert report["status"] in ["Success", "Patron not found"]


def test_patron_db_error(mocker):
    """Invalid case: Database connection fails."""
    def mock_conn_fail():
        raise Exception("DB error")

    mocker.patch("services.library_service.get_db_connection", side_effect=mock_conn_fail)
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=[])
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=0)

    import pytest
    with pytest.raises(Exception) as exc:
        get_patron_status_report("123456")
    assert "DB error" in str(exc.value)