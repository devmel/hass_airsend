"""Config flow for AirSend integration."""
import os
import logging
import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_INTERNAL_URL

from . import DOMAIN, load_airsend_yaml, get_internal_url

_LOGGER = logging.getLogger(DOMAIN)


async def test_connection(url: str) -> str | None:
    """Test connection to AirSend addon. Returns None if OK, error key otherwise."""
    if not url:
        return "no_url"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                # L'addon répond même avec 401/404, l'important est qu'il réponde
                if response.status < 500:
                    return None
                return "cannot_connect"
    except aiohttp.ClientConnectorError:
        return "cannot_connect"
    except TimeoutError:
        return "timeout"
    except Exception:
        return "cannot_connect"


class AirSendConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the AirSend config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """First step: detect URL, test connection, load devices."""
        errors = {}

        internal_url = await get_internal_url(self.hass)

        if user_input is not None:
            internal_url = user_input.get(CONF_INTERNAL_URL, internal_url).strip()
            if internal_url and not internal_url.endswith("/"):
                internal_url += "/"

            # Test de connexion
            connection_error = await test_connection(internal_url)
            if connection_error:
                errors["base"] = connection_error
            else:
                # Chargement du yaml
                yaml_data = await self.hass.async_add_executor_job(
                    load_airsend_yaml, self.hass
                )
                devices = yaml_data.get("devices", {})

                if not devices:
                    errors["base"] = "no_devices"
                else:
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
        if not yaml_exists and not errors:
            errors["base"] = "yaml_not_found"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_INTERNAL_URL, default=internal_url): str,
                }
            ),
            description_placeholders={"yaml_path": yaml_path},
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

            # Test de connexion
            connection_error = await test_connection(internal_url)
            if connection_error:
                errors["base"] = connection_error
            else:
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
