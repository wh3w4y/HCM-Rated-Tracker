from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .entity_base import HcmRatedTrackerEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            RecommendationsSensor(hass, entry),
            LogSensor(hass, entry),
        ],
        True,
    )


class RecommendationsSensor(HcmRatedTrackerEntity, SensorEntity):
    _attr_name = "Recommendations"
    _attr_icon = "mdi:lightbulb-on-outline"

    @property
    def native_value(self) -> str | None:
        # keep state short-ish (optional), put full text in attribute
        text = getattr(self.manager.state, "recommendations", "") or ""
        return "Ready" if text else "Empty"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "text": getattr(self.manager.state, "recommendations", "") or ""
        }


class LogSensor(HcmRatedTrackerEntity, SensorEntity):
    _attr_name = "Log"
    _attr_icon = "mdi:format-list-bulleted"

    @property
    def native_value(self) -> str | None:
        text = self.manager.format_log() if hasattr(self.manager, "format_log") else ""
        return "Ready" if text else "Empty"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "text": self.manager.format_log() if hasattr(self.manager, "format_log") else ""
        }
