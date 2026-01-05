from __future__ import annotations

DOMAIN = "hcm_rated_tracker"

ATTR_TITLE = "title"
ATTR_EXTRA = "extra"
ATTR_RATING = "rating"

# YAML source of truth (relative to /config)
DEFAULT_YAML_REL_PATH = "hcm_rated_tracker/books.yaml"

PLATFORMS: list[str] = ["text", "number", "button"]
