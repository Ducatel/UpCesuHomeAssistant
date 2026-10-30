"""Tests for Up CESU API client."""

from __future__ import annotations

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

import pytest

# Import after path setup
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from custom_components.up_cesu.api import (
    UpCesuApiError,
    UpCesuAuthenticationError,
    UpCesuClient,
)


# Test credentials from environment variables
TEST_CODE_CESU = os.getenv("LOGIN", "2159790")
TEST_PASSWORD = os.getenv("PASSWORD", "test_password")


# Integration test with real credentials (only runs if LOGIN and PASSWORD are set)
@pytest.mark.skipif(
    not (os.getenv("LOGIN") and os.getenv("PASSWORD")),
    reason="Real credentials not provided in environment variables"
)
@pytest.mark.asyncio
async def test_real_api_call():
    """Integration test with real Up CESU credentials.
    
    This test requires LOGIN and PASSWORD environment variables to be set.
    It makes a real API call to the Up CESU website.
    """
    code_cesu = os.getenv("LOGIN")
    password = os.getenv("PASSWORD")
    
    logger.info("Credentials loaded from environment")
    logger.info(f"Testing with code CESU: {code_cesu}")
    
    client = UpCesuClient(code_cesu, password)
    
    logger.info("Starting real API call to Up CESU website")
    # This will make a real call to the Up CESU website
    result = await client.async_fetch()
    logger.info("API call completed successfully")
    
    # Basic assertions
    assert "e_cesu_balance" in result
    assert "paper_cesu_balance" in result
    assert "generated_at" in result
    
    # Balance should be a float
    assert isinstance(result["e_cesu_balance"], float)
    assert isinstance(result["paper_cesu_balance"], float)
    
    logger.info(f"e-CESU balance: {result['e_cesu_balance']} €")
    logger.info(f"Paper CESU balance: {result['paper_cesu_balance']} €")
    logger.info(f"Data generated at: {result['generated_at']}")


# Test for balance parsing logic
@pytest.mark.asyncio
async def test_balance_parsing():
    """Test the balance parsing logic with various formats."""
    logger.info("Testing balance parsing logic")
    
    # Test cases: (input_text, expected_float)
    test_cases = [
        ("150,50 €", 150.50),
        ("200,00 €", 200.00),
        ("0,00 €", 0.00),
        ("1 250,50 €", 1250.50),
        ("75,25 €", 75.25),
        ("", 0.00),  # Empty string should default to 0
        ("  ", 0.00),  # Whitespace only
    ]
    
    for input_text, expected in test_cases:
        # Simulate the parsing logic from _extract_balances
        text = input_text or "0,00 €"
        cleaned = text.replace(" ", "").replace("€", "").replace(",", ".").strip()
        result = float(cleaned) if cleaned else 0.0
        assert result == expected, f"Failed to parse '{input_text}': got {result}, expected {expected}"
        logger.debug(f"Parsed '{input_text}' -> {result}")
    
    logger.info("All balance parsing tests passed!")
