from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .entity_base import HcmRatedTrackerEntity

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    async_add_entities([RatingNumber(hass, entry)])

class RatingNumber(HcmRatedTrackerEntity, NumberEntity):
    _attr_name = "Rating"
    _attr_icon = "mdi:star"
    _attr_min_value = 0
    _attr_max_value = 10
    _attr_step = 1
    _attr_mode = "slider"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, entry)
        self._value = 0

    @property
    def native_value(self) -> float | None:
        return self._value

    async def async_set_native_value(self, value: float) -> None:
        self._value = int(value)
        self.async_write_ha_state()
