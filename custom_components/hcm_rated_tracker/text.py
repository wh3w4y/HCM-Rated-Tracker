from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, CONF_EXTRA_LABEL
from .entity import BaseTrackerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([TitleEntity(entry.entry_id), ExtraEntity(entry.entry_id), LogEntity(entry.entry_id), RecommendationsEntity(entry.entry_id)])


class _BaseText(BaseTrackerEntity, TextEntity):
    _attr_mode = "text"
    _attr_native_min = 0
    _attr_native_max = 255

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.hass.bus.async_listen(f"{DOMAIN}_updated_{self._entry_id}", self._handle_update))

    @callback
    def _handle_update(self, event) -> None:
        self.async_write_ha_state()


class TitleEntity(_BaseText):
    _attr_name = "Title"

    @property
    def native_value(self) -> str:
        return self.hass.data[DOMAIN][self._entry_id].current_title

    async def async_set_value(self, value: str) -> None:
        m = self.hass.data[DOMAIN][self._entry_id]
        m.current_title = value.strip()
        m._fire_update()


class ExtraEntity(_BaseText):
    _attr_name = "Extra"

    @property
    def native_value(self) -> str:
        return self.hass.data[DOMAIN][self._entry_id].current_extra

    async def async_set_value(self, value: str) -> None:
        m = self.hass.data[DOMAIN][self._entry_id]
        m.current_extra = value.strip()
        m._fire_update()

    @property
    def extra_state_attributes(self):
        m = self.hass.data[DOMAIN][self._entry_id]
        return {"label": m.opts[CONF_EXTRA_LABEL]}


class LogEntity(_BaseText):
    _attr_name = "Log"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str:
        return self.hass.data[DOMAIN][self._entry_id].format_log()

    async def async_set_value(self, value: str) -> None:
        return


class RecommendationsEntity(_BaseText):
    _attr_name = "Recommendations"
    _attr_native_max = 100000

    @property
    def native_value(self) -> str:
        return self.hass.data[DOMAIN][self._entry_id].state.recommendations or ""

    async def async_set_value(self, value: str) -> None:
        m = self.hass.data[DOMAIN][self._entry_id]
        m.state.recommendations = value
        await m.storage.save(m.state)
        m._fire_update()
