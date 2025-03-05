"""Config flow for RFID Batches integration."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN


class RfidBatchesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RFID Batches."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Here you could validate and process user_input if needed.
            return self.async_create_entry(
                title=user_input["name"], data=user_input
            )

        data_schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required("card_type", default="HASS Tag"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["HASS Tag", "Pecan Batch", "Equipment"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required("tag_id", default=str(self.tag_id)): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_integration_discovery(self, discovery_info: dict[str, str]):
        """Handle integration discovery."""
        self.tag_id = discovery_info["tag_id"]

        await self.async_set_unique_id(self.tag_id)
        self._abort_if_unique_id_configured()

        return await self.async_step_user()

    @staticmethod
    def async_get_options_flow(entry):
        """Define the options flow."""
        return RfidBatchesOptionsFlowHandler()


class RfidBatchesOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for RFID Batches integration."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # Save additional options, such as batch step or relationships.
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    "batch_step",
                    default=self.config_entry.options.get("batch_step", "Step1"),
                ): str,
                # You can add more options here.
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)
