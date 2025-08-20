"""The Govee integration."""
from __future__ import annotations

import os
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .rate_limiter import GoveeRateLimiter

_LOGGER = logging.getLogger(__name__)

DOMAIN = "govee"
PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Govee integration."""
    # Register custom card
    card_dir = os.path.join(os.path.dirname(__file__), "www")
    if os.path.isdir(card_dir):
        hass.http.register_static_path(
            f"/govee-api-monitor-card.js",
            os.path.join(card_dir, "govee-api-monitor-card.js"),
            cache_headers=False,
        )
        _LOGGER.info("Registered Govee API Monitor card")
        
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Govee from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create rate limiter
    rate_limiter = GoveeRateLimiter(hass)
    
    # Store the api key and rate limiter
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": entry.data[CONF_API_KEY],
        "rate_limiter": rate_limiter
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
