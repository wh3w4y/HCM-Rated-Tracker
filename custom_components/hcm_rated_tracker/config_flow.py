from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    PRESETS,
    CONF_PRESET,
    CONF_TRACKER_NAME,
    CONF_ITEM_LABEL,
    CONF_EXTRA_LABEL,
    CONF_MIN_RATING,
    CONF_RECENT_COUNT,
    CONF_SAME_LANE_COUNT,
    CONF_DIFFERENT_GENRE_COUNT,
    CONF_OPENAI_CONFIG_ENTRY,
    DEFAULT_MIN_RATING,
    DEFAULT_RECENT_COUNT,
    DEFAULT_SAME_LANE_COUNT,
    DEFAULT_DIFFERENT_GENRE_COUNT,
)

PRESET_CHOICES = list(PRESETS.keys())


class HcmRatedTrackerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._preset = "books"
        self._tracker_name = ""
        self._item_label = ""
        self._extra_label = ""

    async def async_step_user(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {vol.Required(CONF_PRESET, default="books"): vol.In(PRESET_CHOICES)}
                ),
            )

        self._preset = user_input[CONF_PRESET]
        preset = PRESETS.get(self._preset, PRESETS["other"])
        self._tracker_name = preset["tracker_name"]
        self._item_label = preset["item_label"]
        self._extra_label = preset["extra_label"]
        return await self.async_step_details()

    async def async_step_details(self, user_input=None):
        if user_input is None:
            return self.async_show_form(
                step_id="details",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_TRACKER_NAME, default=self._tracker_name): str,
                        vol.Required(CONF_ITEM_LABEL, default=self._item_label): str,
                        vol.Required(CONF_EXTRA_LABEL, default=self._extra_label): str,
                    }
                ),
            )

        data = {
            CONF_PRESET: self._preset,
            CONF_TRACKER_NAME: user_input[CONF_TRACKER_NAME].strip() or self._tracker_name,
            CONF_ITEM_LABEL: user_input[CONF_ITEM_LABEL].strip() or self._item_label,
            CONF_EXTRA_LABEL: user_input[CONF_EXTRA_LABEL].strip() or self._extra_label,
        }
        title = data[CONF_TRACKER_NAME]
        return self.async_create_entry(title=title, data=data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HcmRatedTrackerOptionsFlowHandler(config_entry)


class HcmRatedTrackerOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        d = self.config_entry.data
        o = self.config_entry.options

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_PRESET, default=o.get(CONF_PRESET, d.get(CONF_PRESET, "books"))): vol.In(PRESET_CHOICES),
                        vol.Required(CONF_TRACKER_NAME, default=o.get(CONF_TRACKER_NAME, d.get(CONF_TRACKER_NAME, "Tracker"))): str,
                        vol.Required(CONF_ITEM_LABEL, default=o.get(CONF_ITEM_LABEL, d.get(CONF_ITEM_LABEL, "item"))): str,
                        vol.Required(CONF_EXTRA_LABEL, default=o.get(CONF_EXTRA_LABEL, d.get(CONF_EXTRA_LABEL, "Extra"))): str,

                        vol.Required(CONF_OPENAI_CONFIG_ENTRY, default=o.get(CONF_OPENAI_CONFIG_ENTRY, "")): str,
                        vol.Required(CONF_MIN_RATING, default=o.get(CONF_MIN_RATING, DEFAULT_MIN_RATING)): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
                        vol.Required(CONF_RECENT_COUNT, default=o.get(CONF_RECENT_COUNT, DEFAULT_RECENT_COUNT)): vol.All(vol.Coerce(int), vol.Range(min=3, max=50)),
                        vol.Required(CONF_SAME_LANE_COUNT, default=o.get(CONF_SAME_LANE_COUNT, DEFAULT_SAME_LANE_COUNT)): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                        vol.Required(CONF_DIFFERENT_GENRE_COUNT, default=o.get(CONF_DIFFERENT_GENRE_COUNT, DEFAULT_DIFFERENT_GENRE_COUNT)): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
                    }
                ),
            )

        return self.async_create_entry(title="", data=user_input)
