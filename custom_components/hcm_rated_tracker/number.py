from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .entity import BaseTrackerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([RatingEntity(entry.entry_id)])


class RatingEntity(BaseTrackerEntity, NumberEntity):
    _attr_name = "Rating"
    _attr_native_min_value = 0
    _attr_native_max_value = 10
    _attr_native_step = 1

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.hass.bus.async_listen(f"{DOMAIN}_updated_{self._entry_id}", self._handle_update))

    @callback
    def _handle_update(self, event) -> None:
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        return float(self.hass.data[DOMAIN][self._entry_id].current_rating)

    async def async_set_native_value(self, value: float) -> None:
        m = self.hass.data[DOMAIN][self._entry_id]
        m.current_rating = int(value)
        m._fire_update()
