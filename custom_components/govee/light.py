"""Platform for Govee light integration."""
from __future__ import annotations

import logging
from typing import Any
from datetime import datetime

import aiohttp
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ATTR_COLOR_TEMP,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.color import (
    color_temperature_kelvin_to_mired,
    color_temperature_mired_to_kelvin,
)
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
        lights.append(GoveeLight(hass, entry, device))

    async_add_entities(lights)

class GoveeLight(LightEntity):
    """Representation of a Govee Light."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, device_info: dict) -> None:
        """Initialize the light."""
        self.hass = hass
        self._entry_id = config_entry.entry_id
        self._api_key = config_entry.data[CONF_API_KEY]
        self._device = device_info
        self._attr_name = device_info["deviceName"]
        self._attr_unique_id = device_info["device"]
        self._device_id = device_info["device"]
        self._model = device_info["model"]
        self._state = None
        self._brightness = None
        self._color = None
        self._color_temp = None
        self._available = True
        self._attr_should_poll = True
        
        # Define color temperature range (in Kelvin)
        self._attr_min_color_temp_kelvin = 2000  # Warm white
        self._attr_max_color_temp_kelvin = 9000  # Cool white
        
        # Set supported features based on device capabilities
        self._attr_supported_color_modes = set()
        
        # Get device capabilities from supportCmds if available
        commands = device_info.get("supportCmds", [])
        if isinstance(commands, list):
            if "color" in commands:
                self._attr_supported_color_modes.add(ColorMode.RGB)
            if "colorTem" in commands:
                self._attr_supported_color_modes.add(ColorMode.COLOR_TEMP)
            if "brightness" in commands:
                if not self._attr_supported_color_modes:
                    self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)
            
        # If no specific modes are supported, default to ON/OFF
        if not self._attr_supported_color_modes:
            self._attr_supported_color_modes = {ColorMode.ONOFF}
            self._attr_color_mode = ColorMode.ONOFF
        else:
            # Set the current color mode based on capabilities
            self._attr_color_mode = (
                ColorMode.RGB if ColorMode.RGB in self._attr_supported_color_modes
                else ColorMode.BRIGHTNESS if ColorMode.BRIGHTNESS in self._attr_supported_color_modes
                else ColorMode.ONOFF
            )
        
        # Initialize features - using proper color modes instead of deprecated features
        self._attr_supported_features = 0  # No additional features beyond color modes

    @property
    def available(self) -> bool:
        """Return if light is available."""
        return self._available

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
        return self._color if ColorMode.RGB in self._attr_supported_color_modes else None

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature in Kelvin."""
        return self._color_temp if ColorMode.COLOR_TEMP in self._attr_supported_color_modes else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = "https://developer-api.govee.com/v1/devices/control"
        
        command = {
            "device": self._device_id,
            "model": self._model,
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

        try:
            async with session.put(url, headers=headers, json=command) as response:
                response.raise_for_status()
                self._state = True
                if ATTR_BRIGHTNESS in kwargs:
                    self._brightness = kwargs[ATTR_BRIGHTNESS]
                if ATTR_RGB_COLOR in kwargs:
                    self._color = kwargs[ATTR_RGB_COLOR]
        except Exception as e:
            _LOGGER.error("Error turning on Govee light %s: %s", self._attr_name, str(e))
            self._available = False

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = "https://developer-api.govee.com/v1/devices/control"
        
        command = {
            "device": self._device_id,
            "model": self._model,
            "cmd": {
                "name": "turn",
                "value": "off"
            }
        }

        try:
            async with session.put(url, headers=headers, json=command) as response:
                response.raise_for_status()
                self._state = False
        except Exception as e:
            _LOGGER.error("Error turning off Govee light %s: %s", self._attr_name, str(e))
            self._available = False

    async def async_update(self) -> None:
        """Fetch new state data for this light."""
        rate_limiter = self.hass.data[DOMAIN][self._entry_id]["rate_limiter"]
        
        if not await rate_limiter.can_make_request():
            _LOGGER.debug("Rate limit reached for %s, skipping update", self._attr_name)
            return
            
        session = async_get_clientsession(self.hass)
        headers = {"Govee-API-Key": self._api_key}
        url = f"https://developer-api.govee.com/v1/devices/state?device={self._device_id}&model={self._model}"

        try:
            async with session.get(url, headers=headers) as response:
                # Update rate limiter with response headers
                remaining = response.headers.get("Rate-Limit-Remaining")
                reset_time = response.headers.get("Rate-Limit-Reset")
                if remaining is not None and reset_time is not None:
                    rate_limiter.update_api_limits(
                        int(remaining),
                        datetime.fromtimestamp(int(reset_time))
                    )
                
                # Handle rate limit response
                if response.status == 429:
                    _LOGGER.warning(
                        "Rate limit reached for %s, next update in %s seconds",
                        self._attr_name,
                        reset_time
                    )
                    await rate_limiter.increment_call_count()
                    return
                
                response.raise_for_status()
                await rate_limiter.increment_call_count()
                
                data = await response.json()
                if "data" in data and "properties" in data["data"]:
                    properties = data["data"]["properties"]
                    for prop in properties:
                        if not isinstance(prop, dict) or "name" not in prop:
                            continue
                            
                        prop_name = prop.get("name", "")
                        prop_value = prop.get("value")
                        
                        if prop_name == "powerState":
                            self._state = prop_value == "on"
                        elif prop_name == "brightness" and prop_value is not None:
                            try:
                                self._brightness = int(float(prop_value) * 255 / 100)
                            except (ValueError, TypeError):
                                _LOGGER.warning("Invalid brightness value received: %s", prop_value)
                        elif prop_name == "color" and isinstance(prop_value, dict):
                            try:
                                self._color = (
                                    prop_value.get("r", 0),
                                    prop_value.get("g", 0),
                                    prop_value.get("b", 0)
                                )
                            except (ValueError, TypeError):
                                _LOGGER.warning("Invalid color value received: %s", prop_value)
                    self._available = True
                else:
                    self._available = False

        except aiohttp.ClientError as e:
            _LOGGER.error("Error updating Govee light %s: %s", self._attr_name, str(e))
            self._available = False
        except Exception as e:
            _LOGGER.error("Unexpected error updating Govee light %s: %s", self._attr_name, str(e))
            self._available = False
