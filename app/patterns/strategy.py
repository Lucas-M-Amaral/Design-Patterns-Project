from typing import Dict, Any
from abc import ABC, abstractmethod


# Strategy Pattern for Payment Processing
class PaymentStrategy(ABC):
    """Abstract base class for payment strategies."""

    @abstractmethod
    def process_payment(self, amount: float, payment_type) -> Dict[str, Any]:
        """Process the payment and return True if successful, False otherwise."""
        raise NotImplementedError("Subclasses must implement this method.")


class CreditCardPaymentStrategy(PaymentStrategy):
    """Concrete strategy for processing credit card payments."""

    def process_payment(self, amount: float, payment_type) -> Dict[str, Any]:
        """Process a credit card payment."""
        amount /= 3 # applying 3x installments
        installments = 3
        return {"amount": amount, "installments": installments}


class PixPaymentStrategy(PaymentStrategy):
    """Concrete strategy for processing Pix payments."""

    def process_payment(self, amount: float, payment_type) -> Dict[str, Any]:
        """Process a Pix payment."""
        amount *= 0.95  # applying 5% discount
        installments = 1
        return {"amount": amount, "installments": installments}


class BilletPaymentStrategy(PaymentStrategy):
    """Concrete strategy for processing billet payments."""

    def process_payment(self, amount: float, payment_type) -> Dict[str, Any]:
        """Process a billet payment."""
        return {"amount": amount, "installments": 1}


class PaymentContext:
    """Context for using a payment strategy."""

    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy):
        """Set a new payment strategy."""
        self._strategy = strategy

    def process_payment(self, amount: float, payment_type) -> Dict[str, Any]:
        """Process the payment using the current strategy."""
        return self._strategy.process_payment(
            payment_type=payment_type,
            amount=amount
        )
