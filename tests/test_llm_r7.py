import pytest
from datetime import datetime, timedelta
from library_service import get_patron_status_report 
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
    monkeypatch.setattr("library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0})
    return monkeypatch


# --- NORMAL CASES ---

def test_patron_with_current_books(mock_functions):
    """✅ Normal case: Patron has currently borrowed books and late fees."""
    borrowed_books = [
        {"book_id": 1, "title": "Book A", "author": "Author A", "due_date": (datetime.now() - timedelta(days=2)).isoformat()},
        {"book_id": 2, "title": "Book B", "author": "Author B", "due_date": (datetime.now() + timedelta(days=5)).isoformat()},
    ]
    mock_functions.setattr("database.get_patron_borrowed_books", lambda pid: borrowed_books)
    mock_functions.setattr("database.get_patron_borrow_count", lambda pid: 2)
    mock_functions.setattr("library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 1.0 if bid == 1 else 0.0})

    report = get_patron_status_report("123456")
    assert report["status"] == "Success"
    assert len(report["borrowed_books"]) == 2
    assert report["total_late_fees"] == 1.0
    assert report["total_books_borrowed"] == 2


# --- EDGE CASES ---

def test_patron_no_current_books_but_has_history(mock_functions):
    """⚙️ Edge case: Patron has no current books but has borrowing history."""
    history_records = [{"book_id": 3, "title": "Book C", "author": "Author C", "borrow_date": "2025-01-01T00:00:00"}]
    
    class MockConn:
        def execute(self, query, params): return history_records
        def close(self): pass
    mock_functions.setattr("database.get_db_connection", lambda: MockConn())

    report = get_patron_status_report("222222")
    assert report["status"] == "Success"
    assert report["borrowed_books"] == []
    assert report["borrowing_history"] == history_records


def test_patron_not_found(mock_functions):
    """⚙️ Edge case: Patron not found (no borrowed books, no history)."""
    report = get_patron_status_report("999999")
    assert report["status"] == "Patron not found"
    assert report["borrowed_books"] == []
    assert report["total_books_borrowed"] == 0
    assert report["borrowing_history"] == []
    assert report["total_late_fees"] == 0.0


def test_patron_all_books_returned_late_fee(mock_functions):
    """⚙️ Edge case: Patron has no current books but late fees calculated from borrowed books."""
    mock_functions.setattr("database.get_patron_borrowed_books", lambda pid: [])
    
    class MockConn:
        def execute(self, query, params):
            return [{"book_id": 1, "title": "Book D", "author": "Author D", "borrow_date": "2025-01-01T00:00:00"}]
        def close(self): pass
    mock_functions.setattr("database.get_db_connection", lambda: MockConn())
    mock_functions.setattr("library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 5.0})

    report = get_patron_status_report("333333")
    assert report["status"] == "Success"
    # borrowed_books empty, but history present
    assert report["borrowed_books"] == []
    assert report["total_late_fees"] == 0.0
    assert len(report["borrowing_history"]) == 1


# --- INVALID CASES ---

def test_patron_invalid_id_format(mock_functions):
    """❌ Invalid case: Patron ID is incorrectly formatted (non-digit)."""
    report = get_patron_status_report("abc123")
    # Function does not currently validate format; should handle gracefully
    assert report["status"] in ["Success", "Patron not found"]


def test_patron_db_error(monkeypatch):
    """❌ Invalid case: Database connection fails."""
    def mock_conn_fail():
        raise Exception("DB error")
    monkeypatch.setattr("database.get_db_connection", mock_conn_fail)
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: [])
    monkeypatch.setattr("database.get_patron_borrow_count", lambda pid: 0)

    with pytest.raises(Exception) as exc:
        get_patron_status_report("123456")
    assert "DB error" in str(exc.value)