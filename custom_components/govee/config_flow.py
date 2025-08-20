"""Config flow for Govee integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import requests

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Govee."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Validate the API key by making a test request
                headers = {"Govee-API-Key": user_input[CONF_API_KEY]}
                response = requests.get(
                    "https://developer-api.govee.com/v1/devices",
                    headers=headers
                )
                response.raise_for_status()

                return self.async_create_entry(
                    title="Govee",
                    data=user_input,
                )
            except requests.RequestException:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )
