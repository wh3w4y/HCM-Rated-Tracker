from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import RatedTrackerEntity
from .storage import RatedTrackerStore


def _store(hass: HomeAssistant, entry: ConfigEntry) -> RatedTrackerStore:
    return hass.data[DOMAIN][entry.entry_id]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    store = _store(hass, entry)
    async_add_entities(
        [
            EntriesCountSensor(store, entry.entry_id),
            LastAddedSensor(store, entry.entry_id),
            LogSensor(store, entry.entry_id),
        ],
        True,
    )


class _StoreBackedSensor(RatedTrackerEntity, SensorEntity):
    def __init__(self, store: RatedTrackerStore, entry_id: str, unique_suffix: str) -> None:
        super().__init__(store, entry_id, unique_suffix)
        self._unsub = None

    async def async_added_to_hass(self) -> None:
        @callback
        def _changed() -> None:
            self.async_write_ha_state()

        self._unsub = self._store.add_listener(_changed)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None


class EntriesCountSensor(_StoreBackedSensor):
    _attr_name = "Entries"
    _attr_icon = "mdi:format-list-numbered"
    _attr_native_unit_of_measurement = "books"

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "entries_count")

    @property
    def native_value(self) -> int:
        return len(self._store.entries)


class LastAddedSensor(_StoreBackedSensor):
    _attr_name = "Last Added"
    _attr_icon = "mdi:clock-plus"

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "last_added")

    @property
    def native_value(self) -> str | None:
        if not self._store.entries:
            return None
        e = self._store.entries[0]
        author = e.author or "Unknown"
        return f"{e.title} — {author} — {e.rating}/10"


class LogSensor(_StoreBackedSensor):
    _attr_name = "Log"
    _attr_icon = "mdi:text-long"

    def __init__(self, store: RatedTrackerStore, entry_id: str) -> None:
        super().__init__(store, entry_id, "log")

    @property
    def native_value(self) -> str | None:
        # Sensor state is limited in length; keep it short.
        if not self._store.log:
            return None
        first_line = self._store.log.splitlines()[0]
        return first_line[:255]

    @property
    def extra_state_attributes(self):
        return {"full_log": self._store.log}
