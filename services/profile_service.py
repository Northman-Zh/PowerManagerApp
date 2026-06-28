import json
from pathlib import Path


PROFILES_PATH = Path(
    "config/profiles.json"
)


def load_profiles():

    if not PROFILES_PATH.exists():
        return {}

    try:
        with open(
            PROFILES_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(
                file
            )

    except Exception:
        return {}


def save_profiles(
    profiles
):
    PROFILES_PATH.parent.mkdir(
        exist_ok=True
    )

    with open(
        PROFILES_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profiles,
            file,
            indent=4,
            ensure_ascii=False
        )


def save_profile(
    profile_name,
    brightness_values
):

    profiles = (
        load_profiles()
    )

    profiles[
        profile_name
    ] = brightness_values

    save_profiles(
        profiles
    )