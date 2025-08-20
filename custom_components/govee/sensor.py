"""Sensors for Govee integration."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.const import PERCENTAGE
from homeassistant.util import dt as dt_util

from . import DOMAIN
from .rate_limiter import GoveeRateLimiter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Govee sensors."""
    rate_limiter = hass.data[DOMAIN][entry.entry_id]["rate_limiter"]
    
    async_add_entities(
        [
            GoveeApiRateLimitSensor(rate_limiter),
            GoveePollingIntervalSensor(rate_limiter),
            GoveeApiCallsSensor(rate_limiter),
        ]
    )

class GoveeApiRateLimitSensor(SensorEntity):
    """Sensor for tracking Govee API rate limit."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(self, rate_limiter: GoveeRateLimiter) -> None:
        """Initialize the sensor."""
        self._rate_limiter = rate_limiter
        self._attr_unique_id = "govee_api_rate_limit"
        self._attr_name = "Govee API Rate Limit"
        self._attr_should_poll = True

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        stats = self._rate_limiter.usage_stats
        return round(stats["usage_percentage"], 2)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        return self._rate_limiter.usage_stats

    async def async_update(self) -> None:
        """Update the sensor."""
        # The rate limiter maintains its own state
        pass

class GoveeApiCallsSensor(SensorEntity):
    """Sensor for tracking detailed Govee API usage."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_should_poll = True
    _attr_icon = "mdi:api"

    def __init__(self, rate_limiter: GoveeRateLimiter) -> None:
        """Initialize the sensor."""
        self._rate_limiter = rate_limiter
        self._attr_unique_id = "govee_api_calls"
        self._attr_name = "Govee API Calls"
        self._attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> StateType:
        """Return the total number of API calls made today."""
        return self._rate_limiter.usage_stats["total_calls_today"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        stats = self._rate_limiter.usage_stats
        
        # Format the reset time for better readability
        reset_time = None
        if stats.get("api_reset_time"):
            try:
                reset_time = dt_util.as_local(
                    datetime.fromisoformat(stats["api_reset_time"])
                ).isoformat()
            except (ValueError, TypeError):
                reset_time = stats["api_reset_time"]

        # Format the last reset date
        last_reset = None
        if stats.get("last_reset_date"):
            try:
                last_reset = dt_util.as_local(
                    datetime.fromisoformat(stats["last_reset_date"])
                ).isoformat()
            except (ValueError, TypeError):
                last_reset = stats["last_reset_date"]

        return {
            "total_calls_today": stats["total_calls_today"],
            "remaining_calls": stats["remaining_calls"],
            "usage_percentage": round(stats["usage_percentage"], 2),
            "daily_limit": stats["daily_limit"],
            "device_count": stats["device_count"],
            "adaptive_polling_interval": stats["adaptive_polling_interval"],
            "last_reset_date": last_reset,
            "rate_limit_status": stats["rate_limit_status"],
            "api_remaining_calls": stats.get("api_remaining_calls"),
            "api_reset_time": reset_time,
            "last_api_call_time": dt_util.now().isoformat()
        }

class GoveePollingIntervalSensor(SensorEntity):
    """Sensor for tracking Govee polling interval."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(self, rate_limiter: GoveeRateLimiter) -> None:
        """Initialize the sensor."""
        self._rate_limiter = rate_limiter
        self._attr_unique_id = "govee_polling_interval"
        self._attr_name = "Govee Polling Interval"
        self._attr_should_poll = True

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self._rate_limiter.polling_interval

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        stats = self._rate_limiter.usage_stats
        return {
            "device_count": stats["device_count"],
            "safe_limit": stats["safe_limit"],
            "adaptive_interval": stats["adaptive_polling_interval"],
        }

    async def async_update(self) -> None:
        """Update the sensor."""
        # The rate limiter maintains its own state
        pass
