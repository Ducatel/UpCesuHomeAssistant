"""Data update coordinator for Up CESU.

This module provides the UpCesuDataUpdateCoordinator class, which manages
periodic data updates from the Up CESU website and caches the results for
all sensor entities to use.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import UpCesuApiError, UpCesuAuthenticationError, UpCesuClient
from .const import CONF_CODE_CESU, CONF_PASSWORD, DOMAIN, UPDATE_INTERVAL

# Logger for coordinator operations
_LOGGER = logging.getLogger(__name__)


class UpCesuDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for fetching and caching Up CESU data.

    This class extends Home Assistant's DataUpdateCoordinator to:
    - Periodically fetch data from the Up CESU website.
    - Cache the data for all sensor entities to use.
    - Handle errors (e.g., authentication failures, timeouts).

    Attributes:
        client: UpCesuClient instance for fetching data.
    """

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry
    ) -> None:
        """Initialize the coordinator.

        Args:
            hass: Home Assistant core instance.
            entry: Configuration entry for this integration.
        """
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
            always_update=False,
        )
        # Initialize the API client with user credentials
        self.client = UpCesuClient(
            entry.data[CONF_CODE_CESU],
            entry.data[CONF_PASSWORD],
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and return the latest data from Up CESU website.

        This method is called automatically by the coordinator at the specified
        update interval (default: every 6 hours).

        Returns:
            dict: Data containing e-CESU and paper CESU balances.

        Raises:
            ConfigEntryAuthFailed: If authentication fails (triggers re-authentication flow).
            UpdateFailed: If there is an API error or other issue.
        """
        _LOGGER.debug("Starting _async_update_data for coordinator")
        try:
            data = await self.client.async_fetch()
            _LOGGER.debug("Data fetched successfully: %s", data)
            return data
        except UpCesuAuthenticationError as err:
            _LOGGER.error("Authentication failed in coordinator: %s", err)
            # Raise ConfigEntryAuthFailed to trigger Home Assistant's re-authentication flow
            raise ConfigEntryAuthFailed from err
        except UpCesuApiError as err:
            _LOGGER.error("API error in coordinator: %s", err)
            raise UpdateFailed(str(err)) from err
        except Exception as err:
            _LOGGER.error("Unexpected error in coordinator: %s", err)
            raise UpdateFailed(str(err)) from err
