"""Sensors for Govee integration."""
from __future__ import annotations

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

from . import DOMAIN
from .rate_limiter import GoveeRateLimiter

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
