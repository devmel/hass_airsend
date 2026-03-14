"""AirSend sensors."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.const import CONF_INTERNAL_URL, UnitOfTemperature, LIGHT_LUX

from .device import Device
from . import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AirSend sensors from a config entry."""
    internal_url = entry.data.get(CONF_INTERNAL_URL, "")
    devices_config = entry.data.get("devices", {})

    entities = []
    for name, options in devices_config.items():
        device = Device(name, options, internal_url)

        # Generic external sensor (type 1)
        if device.is_sensor:
            entities.append(AirSendAnySensor(hass, device))

        # AirSend box sensors (type 0) — optional temp/illuminance
        if device.is_airsend:
            sensors = False
            try:
                sensors = eval(str(options.get("sensors", False)))
            except Exception:
                pass
            if sensors:
                entities.append(AirSendTempSensor(hass, device))
                entities.append(AirSendIllSensor(hass, device))

    async_add_entities(entities)


class AirSendAnySensor(SensorEntity):
    """Generic AirSend sensor (type 1)."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._device = device
        self._unique_id = DOMAIN + "_" + str(device.unique_channel_name) + "_sensor"
        self.entity_id = generate_entity_id("sensor.{}", device.unique_channel_name, hass=hass)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name

    @property
    def extra_state_attributes(self):
        return self._device.extra_state_attributes

    @property
    def available(self):
        return True

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info


class AirSendTempSensor(SensorEntity):
    """AirSend device temperature sensor."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._device = device
        uname = DOMAIN + "_" + str(device.unique_channel_name) + "_temp"
        self._unique_id = uname
        self._coordinator = DataUpdateCoordinator(
            hass, _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=12),
        )
        self._coordinator.async_add_listener(lambda: None)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name + "_temp"

    @property
    def available(self):
        return True

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_unit_of_measurement(self):
        return UnitOfTemperature.CELSIUS

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    async def async_update_data(self):
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "TEMPERATURE"}
        await self._coordinator.hass.async_add_executor_job(
            lambda: self._device.transfer(note, self.entity_id)
        )


class AirSendIllSensor(SensorEntity):
    """AirSend device illuminance sensor."""

    def __init__(self, hass: HomeAssistant, device: Device) -> None:
        self._device = device
        uname = DOMAIN + "_" + str(device.unique_channel_name) + "_ill"
        self._unique_id = uname
        self._coordinator = DataUpdateCoordinator(
            hass, _LOGGER,
            name=uname,
            update_method=self.async_update_data,
            update_interval=timedelta(seconds=12),
        )
        self._coordinator.async_add_listener(lambda: None)

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        return self._device.name + "_ill"

    @property
    def available(self):
        return True

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.ILLUMINANCE

    @property
    def native_unit_of_measurement(self):
        return LIGHT_LUX

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    async def async_update_data(self):
        self._coordinator.update_interval = timedelta(seconds=self._device.refresh_value)
        note = {"method": "QUERY", "type": "ILLUMINANCE"}
        await self._coordinator.hass.async_add_executor_job(
            lambda: self._device.transfer(note, self.entity_id)
        )
