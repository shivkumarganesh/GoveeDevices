"""Config flow for Govee integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
                # Get the Home Assistant aiohttp client session
                session = async_get_clientsession(self.hass)
                
                # Validate the API key by making a test request
                headers = {"Govee-API-Key": user_input[CONF_API_KEY]}
                async with session.get(
                    "https://developer-api.govee.com/v1/devices",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_text = await response.text()
                    _LOGGER.debug("Govee API Response: %s", response_text)
                    
                    if response.status == 401:
                        _LOGGER.error("Invalid API key provided")
                        errors["base"] = "invalid_api_key"
                    elif response.status == 429:
                        _LOGGER.error("Rate limit exceeded")
                        errors["base"] = "rate_limit"
                    elif response.status != 200:
                        _LOGGER.error("API error: %s - %s", response.status, response_text)
                        errors["base"] = "api_error"
                    else:
                        # Verify the response contains valid data
                        data = await response.json()
                        if "data" not in data or "devices" not in data["data"]:
                            _LOGGER.error("Unexpected API response format: %s", data)
                            errors["base"] = "invalid_response"
                        else:
                            return self.async_create_entry(
                                title="Govee",
                                data=user_input,
                            )
                        
            except aiohttp.ClientTimeout:
                _LOGGER.error("Timeout connecting to Govee API")
                errors["base"] = "timeout"
            except aiohttp.ClientError:
                _LOGGER.error("Connection error to Govee API")
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error("Unknown error occurred: %s", str(err))
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )
