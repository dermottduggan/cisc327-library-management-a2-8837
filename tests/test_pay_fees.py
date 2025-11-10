# Test pay_late_fees() function

import pytest
from services.payment_service import PaymentGateway
from services.library_service import pay_late_fees
from unittest.mock import Mock


# Test successful payment, payment declined by gateway, invalid patron ID (verify
# mock NOT called), zero late fees (verify mock NOT called), and network error exception handling.


def test_payment_success(mocker):
    mock_calc_func = mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mock_get_book_func = mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is True
    assert msg == "Payment successful! Success"
    assert txn == "txn_123"

    mock_gateway.process_payment.assert_called_with(patron_id="123456", amount=1.00, description="Late fees for 'The Great Gatsby'")

def test_payment_declined(mocker):
    mock_calc_func = mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mock_get_book_func = mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (False, "", "Payment declined")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert msg == "Payment failed: Payment declined"
    assert txn == None

    mock_gateway.process_payment.assert_called_with(patron_id="123456", amount=1.00, description="Late fees for 'The Great Gatsby'")

def test_invalid_patron_id(mocker):
    mock_calc_func = mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mock_get_book_func = mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    success, msg, txn = pay_late_fees("1234567", 1, mock_gateway)

    assert success is False
    assert msg == "Invalid patron ID. Must be exactly 6 digits."
    assert txn == None

    mock_gateway.process_payment.assert_not_called()

def test_zero_late_fees(mocker):
    mock_calc_func = mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.00})
    mock_get_book_func = mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert msg == "No late fees to pay for this book."
    assert txn == None

    mock_gateway.process_payment.assert_not_called()

def test_network_error_handling(mocker):
    mock_calc_func = mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 1.00})
    mock_get_book_func = mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.process_payment.side_effect = Exception("Exception occurred")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success is False
    assert msg == "Payment processing error: Exception occurred"
    assert txn == None

    mock_gateway.process_payment.assert_called_once()