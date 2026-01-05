from __future__ import annotations

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN, SIGNAL_UPDATED


class TrackerEntity(Entity):
    def __init__(self, manager, name: str, unique_suffix: str) -> None:
        self.manager = manager
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{manager.entry_id}_{unique_suffix}"
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        self._unsub = async_dispatcher_connect(
            self.hass, SIGNAL_UPDATED, self._handle_update
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None

    def _handle_update(self, entry_id: str) -> None:
        if entry_id == self.manager.entry_id:
            self.async_write_ha_state()
