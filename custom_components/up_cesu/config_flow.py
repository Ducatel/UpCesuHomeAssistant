"""Configuration flow for Up CESU integration.

This module handles the user interface for configuring the Up CESU integration,
including validation of credentials during setup.
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import UpCesuApiError, UpCesuAuthenticationError, UpCesuClient
from .const import CONF_CODE_CESU, CONF_PASSWORD, DOMAIN

# Logger for configuration flow operations
_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow):
    """Configuration flow handler for Up CESU integration.

    This class manages the user interface for adding and configuring
    the Up CESU integration in Home Assistant.

    Attributes:
        VERSION: Configuration flow version (increment when making breaking changes).
    """

    VERSION = 1

    def _schema(self, defaults: dict[str, Any] | None = None) -> vol.Schema:
        """Create a configuration schema for the Up CESU integration.

        Args:
            defaults: Optional dictionary of default values for the form fields.

        Returns:
            vol.Schema: A schema defining the configuration form fields.
        """
        defaults = defaults or {}
        return vol.Schema(
            {
                vol.Required(CONF_CODE_CESU, default=defaults.get(CONF_CODE_CESU, "")): str,
                vol.Required(CONF_PASSWORD, default=defaults.get(CONF_PASSWORD, "")): str,
            }
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial configuration step (user form submission).

        This method is called when the user submits the configuration form.
        It validates the credentials and creates a new config entry if successful.

        Args:
            user_input: Dictionary containing user-submitted form data (code CESU, password).

        Returns:
            ConfigFlowResult: Result of the configuration step (form or entry creation).
        """
        _LOGGER.debug("Starting async_step_user")
        errors: dict[str, str] = {}

        if user_input is not None:
            _LOGGER.debug("Validating user input: code_cesu=%s", user_input.get(CONF_CODE_CESU, "REDACTED"))

            try:
                await self._async_validate_input(user_input)
                _LOGGER.debug("Input validation successful")
            except UpCesuAuthenticationError as e:
                _LOGGER.error("Authentication failed: %s", e)
                errors["base"] = "invalid_auth"
            except UpCesuApiError as e:
                _LOGGER.error("API error during validation: %s", e)
                errors["base"] = "cannot_connect"
            except Exception as e:
                _LOGGER.error("Unexpected error during validation: %s", e)
                errors["base"] = "unknown"
            else:
                # Set the unique ID to the code CESU (to prevent duplicate entries)
                await self.async_set_unique_id(user_input[CONF_CODE_CESU])
                self._abort_if_unique_id_configured()

                _LOGGER.debug("Creating config entry for code CESU: %s", user_input[CONF_CODE_CESU])
                return self.async_create_entry(
                    title=f"Up CESU ({user_input[CONF_CODE_CESU]})",
                    data=user_input
                )

        _LOGGER.debug("Showing form with errors: %s", errors)
        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(user_input),
            errors=errors
        )

    async def _async_validate_input(self, data: dict[str, Any]) -> None:
        """Validate user input by testing the connection.

        Args:
            data: Dictionary containing user input (code CESU, password).

        Raises:
            UpCesuAuthenticationError: If credentials are invalid.
            UpCesuApiError: If there is an API error (e.g., network issue).
        """
        client = UpCesuClient(
            data[CONF_CODE_CESU],
            data[CONF_PASSWORD],
        )
        await client.async_fetch()
