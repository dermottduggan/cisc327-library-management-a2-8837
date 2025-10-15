import pytest
from library_service import add_book_to_catalog
from database import get_book_by_isbn, insert_book 

def test_add_valid_book_success(monkeypatch):
    """✅ Normal case: Adds a valid new book successfully."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: None)
    monkeypatch.setattr("database.insert_book", lambda *args: True)
    
    success, message = add_book_to_catalog(
        title="Clean Code",
        author="Robert C. Martin",
        isbn="9780132350884",
        total_copies=5
    )
    assert success is True
    assert "successfully added" in message


# --- EDGE CASES ---

def test_add_book_title_max_length(monkeypatch):
    """⚙️ Edge case: Title exactly 200 characters."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: None)
    monkeypatch.setattr("database.insert_book", lambda *args: True)
    
    title = "A" * 200
    success, message = add_book_to_catalog(
        title=title,
        author="Author Name",
        isbn="1234567890123",
        total_copies=1
    )
    assert success is True
    assert "successfully added" in message


def test_add_book_duplicate_isbn(monkeypatch):
    """⚙️ Edge case: Attempt to add a book with an existing ISBN."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: {"title": "Existing Book"})
    
    success, message = add_book_to_catalog(
        title="New Book",
        author="New Author",
        isbn="1234567890123",
        total_copies=2
    )
    assert success is False
    assert "already exists" in message


# --- INVALID CASES ---

def test_add_book_missing_title(monkeypatch):
    """❌ Invalid case: Missing title."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: None)
    
    success, message = add_book_to_catalog(
        title="   ",  # Blank title
        author="Author",
        isbn="1234567890123",
        total_copies=3
    )
    assert success is False
    assert "Title is required" in message


def test_add_book_invalid_isbn_length(monkeypatch):
    """❌ Invalid case: ISBN not 13 digits."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: None)
    
    success, message = add_book_to_catalog(
        title="Test Book",
        author="Author",
        isbn="12345",  # Too short
        total_copies=2
    )
    assert success is False
    assert "ISBN must be exactly 13 digits" in message


def test_add_book_negative_total_copies(monkeypatch):
    """❌ Invalid case: Total copies is not a positive integer."""
    monkeypatch.setattr("database.get_book_by_isbn", lambda isbn: None)
    
    success, message = add_book_to_catalog(
        title="Book Title",
        author="Author",
        isbn="1234567890123",
        total_copies=-1
    )
    assert success is False
    assert "positive integer" in message
