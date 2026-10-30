"""Sensor entities for Up CESU balances.

This module defines the sensor entities exposed by the Up CESU integration.
It includes sensors for:
- e-CESU balance (€)
- Paper CESU balance (€)
"""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from typing import Any

from .const import CONF_CODE_CESU, DOMAIN
from .coordinator import UpCesuDataUpdateCoordinator

# Logger for sensor-related operations
_LOGGER = logging.getLogger(__name__)


class UpCesuSensorDescription(SensorEntityDescription):
    """Description class for Up CESU sensor entities.

    This class extends SensorEntityDescription to define the metadata
    for each sensor (e.g., name, unit of measurement, device class).
    """


# List of all sensor descriptions for the Up CESU integration
DESCRIPTIONS: tuple[UpCesuSensorDescription, ...] = (
    # e-CESU balance sensor (€)
    UpCesuSensorDescription(
        key="e_cesu_balance",
        name="Solde e-CESU",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=True,
        entity_registry_visible_default=True,
    ),
    # Paper CESU balance sensor (€)
    UpCesuSensorDescription(
        key="paper_cesu_balance",
        name="Solde chèques papier",
        native_unit_of_measurement=CURRENCY_EURO,
        device_class=SensorDeviceClass.MONETARY,
        state_class=SensorStateClass.TOTAL,
        entity_registry_enabled_default=True,
        entity_registry_visible_default=True,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Up CESU sensor entities.

    This function is called by Home Assistant to initialize the sensor platform
    for this integration. It creates one sensor entity for each description in DESCRIPTIONS.

    Args:
        hass: Home Assistant core instance.
        entry: Configuration entry for this integration.
        async_add_entities: Callback to add entities to Home Assistant.
    """
    _LOGGER.debug("Starting async_setup_entry for sensor platform (entry_id: %s)", entry.entry_id)

    try:
        # Retrieve the coordinator stored during integration setup
        coordinator = hass.data[DOMAIN][entry.entry_id]
        _LOGGER.debug("Coordinator found for entry_id: %s", entry.entry_id)
    except KeyError:
        # This should not happen if setup was successful, but handle it gracefully
        _LOGGER.error("Coordinator NOT FOUND in hass.data for entry_id: %s. Available keys: %s", 
                      entry.entry_id, list(hass.data.get(DOMAIN, {}).keys()))
        return

    _LOGGER.debug("Creating sensor entities for %d descriptions", len(DESCRIPTIONS))
    # Create a sensor entity for each description
    entities = [UpCesuSensor(coordinator, entry, description) for description in DESCRIPTIONS]
    _LOGGER.debug("Created %d sensor entities: %s", len(entities), [e.unique_id for e in entities])

    # Add all entities to Home Assistant
    async_add_entities(entities)
    _LOGGER.debug("Sensor entities added to Home Assistant")


class UpCesuSensor(CoordinatorEntity[UpCesuDataUpdateCoordinator], SensorEntity):
    """Sensor entity for Up CESU data.

    This class represents a single sensor entity in Home Assistant, backed by
    the UpCesuDataUpdateCoordinator. It dynamically calculates its value
    based on the data fetched from the Up CESU website.

    Attributes:
        _attr_has_entity_name: If True, the entity name is derived from the device name.
        entity_description: Metadata for this sensor (name, unit, device class, etc.).
        _attr_unique_id: Unique identifier for this entity.
        _attr_device_info: Device information (manufacturer, model, etc.).
        _attr_key: Key used to identify which value to extract from coordinator.data.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: UpCesuDataUpdateCoordinator,
        entry: ConfigEntry,
        description: UpCesuSensorDescription,
    ) -> None:
        """Initialize the Up CESU sensor entity.

        Args:
            coordinator: Coordinator that manages data updates.
            entry: Configuration entry for this integration.
            description: Sensor description (metadata).
        """
        _LOGGER.debug("Initializing UpCesuSensor for key: %s, entry_id: %s", description.key, entry.entry_id)
        super().__init__(coordinator)
        self.entity_description = description

        # Set a unique ID for this entity
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"

        # Set device information
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id)},
            name=f"Up CESU {entry.data[CONF_CODE_CESU]}",
            manufacturer="Up Coop",
            model="Espace Bénéficiaire",
        )

        # Store the key to identify which value to extract from coordinator.data
        self._attr_key = description.key
        _LOGGER.debug("UpCesuSensor initialized: unique_id=%s, name=%s", self.unique_id, self.name)

    @property
    def native_value(self) -> float | None:
        """Return the sensor's current value.

        This property dynamically calculates the sensor's value based on the
        data fetched from the Up CESU website.

        Returns:
            float | None: The current value of the sensor, or None if data is unavailable.
        """
        try:
            data = self.coordinator.data

            # Extract the value based on the sensor's key
            if self._attr_key == "e_cesu_balance":
                return data["e_cesu_balance"]
            elif self._attr_key == "paper_cesu_balance":
                return data["paper_cesu_balance"]

            # Fallback for unknown keys
            return None
        except Exception as e:
            _LOGGER.error("Error calculating native_value for sensor %s: %s", self.unique_id, e)
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes for the sensor.

        Returns:
            dict[str, Any] | None: Extra attributes, or None if not applicable.
        """
        try:
            return {
                "last_updated": self.coordinator.data.get("generated_at"),
                "code_cesu": self._attr_device_info["name"].split()[-1],
            }
        except Exception:
            return None
