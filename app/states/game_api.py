import reflex as rx
import json
import logging
import math
from urllib.parse import urlsplit
import requests


# API helper: validate a public-facing base URL without accepting credentials.
def base_url(value: str) -> str:
    value = value.strip().rstrip("/")
    if not value:
        raise ValueError("Enter your deployed FastAPI backend URL.")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as e:
        logging.exception(f"Error: {e}")
        raise ValueError("The backend URL is invalid.") from e
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Use a complete http:// or https:// URL without credentials, query parameters, or fragments."
        )
    return value


# Data normalization: unwrap JSON strings while retaining arbitrary lists and dictionaries.
def normalize(value: object) -> object:
    for _ in range(5):
        if not isinstance(value, str):
            break
        text = value.strip()
        if text.startswith("```"):
            text = (
                text.removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
        try:
            value = json.loads(text)
        except (ValueError, TypeError) as e:
            logging.exception(f"Error: {e}")
            raise ValueError(
                "The backend returned malformed JSON inside a response field."
            ) from e
    return value


# API helper: real HTTP requests, bounded waits, and safe user-facing failures.
def post_json(url: str, path: str, payload: dict) -> dict:
    try:
        response = requests.post(
            f"{base_url(url)}{path}",
            json=payload,
            timeout=(5, 35),
            allow_redirects=False,
        )
        response.raise_for_status()
        if not 200 <= response.status_code < 300:
            raise ValueError(
                "The backend redirected the request. Use its final service URL."
            )
        data = response.json()
    except requests.Timeout as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            "The backend timed out. Please retry when the service is ready."
        ) from e
    except requests.ConnectionError as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            "Could not connect. Check the public backend URL and that the service is running."
        ) from e
    except requests.HTTPError as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            f"The backend returned HTTP {e.response.status_code}. Check the service and try again."
        ) from e
    except requests.exceptions.JSONDecodeError as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            "The backend returned malformed JSON instead of a JSON response."
        ) from e
    except requests.RequestException as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            "The request could not be completed. Check your backend URL."
        ) from e
    if not isinstance(data, dict):
        raise ValueError("Unexpected response: expected a JSON object.")
    return data


# Data normalization: canonical JSON documents preserve every backend field in state.
def document(value: object) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2)
    except (TypeError, ValueError) as e:
        logging.exception(f"Error: {e}")
        raise ValueError(
            "The backend returned data that is not valid JSON."
        ) from e


# Data normalization: character responses must identify two distinct integer fighters.
def record(value: object) -> dict:
    value = normalize(value)
    if isinstance(value, list) and len(value) == 1:
        value = normalize(value[0])
    if not isinstance(value, dict) or type(value.get("id")) is not int:
        raise ValueError(
            "Unexpected fighter data: each fighter must have an integer id."
        )
    return value


# Data normalization: read known health fields without inventing missing stats.
def health(data: dict) -> float | None:
    for key in ("current_health", "health", "hp"):
        value = data.get(key)
        if isinstance(value, (int, float, str)) and not isinstance(value, bool):
            try:
                number = float(value)
                if math.isfinite(number):
                    return number
            except ValueError:
                pass
    return None


# Data normalization: merge explicit record updates, retaining nested attributes.
def merge_record(current: dict, update: dict) -> dict:
    merged = dict(current)
    for key, value in update.items():
        if key == "id":
            continue
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_record(merged[key], value)
        else:
            merged[key] = value
    return merged


FIGHTERS = [
    {
        "id": 1,
        "name": "Cinder",
        "element": "FIRE / BRAWLER",
        "image": "/character_square_game.png",
        "tag": "A little spark. A lot of fight.",
        "label": "FIGHTER ID 001",
    },
    {
        "id": 2,
        "name": "Volt",
        "element": "ELECTRIC / SPEEDSTER",
        "image": "/character_yellow_square.png",
        "tag": "Small fuse. Lightning moves.",
        "label": "FIGHTER ID 002",
    },
    {
        "id": 3,
        "name": "Moss",
        "element": "EARTH / GUARDIAN",
        "image": "/square_game_character.png",
        "tag": "Rooted in a fighting spirit.",
        "label": "FIGHTER ID 003",
    },
    {
        "id": 4,
        "name": "Marina",
        "element": "WATER / EXPLORER",
        "image": "/marina_water_explorer.png",
        "tag": "Make waves. Break limits.",
        "label": "FIGHTER ID 004",
    },
]


# Fighter panel data: API details take priority; local art supplies presentation only.
def fighter_view(
    raw: str, fallback_id: int, initial_hp: float
) -> dict[str, str]:
    data = json.loads(raw)
    local = FIGHTERS[(fallback_id - 1) % 4]
    hp = health(data)
    maximum = health(
        {"health": data.get("max_health", data.get("max_hp", initial_hp))}
    )
    maximum = maximum if maximum is not None and maximum > 0 else 0
    image = data.get("image_url", data.get("image", ""))
    if not isinstance(image, str) or not image.startswith(
        ("https://", "http://")
    ):
        image = local["image"]
    stats = data.get("attributes", {})
    stats = stats if isinstance(stats, dict) else {}
    chips = []
    for label, keys in [
        ("ATK", ("attack",)),
        ("DEF", ("defence", "defense")),
        ("SPD", ("speed",)),
        ("STA", ("stamina",)),
    ]:
        for key in keys:
            value = data.get(key, stats.get(key))
            if isinstance(value, (int, float, str)):
                chips.append(f"{label} {value}")
                break
    return {
        "name": str(data.get("name") or local["name"]),
        "id": str(data.get("id", fallback_id)),
        "image": image,
        "element": local["element"],
        "health": "HP not provided" if hp is None else f"{hp:g} HP",
        "percent": str(max(0, min(100, hp / maximum * 100)))
        if hp is not None and maximum
        else "0",
        "basis": "Health unavailable"
        if hp is None
        else (
            "Relative to max / starting HP"
            if maximum
            else "No maximum HP supplied"
        ),
        "stats": " · ".join(chips) or "Attributes not provided",
    }
