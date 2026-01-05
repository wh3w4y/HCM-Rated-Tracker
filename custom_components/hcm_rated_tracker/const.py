DOMAIN = "hcm_rated_tracker"

CONF_PRESET = "preset"
CONF_TRACKER_NAME = "tracker_name"
CONF_ITEM_LABEL = "item_label"
CONF_EXTRA_LABEL = "extra_label"

CONF_MIN_RATING = "min_rating"
CONF_RECENT_COUNT = "recent_count"
CONF_SAME_LANE_COUNT = "same_lane_count"
CONF_DIFFERENT_GENRE_COUNT = "different_genre_count"
CONF_OPENAI_CONFIG_ENTRY = "openai_config_entry"

DEFAULT_MIN_RATING = 8
DEFAULT_RECENT_COUNT = 12
DEFAULT_SAME_LANE_COUNT = 6
DEFAULT_DIFFERENT_GENRE_COUNT = 4

STORAGE_VERSION = 1

ATTR_TITLE = "title"
ATTR_EXTRA = "extra"
ATTR_RATING = "rating"

PRESETS = {
    "books": {"tracker_name": "Books", "item_label": "book", "extra_label": "Author"},
    "films": {"tracker_name": "Films", "item_label": "film", "extra_label": "Director"},
    "music": {"tracker_name": "Music", "item_label": "album", "extra_label": "Artist"},
    "tv": {"tracker_name": "TV", "item_label": "show", "extra_label": "Series"},
    "games": {"tracker_name": "Games", "item_label": "game", "extra_label": "Platform"},
    "other": {"tracker_name": "Tracker", "item_label": "item", "extra_label": "Extra"}
}
