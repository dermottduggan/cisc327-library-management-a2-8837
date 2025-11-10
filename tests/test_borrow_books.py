# borrow_book_by_patron - non-digit patron id, patron id too long, book does not exist, book with 0 copies available, valid inputs

import pytest
from services.library_service import (
    borrow_book_by_patron
)


def test_borrow_book_non_digit_patron_id():
    """Test borrowing a book with non-digit patron id."""
    success, message = borrow_book_by_patron("Test fail", "1")
    
    assert success == False
    assert "invalid patron" in message.lower()

def test_borrow_book_patron_id_too_long():
    """Test borrowing a book with patron id too long."""
    success, message = borrow_book_by_patron("1234567", "1")
    
    assert success == False
    assert "invalid patron" in message.lower()

def test_borrow_book_book_dne():
    """Test borrowing a book that doesn't exist"""
    success, message = borrow_book_by_patron("123456", "999")
    
    assert success == False
    assert "book not found" in message.lower()

def test_borrow_book_book_not_available():
    """Test borrowing a book that is not available"""
    success, message = borrow_book_by_patron("123456", "3")
    
    assert success == False
    assert "currently not available" in message.lower()


def test_borrow_book_valid_input(mocker):
    """Test borrowing a book with valid input."""
    mocker.patch("services.library_service.get_db_connection", autospec=True)
    mocker.patch("services.library_service.get_patron_borrow_count", return_value=2)
    mocker.patch("services.library_service.get_book_by_id", return_value={
        "book_id": 12, "title": "Test Book", "author": "Test Author", "available_copies": 5
    })
    mock_insert = mocker.patch("services.library_service.insert_borrow_record", return_value=True)
    mock_update = mocker.patch("services.library_service.update_book_availability", return_value=True)

    success, message = borrow_book_by_patron("123456", 12)
    
    assert success == True
    assert "successfully borrowed" in message.lower()

