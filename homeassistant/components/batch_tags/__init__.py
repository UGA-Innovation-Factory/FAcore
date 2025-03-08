"""The Batch Tags integration."""

import logging

from homeassistant import config_entries
from homeassistant.components.tag import TagEntity
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers import config_validation as cv, discovery_flow

from .const import CONF_TAG_ID, DOMAIN
from .models import async_tag_exists

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.empty_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Batche Tags integration from configuration."""
    _LOGGER.info("Setting up Batche Tags integration")

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

    async def handle_tag_scanned_event(event: Event) -> None:
        """Handle incoming tag scanned events."""

        tag = event.data.get(CONF_TAG_ID)
        if not await async_tag_exists(hass, tag):
            async_trigger_discovery(hass, tag)
        _LOGGER.info("Tag scanned: %s", tag)

    # Listen for events named "tag_scanned"
    hass.bus.async_listen("tag_scanned", handle_tag_scanned_event)

    hass.data.setdefault(DOMAIN, {})

    return True


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Set up Batche Tags from a config entry."""
    _LOGGER.info("Setting up Batche Tags config entry: %s", entry.data)

    # Forward setup to the select platform (if you want to show batch status)
    await hass.config_entries.async_forward_entry_setups(entry, ["select"])
    return True


async def async_update_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Update a config entry."""


async def async_unload_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "select")
    return True


class BatchTagEntity(TagEntity):
    """Extention of the TagEntity class for batch tags."""

    def __init__(self, tag_id: str, batch_id: str | None = None, extra_attributes: dict | None = None):
        """Initialize the tag entity."""
        self._tag_id = tag_id
        self._batch_id = batch_id
        self._extra_attributes = extra_attributes

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the tag."""
        return self._tag_id

    @property
    def name(self) -> str:
        """Return the name of the tag."""
        return self._batch_id or self._tag_id

    @property
    def extra_state_attributes(self) -> dict:
        """Return the extra state attributes."""
        return self._extra_attributes or {}

