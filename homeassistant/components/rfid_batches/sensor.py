"""Sensor platform for RFID Batches integration."""

import logging

from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the RFID Batch sensor."""
    async_add_entities([RfidBatchSensor()])


class RfidBatchSensor(SensorEntity):
    """A dummy sensor representing the RFID Batch status."""

    _attr_name = "RFID Batch Sensor"
    _attr_native_value = "Not set"

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return "mdi:tag"

    async def async_update(self):
        """Fetch new state data for the sensor."""
        # Add logic to update sensor state from your batch processing data.
        self._attr_native_value = "Updated"
