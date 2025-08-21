"""Tests for the Govee light platform."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
    ColorMode,
)
from custom_components.govee.light import GoveeLight, async_setup_entry

async def test_light_init(mock_config_entry, mock_rate_limiter):
    """Test light initialization."""
    hass = MagicMock()
    device_info = {
        "device": "AA:BB:CC:DD:EE:FF:00:11",
        "model": "H6159",
        "deviceName": "Test Light",
        "controllable": True,
        "retrievable": True,
        "supportCmds": ["turn", "brightness", "color"]
    }
    
    light = GoveeLight(hass, mock_config_entry, device_info)
    
    assert light.unique_id == "AA:BB:CC:DD:EE:FF:00:11"
    assert light.name == "Test Light"
    assert ColorMode.RGB in light.supported_color_modes
    assert light.supported_features == 0

async def test_light_turn_on(mock_config_entry, mock_rate_limiter):
    """Test light turn on."""
    hass = MagicMock()
    device_info = {
        "device": "AA:BB:CC:DD:EE:FF:00:11",
        "model": "H6159",
        "deviceName": "Test Light",
        "controllable": True,
        "retrievable": True,
        "supportCmds": ["turn", "brightness", "color"]
    }
    
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession") as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"code": 200})
        
        mock_session.return_value.put = AsyncMock(return_value=mock_response)
        
        light = GoveeLight(hass, mock_config_entry, device_info)
        await light.async_turn_on(brightness=255, rgb_color=(255, 0, 0))
        
        assert light.brightness == 255
        assert light.rgb_color == (255, 0, 0)

async def test_light_turn_off(mock_config_entry, mock_rate_limiter):
    """Test light turn off."""
    hass = MagicMock()
    device_info = {
        "device": "AA:BB:CC:DD:EE:FF:00:11",
        "model": "H6159",
        "deviceName": "Test Light",
        "controllable": True,
        "retrievable": True,
        "supportCmds": ["turn", "brightness", "color"]
    }
    
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession") as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={"code": 200})
        
        mock_session.return_value.put = AsyncMock(return_value=mock_response)
        
        light = GoveeLight(hass, mock_config_entry, device_info)
        await light.async_turn_off()
        
        assert not light.is_on

async def test_light_update(mock_config_entry, mock_rate_limiter):
    """Test light update."""
    hass = MagicMock()
    hass.data = {
        "govee": {
            "test_entry_id": {
                "rate_limiter": mock_rate_limiter
            }
        }
    }
    
    device_info = {
        "device": "AA:BB:CC:DD:EE:FF:00:11",
        "model": "H6159",
        "deviceName": "Test Light",
        "controllable": True,
        "retrievable": True,
        "supportCmds": ["turn", "brightness", "color"]
    }
    
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession") as mock_session:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json = AsyncMock(return_value={
            "data": {
                "properties": [
                    {"name": "powerState", "value": "on"},
                    {"name": "brightness", "value": 50},
                    {"name": "color", "value": {"r": 255, "g": 0, "b": 0}}
                ]
            }
        })
        mock_response.headers = {
            "Rate-Limit-Remaining": "100",
            "Rate-Limit-Reset": "1629500000"
        }
        
        mock_session.return_value.get = AsyncMock(return_value=mock_response)
        
        light = GoveeLight(hass, mock_config_entry, device_info)
        await light.async_update()
        
        assert light.is_on
        assert light.brightness == 127  # 50% of 255
        assert light.rgb_color == (255, 0, 0)

async def test_rate_limit_handling(mock_config_entry, mock_rate_limiter):
    """Test rate limit handling."""
    hass = MagicMock()
    hass.data = {
        "govee": {
            "test_entry_id": {
                "rate_limiter": mock_rate_limiter
            }
        }
    }
    
    device_info = {
        "device": "AA:BB:CC:DD:EE:FF:00:11",
        "model": "H6159",
        "deviceName": "Test Light",
        "controllable": True,
        "retrievable": True,
        "supportCmds": ["turn", "brightness", "color"]
    }
    
    # Test rate limit response
    with patch("homeassistant.helpers.aiohttp_client.async_get_clientsession") as mock_session:
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.headers = {
            "Rate-Limit-Remaining": "0",
            "Rate-Limit-Reset": "1629500000"
        }
        
        mock_session.return_value.get = AsyncMock(return_value=mock_response)
        
        light = GoveeLight(hass, mock_config_entry, device_info)
        await light.async_update()
        
        # Verify rate limiter was updated
        mock_rate_limiter.update_api_limits.assert_called_once()
