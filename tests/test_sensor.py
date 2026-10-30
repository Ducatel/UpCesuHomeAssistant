"""Tests for Up CESU sensors."""

from __future__ import annotations

import os
import sys
import logging
from dotenv import load_dotenv
from unittest.mock import MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

import pytest

# Import after path setup
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from custom_components.up_cesu.sensor import UpCesuSensor, DESCRIPTIONS
from homeassistant.const import CURRENCY_EURO


# Test credentials from environment variables
TEST_CODE_CESU = os.getenv("LOGIN", "2159790")
TEST_PASSWORD = os.getenv("PASSWORD", "test_password")


def test_sensor_descriptions():
    """Test that sensor descriptions are correctly defined."""
    logger.info("Testing sensor descriptions")
    
    assert len(DESCRIPTIONS) == 2
    logger.debug(f"Found {len(DESCRIPTIONS)} sensor descriptions")
    
    # Check e-CESU balance sensor
    e_cesu_sensor = next(d for d in DESCRIPTIONS if d.key == "e_cesu_balance")
    assert e_cesu_sensor.name == "Solde e-CESU"
    assert e_cesu_sensor.native_unit_of_measurement == CURRENCY_EURO
    logger.debug(f"e-CESU sensor: name={e_cesu_sensor.name}, unit={e_cesu_sensor.native_unit_of_measurement}")
    
    # Check paper CESU balance sensor
    paper_sensor = next(d for d in DESCRIPTIONS if d.key == "paper_cesu_balance")
    assert paper_sensor.name == "Solde chèques papier"
    assert paper_sensor.native_unit_of_measurement == CURRENCY_EURO
    logger.debug(f"Paper CESU sensor: name={paper_sensor.name}, unit={paper_sensor.native_unit_of_measurement}")
    
    logger.info("Sensor descriptions test passed")


def test_sensor_native_value():
    """Test sensor native value extraction."""
    from homeassistant.config_entries import ConfigEntry
    from custom_components.up_cesu.coordinator import UpCesuDataUpdateCoordinator
    
    logger.info("Testing sensor native value extraction")
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": TEST_PASSWORD}
    entry.entry_id = "test_entry"
    entry.unique_id = "test_unique_id"
    
    # Create a mock coordinator
    coordinator = MagicMock(spec=UpCesuDataUpdateCoordinator)
    coordinator.data = {
        "e_cesu_balance": 150.50,
        "paper_cesu_balance": 75.25,
        "generated_at": "2024-01-01T00:00:00Z"
    }
    logger.debug("Mock coordinator data prepared")
    
    # Create e-CESU sensor
    e_cesu_desc = next(d for d in DESCRIPTIONS if d.key == "e_cesu_balance")
    e_cesu_sensor = UpCesuSensor(coordinator, entry, e_cesu_desc)
    
    # Test native value
    assert e_cesu_sensor.native_value == 150.50
    logger.debug(f"e-CESU sensor value: {e_cesu_sensor.native_value}")
    
    # Create paper CESU sensor
    paper_desc = next(d for d in DESCRIPTIONS if d.key == "paper_cesu_balance")
    paper_sensor = UpCesuSensor(coordinator, entry, paper_desc)
    
    # Test native value
    assert paper_sensor.native_value == 75.25
    logger.debug(f"Paper CESU sensor value: {paper_sensor.native_value}")
    
    logger.info("Sensor native value test passed")


def test_sensor_native_value_none():
    """Test sensor native value when data is None."""
    from homeassistant.config_entries import ConfigEntry
    from custom_components.up_cesu.coordinator import UpCesuDataUpdateCoordinator
    
    logger.info("Testing sensor native value with missing data")
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": TEST_PASSWORD}
    entry.entry_id = "test_entry"
    entry.unique_id = "test_unique_id"
    
    # Create a mock coordinator with None data
    coordinator = MagicMock(spec=UpCesuDataUpdateCoordinator)
    coordinator.data = {}
    logger.debug("Mock coordinator with empty data")
    
    # Create e-CESU sensor
    e_cesu_desc = next(d for d in DESCRIPTIONS if d.key == "e_cesu_balance")
    e_cesu_sensor = UpCesuSensor(coordinator, entry, e_cesu_desc)
    
    # Test native value (should be None)
    assert e_cesu_sensor.native_value is None
    logger.debug("Sensor correctly returns None for missing data")
    
    logger.info("Sensor native value None test passed")


def test_sensor_device_info():
    """Test sensor device information."""
    from homeassistant.config_entries import ConfigEntry
    from custom_components.up_cesu.coordinator import UpCesuDataUpdateCoordinator
    
    logger.info("Testing sensor device information")
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": TEST_PASSWORD}
    entry.entry_id = "test_entry"
    entry.unique_id = "test_unique_id"
    
    # Create a mock coordinator
    coordinator = MagicMock(spec=UpCesuDataUpdateCoordinator)
    coordinator.data = {
        "e_cesu_balance": 150.50,
        "paper_cesu_balance": 75.25,
        "generated_at": "2024-01-01T00:00:00Z"
    }
    
    # Create e-CESU sensor
    e_cesu_desc = next(d for d in DESCRIPTIONS if d.key == "e_cesu_balance")
    e_cesu_sensor = UpCesuSensor(coordinator, entry, e_cesu_desc)
    
    # Test device info
    assert e_cesu_sensor.device_info["name"] == f"Up CESU {TEST_CODE_CESU}"
    assert e_cesu_sensor.device_info["manufacturer"] == "Up Coop"
    assert e_cesu_sensor.device_info["model"] == "Espace Bénéficiaire"
    
    logger.debug(f"Device name: {e_cesu_sensor.device_info['name']}")
    logger.debug(f"Manufacturer: {e_cesu_sensor.device_info['manufacturer']}")
    logger.debug(f"Model: {e_cesu_sensor.device_info['model']}")
    
    logger.info("Sensor device info test passed")


def test_sensor_unique_id():
    """Test sensor unique ID generation."""
    from homeassistant.config_entries import ConfigEntry
    from custom_components.up_cesu.coordinator import UpCesuDataUpdateCoordinator
    
    logger.info("Testing sensor unique ID generation")
    
    # Create a mock config entry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"code_cesu": TEST_CODE_CESU, "password": TEST_PASSWORD}
    entry.entry_id = "test_entry"
    entry.unique_id = "test_unique_id"
    
    # Create a mock coordinator
    coordinator = MagicMock(spec=UpCesuDataUpdateCoordinator)
    coordinator.data = {
        "e_cesu_balance": 150.50,
        "paper_cesu_balance": 75.25,
        "generated_at": "2024-01-01T00:00:00Z"
    }
    
    # Create e-CESU sensor
    e_cesu_desc = next(d for d in DESCRIPTIONS if d.key == "e_cesu_balance")
    e_cesu_sensor = UpCesuSensor(coordinator, entry, e_cesu_desc)
    
    # Test unique ID
    assert e_cesu_sensor.unique_id == "test_unique_id_e_cesu_balance"
    logger.debug(f"e-CESU sensor unique ID: {e_cesu_sensor.unique_id}")
    
    # Create paper CESU sensor
    paper_desc = next(d for d in DESCRIPTIONS if d.key == "paper_cesu_balance")
    paper_sensor = UpCesuSensor(coordinator, entry, paper_desc)
    
    # Test unique ID
    assert paper_sensor.unique_id == "test_unique_id_paper_cesu_balance"
    logger.debug(f"Paper CESU sensor unique ID: {paper_sensor.unique_id}")
    
    logger.info("Sensor unique ID test passed")
