import pytest
from datetime import datetime, timedelta
from library_service import calculate_late_fee_for_book
from database import get_db_connection, get_all_books, get_patron_borrow_count, get_patron_borrowed_books

@pytest.fixture
def mock_get_patron_borrowed_books(monkeypatch):
    def _mock(data):
        def mock_function(patron_id):
            return data.get(patron_id, [])
        monkeypatch.setattr("database.get_patron_borrowed_books", mock_function)
    return _mock


def test_no_books_found(mock_get_patron_borrowed_books):
    mock_get_patron_borrowed_books({})
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.00
    assert result["status"] == "Patron not found or book not found"


def test_not_overdue(mock_get_patron_borrowed_books):
    due_date = datetime.now() + timedelta(days=1)
    mock_get_patron_borrowed_books({
        "123456": [{"book_id": 1, "due_date": due_date}]
    })
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


def test_one_day_overdue(mock_get_patron_borrowed_books):
    due_date = datetime.now() - timedelta(days=1)
    mock_get_patron_borrowed_books({
        "123456": [{"book_id": 1, "due_date": due_date}]
    })
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.50
    assert result["days_overdue"] == 1


def test_seven_days_overdue(mock_get_patron_borrowed_books):
    due_date = datetime.now() - timedelta(days=7)
    mock_get_patron_borrowed_books({
        "123456": [{"book_id": 1, "due_date": due_date}]
    })
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 3.50  # 7 * $0.50


def test_ten_days_overdue(mock_get_patron_borrowed_books):
    due_date = datetime.now() - timedelta(days=10)
    mock_get_patron_borrowed_books({
        "123456": [{"book_id": 1, "due_date": due_date}]
    })
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 6.50  # 7*0.50 + 3*1.00


def test_fee_capped_at_15(mock_get_patron_borrowed_books):
    due_date = datetime.now() - timedelta(days=30)
    mock_get_patron_borrowed_books({
        "123456": [{"book_id": 1, "due_date": due_date}]
    })
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 15.00