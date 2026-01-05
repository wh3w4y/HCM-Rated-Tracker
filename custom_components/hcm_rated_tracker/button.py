from __future__ import annotations

from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .entity import BaseTrackerEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    async_add_entities([SaveButton(entry.entry_id), GenerateButton(entry.entry_id)])


class _BaseButton(BaseTrackerEntity, ButtonEntity):
    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.hass.bus.async_listen(f"{DOMAIN}_updated_{self._entry_id}", self._handle_update))

    @callback
    def _handle_update(self, event) -> None:
        self.async_write_ha_state()


class SaveButton(_BaseButton):
    _attr_name = "Save"

    async def async_press(self) -> None:
        m = self.hass.data[DOMAIN][self._entry_id]
        title = (m.current_title or "").strip()
        extra = (m.current_extra or "").strip()
        rating = int(m.current_rating or 0)
        if len(title) < 2 or rating < 1:
            return

        await m.add_entry(
            date=datetime.now().strftime("%Y-%m-%d"),
            title=title,
            extra=extra,
            rating=rating,
        )

        m.current_title = ""
        m.current_extra = ""
        m.current_rating = 0
        m._fire_update()

        await m.generate_recommendations()


class GenerateButton(_BaseButton):
    _attr_name = "Generate recommendations"

    async def async_press(self) -> None:
        await self.hass.data[DOMAIN][self._entry_id].generate_recommendations()
