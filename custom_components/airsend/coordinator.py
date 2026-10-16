"""AirSend DataUpdateCoordinator."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .device import Device
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)

# Devices that only push state (covers) are probed for reachability:
# retry quickly while the bridge looks down so entities recover on their own.
_AVAILABILITY_RETRY_SECONDS = 30
_AVAILABILITY_FAILURE_THRESHOLD = 2


class AirSendCoordinator(DataUpdateCoordinator):
    """Coordinator for a single AirSend device — polls state, temp and illuminance."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device.unique_channel_name}",
            update_interval=timedelta(seconds=device.refresh_value),
        )
        self._device = device
        self._availability_failures = 0
        # Data structure shared across all entities of this device
        self.data = {
            "state": None,
            "temperature": None,
            "illuminance": None,
            "available": True,
        }

    @property
    def device(self) -> Device:
        return self._device

    async def _async_update_data(self) -> dict:
        """Fetch data from device — called automatically by the coordinator."""
        data = dict(self.data)  # keep last known values

        # Query state
        if self._device.is_airsend:
            try:
                await self._device.async_transfer(
                    {"method": "QUERY", "type": "STATE"},
                    f"coordinator_{self._device.unique_channel_name}",
                )
                await self._device.async_bind()
                data["available"] = True
            except Exception as err:
                data["available"] = False
                raise UpdateFailed(f"Error querying state for {self._device.name}: {err}") from err

        # Probe reachability so covers (push only) recover on their own
        if self._device.is_cover:
            if await self._device.async_probe():
                data["available"] = True
                self._availability_failures = 0
                self.update_interval = timedelta(seconds=self._device.refresh_value)
            else:
                self._availability_failures += 1
                if self._availability_failures >= _AVAILABILITY_FAILURE_THRESHOLD:
                    data["available"] = False
                self.update_interval = timedelta(seconds=_AVAILABILITY_RETRY_SECONDS)

        # Query temperature if sensors enabled
        if self._device.is_airsend and self._has_sensors:
            try:
                await self._device.async_transfer(
                    {"method": "QUERY", "type": "TEMPERATURE"},
                    f"coordinator_{self._device.unique_channel_name}_temp",
                )
                await self._device.async_transfer(
                    {"method": "QUERY", "type": "ILLUMINANCE"},
                    f"coordinator_{self._device.unique_channel_name}_ill",
                )
            except Exception as err:
                _LOGGER.warning("Sensor query failed for %s: %s", self._device.name, err)

        return data

    @callback
    def async_set_available(self, available: bool) -> None:
        """Update availability reported by entities after a transfer."""
        if available:
            self._availability_failures = 0
        if self.data.get("available", True) == available:
            return
        self.data["available"] = available
        self.async_update_listeners()

    @property
    def _has_sensors(self) -> bool:
        return self.data.get("temperature") is not None or self.data.get("illuminance") is not None

    def set_has_sensors(self, value: bool) -> None:
        """Called by sensor entities to indicate sensors are enabled."""
        if value:
            self.data["temperature"] = self.data.get("temperature")
            self.data["illuminance"] = self.data.get("illuminance")
