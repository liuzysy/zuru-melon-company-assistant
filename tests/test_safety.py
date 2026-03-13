"""Unit tests for the safety guardrail module."""

import pytest
from src.safety.guardrail import SafetyGuardrail


@pytest.fixture
def guardrail() -> SafetyGuardrail:
    """Fixture for initializing the SafetyGuardrail."""
    return SafetyGuardrail()


def test_keyword_blocking(guardrail: SafetyGuardrail) -> None:
    """Test that blocked keywords are detected."""
    is_safe, _ = guardrail.check_input("How to hack into a system?")
    assert not is_safe


def test_safe_input(guardrail: SafetyGuardrail) -> None:
    """Test that safe input passes the check."""
    is_safe, _ = guardrail.check_input("What is the company's vacation policy?")
    assert is_safe