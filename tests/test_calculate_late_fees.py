# calculate_late_fee_for_book - valid input, patron id too short, patron id too long, book id not in db

import pytest
from services.library_service import (
    calculate_late_fee_for_book
)
from datetime import datetime, timedelta

def days_ago(days):
    return datetime.combine(datetime.now().date() - timedelta(days=days) + timedelta(days=1), datetime.min.time())

def days_from_now(days):
    return datetime.combine(datetime.now().date() + timedelta(days=days), datetime.min.time())

def test_calculate_late_fees_valid_input(mocker):
    """Test calculating late fees with a borrowed book that is late."""

    borrowed_book = {
        "book_id": 3,
        "due_date": days_ago(2)
    }
    mocker.patch(
        "services.library_service.get_patron_borrowed_books",
        return_value=[borrowed_book]
    )
    result = calculate_late_fee_for_book("123456", 3)

    assert result["status"].lower() == "success"
    assert result["days_overdue"] == 2
    assert result["fee_amount"] == 1.00

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