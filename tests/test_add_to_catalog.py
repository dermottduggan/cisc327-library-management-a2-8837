# add_book_to_catalog - isbn too long, copies set to 0, copies set to -1, empty author field, empty title field

import pytest
from services.library_service import (
    add_book_to_catalog
)

def test_add_book_valid_input(mocker):
    """Test adding a book with valid input."""

    mocker.patch("services.library_service.get_db_connection", autospec=True)
    mocker.patch("services.library_service.get_all_books", return_value=[])
    mock_insert = mocker.patch("services.library_service.insert_book", return_value=True)

    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890126", 5)
    
    assert success == True
    assert "successfully added" in message.lower()


def test_add_book_invalid_isbn_too_short():
    """Test adding a book with ISBN too short."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "123456789", 5)
    
    assert success == False
    assert "13 digits" in message


def test_add_book_invalid_isbn_too_long():
    """Test adding a book with ISBN too long."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "12345678901234", 5)
    
    assert success == False
    assert "13 digits" in message


def test_add_book_invalid_copies_zero():
    """Test adding a book with 0 copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", 0)
    
    assert success == False
    assert "positive integer" in message


def test_add_book_invalid_copies_negative():
    """Test adding a book with -1 copies."""
    success, message = add_book_to_catalog("Test Book", "Test Author", "1234567890123", -1)
    
    assert success == False
    assert "positive integer" in message


def test_add_book_invalid_author_empty():
    """Test adding a book with empty author."""
    success, message = add_book_to_catalog("Test Book", "", "1234567890123", 1)
    
    assert success == False
    assert "Author" in message


def test_add_book_invalid_title_empty():
    """Test adding a book with empty title."""
    success, message = add_book_to_catalog("", "Test Author", "1234567890123", 1)
    
    assert success == False
    assert "Title" in message