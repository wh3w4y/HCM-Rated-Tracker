from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "hcm_rated_tracker"

ATTR_TITLE = "title"
ATTR_EXTRA = "extra"
ATTR_RATING = "rating"

# YAML source of truth (relative to HA config folder)
# (For you this is effectively /homeassistant)
DEFAULT_YAML_REL_PATH = "hcm_rated_tracker/books.yaml"

PLATFORMS: list[Platform] = [
    Platform.TEXT,
    Platform.NUMBER,
    Platform.BUTTON,
]
