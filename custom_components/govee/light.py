"""Platform for Govee light integration."""
from __future__ import annotations

import logging
from typing import Any

import requests
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
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
    
    # Get the list of devices from Govee API
    headers = {"Govee-API-Key": api_key}
    response = requests.get(
        "https://developer-api.govee.com/v1/devices",
        headers=headers
    )
    response.raise_for_status()
    devices = response.json().get("data", {}).get("devices", [])

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

    def turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
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

        response = requests.put(url, headers=headers, json=command)
        response.raise_for_status()
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
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

        response = requests.put(url, headers=headers, json=command)
        response.raise_for_status()
        self._state = False

    def update(self) -> None:
        """Fetch new state data for this light."""
        headers = {"Govee-API-Key": self._api_key}
        url = f"https://developer-api.govee.com/v1/devices/state"
        params = {
            "device": self._device["device"],
            "model": self._device["model"]
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
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
        except Exception as err:
            _LOGGER.error("Error updating Govee light state: %s", err)
