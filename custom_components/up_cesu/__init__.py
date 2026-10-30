"""Up CESU integration for Home Assistant.

This integration fetches e-CESU and paper CESU balance data from Up CESU
and exposes it as sensors in Home Assistant.
"""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import UpCesuDataUpdateCoordinator

# Logger for this integration
_LOGGER = logging.getLogger(__name__)

# Platforms supported by this integration (only sensors for now)
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Up CESU integration from a config entry.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry containing user credentials.

    Returns:
        bool: True if setup was successful.

    Raises:
        ConfigEntryNotReady: If initial data fetch fails (e.g., API unavailable).
    """
    _LOGGER.debug("Starting async_setup_entry for Up CESU (entry_id: %s)", entry.entry_id)

    # Create the coordinator to manage data updates
    coordinator = UpCesuDataUpdateCoordinator(hass, entry)
    _LOGGER.debug("Coordinator created for entry_id: %s", entry.entry_id)

    try:
        _LOGGER.debug("Calling async_config_entry_first_refresh")
        # Fetch initial data to validate the configuration
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.debug("First refresh completed successfully")
    except Exception as err:
        _LOGGER.error("Failed to retrieve Up CESU data: %s", err)
        raise ConfigEntryNotReady(f"Unable to retrieve Up CESU data: {err}") from err

    # Store the coordinator in Home Assistant's data for later use
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _LOGGER.debug("Storing coordinator in hass.data and forwarding entry setups")

    # Forward setup to all platforms (e.g., sensor)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.debug("async_setup_entry completed successfully for entry_id: %s", entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Up CESU config entry.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry to unload.

    Returns:
        bool: True if unloading was successful.
    """
    # Unload all platforms (e.g., sensor) for this entry
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Clean up the coordinator from Home Assistant's data
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
