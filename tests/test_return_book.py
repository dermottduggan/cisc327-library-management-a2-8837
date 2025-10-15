# return_book_by_patron - valid inputs, book does not exist, book not checked out by patron, patron does not exist

import pytest
from library_service import (
    return_book_by_patron
)


def test_borrow_book_valid_input():
    """Test returning a book with valid input."""
    success, message = return_book_by_patron("123456", "3")
    
    assert success == True
    assert "successfully returned" in message.lower()


def test_borrow_book_book_dne():
    """Test returning a book with book that doesn't exist."""
    success, message = return_book_by_patron("123456", "999")
    
    assert success == False
    assert "book not borrowed" in message.lower()


def test_borrow_book_book_not_checked_out():
    """Test returning a book with book not checked out."""
    success, message = return_book_by_patron("123456", "1")
    
    assert success == False
    assert "book not borrowed" in message.lower()


def test_borrow_book_patron_dne():
    """Test returning a book with patron that doesn't exist"""
    success, message = return_book_by_patron("999999", "1")
    
    assert success == False
    assert "patron not found" in message.lower()