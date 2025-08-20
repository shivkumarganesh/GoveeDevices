"""Platform for Govee light integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Govee light devices."""
    api_key = entry.data[CONF_API_KEY]
    rate_limiter = hass.data[DOMAIN][entry.entry_id]["rate_limiter"]
    session = async_get_clientsession(hass)
    
    if not await rate_limiter.can_make_request():
        _LOGGER.warning("Rate limit reached, delaying device setup")
        return

    # Get the list of devices from Govee API
    headers = {"Govee-API-Key": api_key}
    async with session.get(
        "https://developer-api.govee.com/v1/devices",
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=10)
    ) as response:
        response.raise_for_status()
        
        # Update rate limiter with API response headers
        remaining = response.headers.get("Rate-Limit-Remaining")
        reset_time = response.headers.get("Rate-Limit-Reset")
        if remaining and reset_time:
            rate_limiter.update_api_limits(
                int(remaining),
                datetime.fromtimestamp(int(reset_time))
            )
        
        await rate_limiter.increment_call_count()
        
        data = await response.json()
        devices = data.get("data", {}).get("devices", [])
        
        # Update device count in rate limiter
        await rate_limiter.update_device_count(len(devices))

    # Create light entities for each device
    lights = []
    for device in devices:
        lights.append(GoveeLight(device, api_key))

    async_add_entities(lights)

class GoveeLight(LightEntity):
    """Representation of a Govee Light."""

    def __init__(self, device: dict, api_key: str) -> None:
        """Initialize the light."""
        self._device = device
        self._api_key = api_key
        self._attr_unique_id = device["device"]
        self._attr_name = device["deviceName"]
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._state = None
        self._brightness = None
        self._rgb_color = None

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Return the rgb color value [int, int, int]."""
        return self._rgb_color

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = "https://developer-api.govee.com/v1/devices/control"
        
        command = {
            "device": self._device["device"],
            "model": self._device["model"],
            "cmd": {
                "name": "turn",
                "value": "on"
            }
        }

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 255 * 100)
            command["cmd"] = {
                "name": "brightness",
                "value": brightness
            }

        if ATTR_RGB_COLOR in kwargs:
            command["cmd"] = {
                "name": "color",
                "value": {
                    "r": kwargs[ATTR_RGB_COLOR][0],
                    "g": kwargs[ATTR_RGB_COLOR][1],
                    "b": kwargs[ATTR_RGB_COLOR][2]
                }
            }

        async with session.put(url, headers=headers, json=command) as response:
            response.raise_for_status()
            self._state = True

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = "https://developer-api.govee.com/v1/devices/control"
        
        command = {
            "device": self._device["device"],
            "model": self._device["model"],
            "cmd": {
                "name": "turn",
                "value": "off"
            }
        }

        async with session.put(url, headers=headers, json=command) as response:
            response.raise_for_status()
            self._state = False

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        rate_limiter = self.hass.data[DOMAIN][self._entry_id]["rate_limiter"]
        
        if not await rate_limiter.can_make_request():
            _LOGGER.warning("Rate limit reached, skipping update for device %s", self._attr_name)
            return

        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = f"https://developer-api.govee.com/v1/devices/state"
        params = {
            "device": self._device["device"],
            "model": self._device["model"]
        }

        try:
            async with session.get(url, headers=headers, params=params) as response:
                response.raise_for_status()
                
                # Update rate limiter with API response headers
                remaining = response.headers.get("Rate-Limit-Remaining")
                reset_time = response.headers.get("Rate-Limit-Reset")
                if remaining and reset_time:
                    rate_limiter.update_api_limits(
                        int(remaining),
                        datetime.fromtimestamp(int(reset_time))
                    )
                
                await rate_limiter.increment_call_count()
                
                data = await response.json()
                
                for prop in data.get("data", {}).get("properties", []):
                    if prop["name"] == "powerState":
                        self._state = prop["value"] == "on"
                    elif prop["name"] == "brightness":
                        self._brightness = int(prop["value"] * 255 / 100)
                    elif prop["name"] == "color":
                        self._rgb_color = (
                            prop["value"]["r"],
                            prop["value"]["g"],
                            prop["value"]["b"]
                        )
                        
                # Update polling interval based on current usage
                scan_interval = rate_limiter.polling_interval
                if scan_interval != self._attr_scan_interval:
                    self._attr_scan_interval = scan_interval
                    
        except Exception as err:
            _LOGGER.error("Error updating Govee light state: %s", err)
