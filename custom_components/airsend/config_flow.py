"""Config flow for AirSend integration."""
import os
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_INTERNAL_URL

from . import DOMAIN, load_airsend_yaml, get_internal_url

_LOGGER = logging.getLogger(DOMAIN)

CONF_YAML_PATH = "yaml_path"


class AirSendConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the AirSend config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """First step: confirm airsend.yaml is present and detect URL."""
        errors = {}

        # Auto-detect internal URL
        internal_url = await get_internal_url(self.hass)

        if user_input is not None:
            internal_url = user_input.get(CONF_INTERNAL_URL, internal_url).strip()
            if internal_url and not internal_url.endswith("/"):
                internal_url += "/"

            # Load airsend.yaml to validate it exists and has devices
            yaml_data = await self.hass.async_add_executor_job(
                load_airsend_yaml, self.hass
            )
            devices = yaml_data.get("devices", {})

            if not devices:
                errors["base"] = "no_devices"
            else:
                # Create one config entry for the whole integration
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="AirSend",
                    data={
                        CONF_INTERNAL_URL: internal_url,
                        "devices": devices,
                    },
                )

        yaml_path = self.hass.config.path("airsend.yaml")
        yaml_exists = await self.hass.async_add_executor_job(os.path.exists, yaml_path)

        if not yaml_exists:
            errors["base"] = "yaml_not_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_INTERNAL_URL, default=internal_url): str,
                }
            ),
            description_placeholders={
                "yaml_path": yaml_path,
            },
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Allow reconfiguration (reload yaml + update URL)."""
        errors = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        current_url = entry.data.get(CONF_INTERNAL_URL, "")

        if user_input is not None:
            internal_url = user_input.get(CONF_INTERNAL_URL, current_url).strip()
            if internal_url and not internal_url.endswith("/"):
                internal_url += "/"

            yaml_data = await self.hass.async_add_executor_job(
                load_airsend_yaml, self.hass
            )
            devices = yaml_data.get("devices", {})

            if not devices:
                errors["base"] = "no_devices"
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    data={
                        CONF_INTERNAL_URL: internal_url,
                        "devices": devices,
                    },
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_INTERNAL_URL, default=current_url): str,
                }
            ),
            errors=errors,
        )
