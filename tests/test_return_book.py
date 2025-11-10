# return_book_by_patron - valid inputs, book does not exist, book not checked out by patron, patron does not exist

import pytest
from services.library_service import (
    return_book_by_patron
)


def test_borrow_book_valid_input(mocker):
    """Test returning a book with valid input."""
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[{"book_id": "3", "title": "Test Book", "author": "Author"}]
    )
    mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"fee_amount": 0.0}
    )
    mocker.patch(
        "services.library_service.update_book_availability",
        return_value=True
    )
    mock_update_record = mocker.patch(
        "services.library_service.update_borrow_record_return_date",
        return_value=True
    )
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
    assert "book not borrowed" in message.lower()