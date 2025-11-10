import pytest
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book
from database import get_db_connection, get_all_books, get_patron_borrow_count, get_patron_borrowed_books

@pytest.fixture
def mock_get_patron_borrowed_books(monkeypatch):
    def _mock(data):
        def mock_function(patron_id):
            return data.get(patron_id, [])
        monkeypatch.setattr("services.library_service.get_patron_borrowed_books", mock_function)
    return _mock

def patch_get_books(mocker):
    return mocker.patch("services.library_service.get_patron_borrowed_books")

def days_ago(days):
    return datetime.combine(datetime.now().date() - timedelta(days=days) + timedelta(days=1), datetime.min.time())


def days_from_now(days):
    return datetime.combine(datetime.now().date() + timedelta(days=days), datetime.min.time())


def test_no_books_found(mock_get_patron_borrowed_books):
    mock_get_patron_borrowed_books({})
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.00
    assert result["status"] == "Patron not found or book not found"


def test_not_overdue(mocker):
    due_date = days_from_now(1)
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": 1, "due_date": due_date}]
    )
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.00
    assert result["days_overdue"] == 0


def test_one_day_overdue(mocker):
    due_date = days_ago(1)
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": 1, "due_date": due_date}]
    )
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 0.50
    assert result["days_overdue"] == 1

def test_seven_days_overdue(mocker):
    due_date = days_ago(7)
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": 1, "due_date": due_date}]
    )
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 3.50
    assert result["days_overdue"] == 7

def test_ten_days_overdue(mocker):
    due_date = days_ago(10)
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": 1, "due_date": due_date}]
    )
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 6.50
    assert result["days_overdue"] == 10

def test_fee_capped_at_15(mocker):
    due_date = days_ago(30)
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": 1, "due_date": due_date}]
    )
    result = calculate_late_fee_for_book("123456", 1)
    assert result["fee_amount"] == 15.00
    assert result["days_overdue"] == 30