from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .entity_base import TrackerEntity


class SaveButton(TrackerEntity, ButtonEntity):
    _attr_icon = "mdi:content-save"

    def __init__(self, manager):
        super().__init__(manager, "Save", "save")

    async def async_press(self) -> None:
        await self.manager.commit_draft()


class RecommendButton(TrackerEntity, ButtonEntity):
    _attr_icon = "mdi:wand"

    def __init__(self, manager):
        super().__init__(manager, "Recommend", "recommend")

    async def async_press(self) -> None:
        await self.manager.generate_recommendations()


async def async_setup_entry(hass, entry, async_add_entities):
    manager = hass.data["hcm_rated_tracker"][entry.entry_id]
    async_add_entities([SaveButton(manager), RecommendButton(manager)], True)
