# get_patron_status_report - test with no patron input, patron input too short, patron input too long, valid input


import pytest
from services.library_service import (
    get_patron_status_report
)

def test_patron_status_report_empty_patron():
    """Test patron status report for empty patron."""
    result = get_patron_status_report("")
    
    assert "patron not found" in result["status"].lower()



def test_patron_status_report_patron_too_long():
    """Test patron status report for patron id too long."""
    result = get_patron_status_report("1234567")
    
    assert "patron not found" in result["status"].lower()


def test_patron_status_report_patron_too_short():
    """Test patron status report for patron id too short."""
    result = get_patron_status_report("12345")
    
    assert "patron not found" in result["status"].lower()


def test_patron_status_report_valid_patron():
    """Test patron status report for patron id too short."""
    result = get_patron_status_report("123456")
    
    assert "success" in result["status"].lower()