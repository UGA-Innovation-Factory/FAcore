"""State Selector platform for RFID Batches integration."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    CONF_ACTIVE,
    CONF_BATCH_ID,
    CONF_COMPLETE,
    CONF_PARENT_BATCH_ID,
    CONF_PENDING,
    CONF_STEPS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the RFID Batch sensor."""
    entity_registry: er.EntityRegistry = er.async_get(hass)
    parent = None
    parent_selectors = []

    steps = CONF_STEPS

    if CONF_PARENT_BATCH_ID in config_entry.data:
        parent = config_entry.data.get(CONF_PARENT_BATCH_ID)
        _LOGGER.info("Setting up Batch %s", parent)
        for step in CONF_STEPS:
            entity_id = entity_registry.async_get_entity_id(DOMAIN, 'select', parent + "_" + step)
            _LOGGER.info("Entity ID: %s", entity_id)
            if entity_id is not None:
                if (state := hass.states.get(entity_id)) is not None:
                    if state.state != CONF_PENDING:
                        parent_selectors.append(entity_registry.async_get(entity_id))
                        steps.remove(step)

    if CONF_BATCH_ID in config_entry.data:
        batch = config_entry.data.get(CONF_BATCH_ID)
        entities = [BatchStepSelector(batch, step) for step in steps]
        entities.extend(parent_selectors)
        async_add_entities(entities)

class BatchStepSelector(SelectEntity, RestoreEntity):
    """A selector representing the current state of a step type for a specific batch."""

    def __init__(self, batch, step: str, status: str = CONF_PENDING):
        """Initialize the sensor."""
        if step not in CONF_STEPS:
            raise ValueError(f"Invalid step type: {step}")

        self._attr_name = step + " for Batch " + batch
        self._attr_unique_id = batch + "_" + step
        self.options = [CONF_PENDING, CONF_ACTIVE, CONF_COMPLETE]
        self.current_option = status

    async def async_added_to_hass(self):
        """Run when entity about to be added to hass."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()
        if state:
            self.current_option = state.state

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        self.current_option = option
