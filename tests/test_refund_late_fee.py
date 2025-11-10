# Test refund_late_fee() function

import pytest
from services.payment_service import PaymentGateway
from services.library_service import refund_late_fee_payment
from unittest.mock import Mock

# Test successful refund, invalid transaction ID rejection, and invalid refund amounts (negative, zero, exceeds $15 maximum).

def test_refund_success(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Success")
    success, msg = refund_late_fee_payment("txn_123", 1.00, mock_gateway)

    assert success is True
    assert msg == "Success"

    mock_gateway.refund_payment.assert_called_with("txn_123", 1.00)

def test_invalid_transaction_id(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Success")
    success, msg = refund_late_fee_payment("123", 1.00, mock_gateway)

    assert success is False
    assert msg == "Invalid transaction ID."

    mock_gateway.refund_payment.assert_not_called()

def test_invalid_refund_negative(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Success")
    success, msg = refund_late_fee_payment("txn_123", -1.00, mock_gateway)

    assert success is False
    assert msg == "Refund amount must be greater than 0."

    mock_gateway.refund_payment.assert_not_called()

def test_invalid_refund_zero(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Success")
    success, msg = refund_late_fee_payment("txn_123", 0.00, mock_gateway)

    assert success is False
    assert msg == "Refund amount must be greater than 0."

    mock_gateway.refund_payment.assert_not_called()

def test_invalid_refund_exceeds_max(mocker):
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.refund_payment.return_value = (True, "Success")
    success, msg = refund_late_fee_payment("txn_123", 16.00, mock_gateway)

    assert success is False
    assert msg == "Refund amount exceeds maximum late fee."

    mock_gateway.refund_payment.assert_not_called()
