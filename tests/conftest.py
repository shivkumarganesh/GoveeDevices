"""Test configuration for Govee integration."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from homeassistant.const import CONF_API_KEY
from custom_components.govee.const import DOMAIN

@pytest.fixture
def mock_setup_entry():
    """Mock setup entry."""
    return AsyncMock(return_value=True)

@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    return MagicMock(
        data={CONF_API_KEY: "mock-api-key"},
        entry_id="test_entry_id",
        domain=DOMAIN,
    )

@pytest.fixture
def mock_api_response():
    """Mock API response."""
    return {
        "code": 200,
        "message": "success",
        "data": {
            "devices": [
                {
                    "device": "AA:BB:CC:DD:EE:FF:00:11",
                    "model": "H6159",
                    "deviceName": "Mock Light 1",
                    "controllable": True,
                    "retrievable": True,
                    "supportCmds": ["turn", "brightness", "color"],
                    "properties": {
                        "powerState": "on",
                        "brightness": 50,
                        "color": {"r": 255, "g": 255, "b": 255}
                    }
                }
            ]
        }
    }

@pytest.fixture
def mock_rate_limiter():
    """Create a mock rate limiter."""
    rate_limiter = MagicMock()
    rate_limiter.can_make_request = AsyncMock(return_value=True)
    rate_limiter.increment_call_count = AsyncMock()
    rate_limiter.update_api_limits = MagicMock()
    return rate_limiter
