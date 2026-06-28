import json
from pathlib import Path


SETTINGS_PATH = Path(
    "config/settings.json"
)


DEFAULT_SETTINGS = {
    "update_interval": 45,
    "linked_brightness": True,
    "window_width": 650,
    "window_height": 500,
}


def load_settings():

    if not SETTINGS_PATH.exists():

        save_settings(
            DEFAULT_SETTINGS
        )

        return DEFAULT_SETTINGS

    try:
        with open(
            SETTINGS_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except Exception:
        return DEFAULT_SETTINGS


def save_settings(settings):

    SETTINGS_PATH.parent.mkdir(
        exist_ok=True
    )

    with open(
        SETTINGS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            settings,
            file,
            indent=4,
            ensure_ascii=False
        )