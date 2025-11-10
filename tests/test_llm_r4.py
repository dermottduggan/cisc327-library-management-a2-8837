import pytest
from datetime import datetime
from services.library_service import return_book_by_patron, update_book_availability, update_borrow_record_return_date, calculate_late_fee_for_book
from database import get_patron_borrowed_books


# --- NORMAL CASES ---

def test_return_book_success(monkeypatch):
    """✅ Normal case: Patron successfully returns a borrowed book."""
    fake_books = [{"book_id": 1, "title": "Clean Code"}]
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: fake_books)
    monkeypatch.setattr("services.library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0})
    monkeypatch.setattr("services.library_service.update_book_availability", lambda bid, val: True)
    monkeypatch.setattr("services.library_service.update_borrow_record_return_date", lambda pid, bid, date: True)

    success, message = return_book_by_patron("123456", 1)
    assert success is True
    assert "Successfully returned" in message
    assert "Late fees: 0" in message


# --- EDGE CASES ---

def test_return_book_with_late_fee(monkeypatch):
    """⚙️ Edge case: Patron returns book late and fee is applied."""
    fake_books = [{"book_id": 5, "title": "Book Late"}]
    monkeypatch.setattr("services.library_service.get_patron_borrowed_books", lambda pid: fake_books)
    monkeypatch.setattr("services.library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 15})
    monkeypatch.setattr("services.library_service.update_book_availability", lambda bid, val: True)
    monkeypatch.setattr("services.library_service.update_borrow_record_return_date", lambda pid, bid, date: True)

    success, message = return_book_by_patron("222222", 5)
    assert success is True
    assert "Late fees: 15" in message


def test_return_book_multiple_borrowed(monkeypatch):
    """⚙️ Edge case: Patron borrowed multiple books; returns the correct one."""
    fake_books = [
        {"book_id": 1, "title": "Book A"},
        {"book_id": 2, "title": "Book B"},
    ]
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: fake_books)
    monkeypatch.setattr("services.library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0})
    monkeypatch.setattr("services.library_service.update_book_availability", lambda bid, val: True)
    monkeypatch.setattr("services.library_service.update_borrow_record_return_date", lambda pid, bid, date: True)

    success, message = return_book_by_patron("654321", 2)
    assert success is True
    assert "Successfully returned" in message


# --- INVALID CASES ---

def test_return_book_patron_not_found(monkeypatch):
    """❌ Invalid case: Patron does not exist or has no borrowed books."""
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: [])
    success, message = return_book_by_patron("000000", 1)
    assert success is False
    assert "no books borrowed" in message


def test_return_book_not_borrowed(mocker):
    """❌ Invalid case: Patron exists but did not borrow that specific book."""
    fake_books = [{"book_id": 9, "title": "Other Book"}]
    mocker.patch("services.library_service.get_patron_borrowed_books", return_value=fake_books)
    success, message = return_book_by_patron("123456", 1)
    assert success is False
    assert "Book not borrowed" in message


def test_return_book_update_failure(monkeypatch):
    """❌ Invalid case: Availability update fails during return."""
    fake_books = [{"book_id": 3, "title": "Failing Book"}]
    monkeypatch.setattr("database.get_patron_borrowed_books", lambda pid: fake_books)
    monkeypatch.setattr("services.library_service.calculate_late_fee_for_book", lambda pid, bid: {"fee_amount": 0})
    monkeypatch.setattr("services.library_service.update_book_availability", lambda bid, val: False)

    success, message = return_book_by_patron("111111", 3)
    assert success is False
    assert "not updated" in message