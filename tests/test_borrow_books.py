# borrow_book_by_patron - non-digit patron id, patron id too long, book does not exist, book with 0 copies available, valid inputs

import pytest
from library_service import (
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


def test_borrow_book_valid_input():
    """Test borrowing a book with valid input."""
    success, message = borrow_book_by_patron("123456", "1")
    
    assert success == True
    assert "successfully borrowed" in message.lower()

