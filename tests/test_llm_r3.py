import pytest
from datetime import datetime, timedelta
from library_service import borrow_book_by_patron, get_book_by_id, get_patron_borrow_count
from database import get_db_connection, get_patron_borrowed_books, update_book_availability, insert_borrow_record


# --- NORMAL CASES ---

def test_borrow_book_success(monkeypatch):
    """✅ Normal case: Patron successfully borrows an available book."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: {"title": "Clean Code", "available_copies": 3})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda patron_id: 2)
    monkeypatch.setattr("database.insert_borrow_record", lambda *args: True)
    monkeypatch.setattr("database.update_book_availability", lambda *args: True)

    success, message = borrow_book_by_patron("123456", 1)
    assert success is True
    assert "Successfully borrowed" in message
    assert "Due date" in message


# --- EDGE CASES ---

def test_borrow_book_patron_at_limit(monkeypatch):
    """⚙️ Edge case: Patron has already borrowed 5 books (max limit)."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: {"title": "Book A", "available_copies": 2})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda patron_id: 5)

    success, message = borrow_book_by_patron("654321", 2)
    assert success is False
    assert "maximum borrowing limit" in message


def test_borrow_book_exactly_one_copy_left(monkeypatch):
    """⚙️ Edge case: Book has exactly 1 available copy."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: {"title": "Book B", "available_copies": 1})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda patron_id: 0)
    monkeypatch.setattr("database.insert_borrow_record", lambda *args: True)
    monkeypatch.setattr("database.update_book_availability", lambda *args: True)

    success, message = borrow_book_by_patron("111111", 3)
    assert success is True
    assert "Successfully borrowed" in message


# --- INVALID CASES ---

def test_borrow_book_invalid_patron_id(monkeypatch):
    """❌ Invalid case: Patron ID not 6 digits."""
    success, message = borrow_book_by_patron("abc12", 1)
    assert success is False
    assert "Invalid patron ID" in message


def test_borrow_book_not_available(monkeypatch):
    """❌ Invalid case: Book exists but has no available copies."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: {"title": "Unavailable Book", "available_copies": 0})

    success, message = borrow_book_by_patron("123456", 4)
    assert success is False
    assert "not available" in message


def test_borrow_book_database_failure(monkeypatch):
    """❌ Invalid case: Database error during record creation or update."""
    monkeypatch.setattr("library_service.get_book_by_id", lambda book_id: {"title": "Book X", "available_copies": 2})
    monkeypatch.setattr("library_service.get_patron_borrow_count", lambda patron_id: 1)
    monkeypatch.setattr("database.insert_borrow_record", lambda *args: False)  # Fail DB insert
    monkeypatch.setattr("database.update_book_availability", lambda *args: True)

    success, message = borrow_book_by_patron("999999", 5)
    assert success is False
    assert "Database error" in message