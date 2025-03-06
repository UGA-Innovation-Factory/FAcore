"""Sensor platform for RFID Batches integration."""

import logging

from homeassistant.components.sensor import SensorEntity

from .const import CONF_ACTIVE, CONF_BATCH_ID, CONF_COMPLETE, CONF_PENDING, CONF_STEPS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the RFID Batch sensor."""
    if CONF_BATCH_ID in config_entry.data:
        batch = config_entry.data.get(CONF_BATCH_ID)
        entities = [BatchStepSensor(batch, step) for step in CONF_STEPS]
        async_add_entities(entities)


class BatchStepSensor(SensorEntity):
    """A sensor representing the current state of a step type for a specific batch."""

    def __init__ (self, batch, step: str, status: str = CONF_PENDING):
        """Initialize the sensor."""
        if step not in CONF_STEPS:
            raise ValueError(f"Invalid step type: {step}")

        self._attr_name = step + " for Batch " + batch
        self._attr_native_value = status
        self._attr_unique_id = batch + "_" + step

    async def async_update(self):
        """Fetch new state data for the sensor."""
        if self._attr_native_value == CONF_PENDING:
            self._attr_native_value = CONF_ACTIVE

        if self._attr_native_value == CONF_ACTIVE:
            self._attr_native_value = CONF_COMPLETE
