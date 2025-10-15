# calculate_late_fee_for_book - valid input, patron id too short, patron id too long, book id not in db

import pytest
from library_service import (
    calculate_late_fee_for_book
)


def test_calculate_late_fees_valid_input():
    """Test calculating late fees with valid input."""
    result = calculate_late_fee_for_book("123456", "3")
    
    assert "success" in result["status"].lower()

def test_calculate_late_fees_patron_id_too_short():
    """Test calculating late fees with patron id too short."""
    result = calculate_late_fee_for_book("1234", "3")
    
    assert "patron not found" in result["status"].lower()

def test_calculate_late_fees_patron_id_too_long():
    """Test calculating late fees with patron id too long."""
    result = calculate_late_fee_for_book("1234567", "3")
    
    assert "patron not found" in result["status"].lower()


def test_calculate_late_fees_book_dne():
    """Test calculating late fees with book that doesn't exist."""
    result = calculate_late_fee_for_book("123456", "999")
    
    assert "book not found" in result["status"].lower()