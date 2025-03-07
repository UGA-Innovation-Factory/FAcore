"""Config flow for RFID Batches integration."""

from datetime import datetime
from typing import Any

import funkybob
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ACTUATORS,
    CONF_BATCH_CREATION_DATE,
    CONF_BATCH_ID,
    CONF_CARD_TYPE,
    CONF_CARD_TYPE_BATCH,
    CONF_CARD_TYPE_EQUIPMENT,
    CONF_CARD_TYPE_TAG,
    CONF_NAME,
    CONF_PARENT_BATCH_ID,
    CONF_SENSORS,
    CONF_STEP,
    CONF_STEPS,
    CONF_TAG_ID,
    DOMAIN,
)


class RfidBatchesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RFID Batches."""

    VERSION = 1

    async def async_step_integration_discovery(self, discovery_info: dict[str, str]):
        """Handle integration discovery."""
        self.tag_id = discovery_info[CONF_TAG_ID]

        await self.async_set_unique_id(self.tag_id)
        self._abort_if_unique_id_configured()

        return await self.async_step_user()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""

        if not hasattr(self, "tag_id"):
            self.tag_id = ""

        user_schema = vol.Schema(
            {
                vol.Required(CONF_CARD_TYPE, default=CONF_CARD_TYPE_BATCH): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[CONF_CARD_TYPE_TAG, CONF_CARD_TYPE_BATCH, CONF_CARD_TYPE_EQUIPMENT],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_TAG_ID, default=self.tag_id): str,
            }
        )
        errors = {}

        if user_input is not None:
            self.shared_input = user_input
            if user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_TAG:
                return await self.async_step_tag()
            if user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_EQUIPMENT:
                return await self.async_step_equipment()
            if user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_BATCH:
                return await self.async_step_batch()

        return self.async_show_form(
            step_id="user", data_schema=user_schema, errors=errors
        )

    async def async_step_batch(self, user_input: dict[str, Any] | None = None):
        """Handle entry creation for a batch instance."""
        if user_input is not None:
            return await self.async_step_tag(user_input)

        name_generator = funkybob.RandomNameGenerator(members=2, separator=" ")
        it = iter(name_generator)
        def next_name():
            return next(it)

        BATCH_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_BATCH_ID, default=str(next_name()).title()): str,
                vol.Required(CONF_BATCH_CREATION_DATE, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S")): selector.DateTimeSelector(),
                vol.Optional(CONF_PARENT_BATCH_ID): str,
            }
        )

        return self.async_show_form(
            step_id="batch",
            data_schema=BATCH_DATA_SCHEMA,
        )

    async def async_step_equipment(self, user_input: dict[str, Any] | None = None):
        """Handle entry creation for an equipment instance."""
        if user_input is not None:
            return await self.async_step_tag(user_input)

        EQUIPMENT_DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_STEP): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=CONF_STEPS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_SENSORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor", "input_number", "number", "light"],
                        multiple=True,
                    )
                ),
                vol.Optional(CONF_ACTUATORS): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["switch", "light", "input_number"],
                        multiple=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="equipment",
            data_schema=EQUIPMENT_DATA_SCHEMA,
        )

    async def async_step_tag(self, user_input: dict[str, Any] | None = None):
        """Handle entry creation for a any tag instance."""
        if user_input is None:
            user_input = {}

        if hasattr(self, "shared_input"):
            user_input.update(self.shared_input)

        if user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_TAG:
            title = f"Tag {user_input[CONF_TAG_ID]}"
        elif user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_BATCH:
            title = f"Batch {user_input[CONF_BATCH_ID]}"
        elif user_input[CONF_CARD_TYPE] == CONF_CARD_TYPE_EQUIPMENT:
            title = f"Equipment {user_input[CONF_NAME]}"

        return self.async_create_entry(
            title=title, data=user_input
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        """Define the options flow."""
        return RfidBatchesOptionsFlowHandler()


class RfidBatchesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for RFID Batches integration."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Save additional options, such as batch step or relationships.
            return self.async_create_entry(data=user_input)

        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Optional(CONF_TAG_ID): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            )
        )
