"""Tests for Up CESU coordinator."""

from __future__ import annotations

import os
import sys
import logging
from dotenv import load_dotenv
from unittest.mock import AsyncMock, MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

import pytest

# Import after path setup
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from custom_components.up_cesu.coordinator import UpCesuDataUpdateCoordinator
from custom_components.up_cesu.api import UpCesuApiError, UpCesuClient


# Test credentials from environment variables
TEST_CODE_CESU = os.getenv("LOGIN", "2159790")
TEST_PASSWORD = os.getenv("PASSWORD", "test_password")


@pytest.mark.asyncio
async def test_coordinator_update():
    """Test coordinator data update."""
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
    
    logger.info("Testing coordinator data update")
    
    # Create a mock Home Assistant instance
    hass = MagicMock(spec=HomeAssistant)
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": TEST_PASSWORD}
    entry.entry_id = "test_entry"
    
    # Create coordinator
    coordinator = UpCesuDataUpdateCoordinator(hass, entry)
    logger.debug("Coordinator created")
    
    # Mock the client's async_fetch method
    mock_data = {
        "e_cesu_balance": 150.50,
        "paper_cesu_balance": 75.25,
        "generated_at": "2024-01-01T00:00:00Z"
    }
    coordinator.client.async_fetch = AsyncMock(return_value=mock_data)
    logger.debug("Mock data prepared")
    
    # Call update
    result = await coordinator._async_update_data()
    logger.debug("Update completed")
    
    # Assertions
    assert result == mock_data
    coordinator.client.async_fetch.assert_called_once()
    logger.info("Coordinator update test passed")


@pytest.mark.asyncio
async def test_coordinator_update_failure():
    """Test coordinator data update failure."""
    from homeassistant.core import HomeAssistant
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.helpers.update_coordinator import UpdateFailed
    from homeassistant.exceptions import ConfigEntryAuthFailed
    
    logger.info("Testing coordinator error handling")
    
    # Create a mock Home Assistant instance
    hass = MagicMock(spec=HomeAssistant)
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": "wrong_password"}
    entry.entry_id = "test_entry"
    
    # Create coordinator
    coordinator = UpCesuDataUpdateCoordinator(hass, entry)
    
    # Mock the client's async_fetch method to raise authentication error
    from custom_components.up_cesu.api import UpCesuAuthenticationError
    coordinator.client.async_fetch = AsyncMock(side_effect=UpCesuAuthenticationError("Invalid credentials"))
    logger.debug("Testing authentication error handling")
    
    # Call update and expect ConfigEntryAuthFailed
    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()
    logger.info("Authentication error handled correctly")
    
    # Mock the client's async_fetch method to raise API error
    coordinator.client.async_fetch = AsyncMock(side_effect=UpCesuApiError("API error"))
    logger.debug("Testing API error handling")
    
    # Call update and expect UpdateFailed
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    logger.info("API error handled correctly")
