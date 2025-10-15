# search_books_in_catalog - search for correct ISBN, search for incorrect ISBN, search for title with case matching, search for title with wrong casing, invalid title search

import pytest
from library_service import (
    search_books_in_catalog
)

def test_search_catalog_valid_isbn():
    """Test searching catalog for valid ISBN."""
    result = search_books_in_catalog("9780743273565", "isbn")
    
    assert len(result) == 1


def test_search_catalog_invalid_isbn():
    """Test searching catalog for invalid ISBN."""
    result = search_books_in_catalog("9780743273566", "isbn")
    
    assert len(result) == 0


def test_search_catalog_valid_title_correct_case():
    """Test searching catalog for title with correct casing."""
    result = search_books_in_catalog("The Great Gatsby", "title")
    
    assert len(result) == 1

def test_search_catalog_valid_title_incorrect_case():
    """Test searching catalog for title with incorrect casing."""
    result = search_books_in_catalog("the great gatsby", "title")
    
    assert len(result) == 1

def test_search_catalog_invalid_title():
    """Test searching catalog for invalid title."""
    result = search_books_in_catalog("test book", "title")
    
    assert len(result) == 0