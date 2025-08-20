"""Rate limiter for Govee API."""
from datetime import datetime, timedelta
import logging
from typing import Optional
import asyncio
import math

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.const import STATE_UNKNOWN
from homeassistant.components.sensor import SensorEntity
from homeassistant.util import dt as dt_util

_LOGGER = logging.getLogger(__name__)

# Constants
DAILY_LIMIT = 10000
SAFE_LIMIT = 8000  # Target to stay under this limit
MIN_POLLING_INTERVAL = 10  # Minimum seconds between updates
MAX_POLLING_INTERVAL = 300  # Maximum seconds between updates
RATE_LIMIT_BUFFER = 100  # Minimum requests to keep available

class GoveeRateLimiter:
    """Rate limiter for Govee API."""

    def __init__(self, hass: HomeAssistant):
        """Initialize rate limiter."""
        self.hass = hass
        self._total_calls = 0
        self._last_reset = dt_util.now()
        self._device_count = 0
        self._lock = asyncio.Lock()
        self._current_polling_interval = MIN_POLLING_INTERVAL
        self._api_reset_time: Optional[datetime] = None
        self._api_remaining_calls: Optional[int] = None

    @property
    def daily_requests_per_device(self) -> int:
        """Calculate safe number of requests per device per day."""
        if self._device_count == 0:
            return 0
        # Reserve 20% of SAFE_LIMIT for manual operations and headroom
        safe_requests = int(SAFE_LIMIT * 0.8)
        return safe_requests // self._device_count

    def calculate_polling_interval(self) -> int:
        """Calculate optimal polling interval based on device count and usage."""
        if self._device_count == 0:
            return MAX_POLLING_INTERVAL

        # Calculate requests per device per day
        requests_per_device = self.daily_requests_per_device

        # Calculate seconds per day per device
        seconds_per_day = 24 * 60 * 60
        
        # Calculate ideal interval
        ideal_interval = seconds_per_day / requests_per_device if requests_per_device > 0 else MAX_POLLING_INTERVAL

        # Adjust based on current usage
        if self._total_calls > 0:
            time_elapsed = (dt_util.now() - self._last_reset).total_seconds()
            current_rate = self._total_calls / time_elapsed if time_elapsed > 0 else 0
            projected_daily_calls = current_rate * seconds_per_day

            if projected_daily_calls > SAFE_LIMIT:
                # Increase interval to slow down
                ideal_interval *= 1.5
            elif projected_daily_calls < SAFE_LIMIT * 0.7:
                # Room to decrease interval
                ideal_interval *= 0.8

        # Ensure interval stays within bounds
        return max(MIN_POLLING_INTERVAL, min(int(ideal_interval), MAX_POLLING_INTERVAL))

    async def update_device_count(self, count: int) -> None:
        """Update the number of devices being managed."""
        async with self._lock:
            self._device_count = count
            self._current_polling_interval = self.calculate_polling_interval()

    def update_api_limits(self, remaining_calls: Optional[int], reset_time: Optional[datetime]) -> None:
        """Update API limits from response headers."""
        self._api_remaining_calls = remaining_calls
        self._api_reset_time = reset_time

    async def increment_call_count(self) -> None:
        """Increment the API call counter."""
        async with self._lock:
            now = dt_util.now()
            
            # Check if we need to reset counters
            if now.date() > self._last_reset.date():
                self._total_calls = 0
                self._last_reset = now

            self._total_calls += 1
            
            # Recalculate polling interval every 100 calls
            if self._total_calls % 100 == 0:
                self._current_polling_interval = self.calculate_polling_interval()

    async def can_make_request(self) -> bool:
        """Check if we can make a new API request."""
        async with self._lock:
            # If we have API remaining calls info, use it
            if self._api_remaining_calls is not None:
                if self._api_remaining_calls <= RATE_LIMIT_BUFFER:
                    return False

            # Check our local tracking
            now = dt_util.now()
            if now.date() > self._last_reset.date():
                self._total_calls = 0
                self._last_reset = now
                return True

            # Use projected daily calls to determine if we can make a request
            time_elapsed = (now - self._last_reset).total_seconds()
            if time_elapsed > 0:
                current_rate = self._total_calls / time_elapsed
                projected_daily_calls = current_rate * 24 * 60 * 60
                return projected_daily_calls < SAFE_LIMIT

            return self._total_calls < SAFE_LIMIT

    @property
    def polling_interval(self) -> int:
        """Get current polling interval."""
        return self._current_polling_interval

    @property
    def usage_stats(self) -> dict:
        """Get current usage statistics."""
        now = dt_util.now()
        time_elapsed = (now - self._last_reset).total_seconds()
        projected_daily_calls = 0
        if time_elapsed > 0:
            current_rate = self._total_calls / time_elapsed
            projected_daily_calls = int(current_rate * 24 * 60 * 60)

        return {
            "total_calls_today": self._total_calls,
            "remaining_calls": SAFE_LIMIT - self._total_calls,
            "usage_percentage": (self._total_calls / SAFE_LIMIT) * 100,
            "daily_limit": DAILY_LIMIT,
            "safe_limit": SAFE_LIMIT,
            "device_count": self._device_count,
            "adaptive_polling_interval": self._current_polling_interval,
            "last_reset_date": self._last_reset.isoformat(),
            "projected_daily_calls": projected_daily_calls,
            "rate_limit_status": self._get_status(),
            "api_remaining_calls": self._api_remaining_calls,
            "api_reset_time": self._api_reset_time.isoformat() if self._api_reset_time else None
        }

    def _get_status(self) -> str:
        """Get the current rate limit status."""
        if self._total_calls >= SAFE_LIMIT:
            return "CRITICAL"
        elif self._total_calls >= SAFE_LIMIT * 0.8:
            return "WARNING"
        return "NORMAL"
