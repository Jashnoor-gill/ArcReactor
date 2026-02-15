"""Small fee utilities for admin fee management (minimal complexity)."""
from typing import NamedTuple


def calculate_due_amount(base_fee: float, discounts: float = 0.0, payments_made: float = 0.0, late_fee: float = 0.0) -> float:
    """Calculate remaining due amount with O(1) complexity.

    Formula: due = base_fee - discounts - payments_made + late_fee
    Returns a non-negative amount rounded to 2 decimals.

    Examples:
        >>> calculate_due_amount(1000, discounts=100, payments_made=200, late_fee=50)
        750.0
    """
    try:
        due = float(base_fee) - float(discounts) - float(payments_made) + float(late_fee)
    except (TypeError, ValueError):
        raise ValueError("Numeric inputs required for fee calculation")

    if due <= 0:
        return 0.0
    return round(due, 2)


class Invoice(NamedTuple):
    student_id: int
    base_fee: float
    discounts: float
    payments_made: float
    late_fee: float
    due: float


def create_invoice(student_id: int, base_fee: float, discounts: float = 0.0, payments_made: float = 0.0, late_fee: float = 0.0) -> Invoice:
    """Return a simple Invoice NamedTuple (no DB operations)."""
    due = calculate_due_amount(base_fee, discounts, payments_made, late_fee)
    return Invoice(student_id=student_id, base_fee=base_fee, discounts=discounts, payments_made=payments_made, late_fee=late_fee, due=due)
