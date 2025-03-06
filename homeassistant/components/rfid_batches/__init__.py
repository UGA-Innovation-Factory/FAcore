"""The RFID Batches integration."""

import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, discovery_flow

from .const import CONF_TAG_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the RFID Batches integration from configuration."""
    _LOGGER.info("Setting up RFID Batches integration")

    @callback
    def async_trigger_discovery(
        hass: HomeAssistant,
        tag_id: str,
    ) -> None:
        """Trigger config flows for discovered device."""
        discovery_flow.async_create_flow(
            hass,
            DOMAIN,
            context={"source": config_entries.SOURCE_INTEGRATION_DISCOVERY},
            data={CONF_TAG_ID: tag_id},
        )

    async def handle_rfid_event(event):
        """Handle incoming RFID tag scanned events."""
        tag = event.data.get(CONF_TAG_ID)
        async_trigger_discovery(hass, tag)
        _LOGGER.info("RFID tag scanned: %s", tag)

    # Listen for events named "rfid_tag_scanned"
    hass.bus.async_listen("tag_scanned", handle_rfid_event)

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up RFID Batches from a config entry."""
    _LOGGER.info("Setting up RFID Batches config entry: %s", entry.data)

    # Forward setup to the select platform (if you want to show batch status)
    await hass.config_entries.async_forward_entry_setups(entry, ["select"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "select")
    return True
