"""AirSend sensors."""
from typing import Any
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.typing import ConfigType
from homeassistant.const import CONF_DEVICES, CONF_INTERNAL_URL, UnitOfTemperature, LIGHT_LUX

from .device import Device

from . import DOMAIN
import logging
_LOGGER = logging.getLogger(DOMAIN)

async def async_setup_platform(
    hass: HomeAssistant, config: ConfigType, async_add_entities, discovery_info=None
) -> None:
    if discovery_info is None:
        return
    for name, options in discovery_info[CONF_DEVICES].items():
        device = Device(name, options, discovery_info[CONF_INTERNAL_URL])
        if device.is_airsend:
            entity = AirSendStateSensor(hass, device)
            async_add_entities([entity])
            sensors = False
            try:
                sensors = eval(str(options["sensors"]))
            except KeyError:
                pass
            if sensors == True:
                entityTmp = AirSendTempSensor(hass, device)
                entityIll = AirSendIllSensor(hass, device)
                async_add_entities([entityTmp, entityIll])
        if device.is_sensor:
            entity = AirSendAnySensor(hass, device)
            async_add_entities([entity])

class AirSendAnySensor(SensorEntity):
    """Representation of an AirSend device temperature."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a sensor."""
        self._device = device
        uname = DOMAIN + device.name
        self._unique_id = "_".join(x for x in uname)
        self.entity_id = generate_entity_id("sensor.{}", self._device.unique_channel_name, hass=hass)

    @property
    def unique_id(self):
        """Return unique identifier of device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._device.name

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        return self._device.extra_state_attributes

    @property
    def available(self):
        return True

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False


class AirSendStateSensor(BinarySensorEntity):
    """Representation of an AirSend device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a sensor."""
        self.hass = hass
        self._bind = None
        self._device = device
        uname = DOMAIN + device.name + "_state"
        self._unique_id = "_".join(x for x in uname)
        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=10), 
        )
        def null_callback():
            return
        self._coordinator.async_add_listener(null_callback)

    @property
    def unique_id(self):
        """Return unique identifier of device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._device.name + "_state"

    @property
    def device_class(self) -> BinarySensorDeviceClass | None:
        """Cette entité"""
        return BinarySensorDeviceClass.RUNNING

    @property
    def available(self):
        return True

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    async def async_update_data(self):
        """Register update callback."""
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "STATE"}
        await self.hass.async_add_executor_job( lambda: self._device.transfer(note, self.entity_id) )
        await self.hass.async_add_executor_job( lambda: self._device.bind() )


class AirSendTempSensor(SensorEntity):
    """Representation of an AirSend device temperature."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a sensor."""
        self._device = device
        uname = DOMAIN + device.name + "_temp"
        self._unique_id = "_".join(x for x in uname)
        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=12), 
        )
        def null_callback():
            return
        self._coordinator.async_add_listener(null_callback)

    @property
    def unique_id(self):
        """Return unique identifier of device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._device.name + "_temp"

    @property
    def available(self):
        return True

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Cette entité"""
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        """Return measurement unit."""
        return UnitOfTemperature.CELSIUS

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    async def async_update_data(self):
        """Register update callback."""
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "TEMPERATURE"}
        await self.hass.async_add_executor_job( lambda: self._device.transfer(note, self.entity_id) )


class AirSendIllSensor(SensorEntity):
    """Representation of an AirSend device temperature."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Device,
    ) -> None:
        """Initialize a sensor."""
        self._device = device
        uname = DOMAIN + device.name + "_ill"
        self._unique_id = "_".join(x for x in uname)
        self._coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=12), 
        )
        def null_callback():
            return
        self._coordinator.async_add_listener(null_callback)

    @property
    def unique_id(self):
        """Return unique identifier of device."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._device.name + "_ill"

    @property
    def available(self):
        return True

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Cette entité"""
        return SensorDeviceClass.ILLUMINANCE

    @property
    def native_unit_of_measurement(self):
        """Return measurement unit."""
        return LIGHT_LUX

    @property
    def should_poll(self) -> bool:
        """Return the polling state."""
        return False

    async def async_update_data(self):
        """Register update callback."""
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "ILLUMINANCE"}
        await self.hass.async_add_executor_job( lambda: self._device.transfer(note, self.entity_id) )
