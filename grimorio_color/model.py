# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Modelo de datos compartido por el Grimorio de Color.

Sin dependencias de Krita ni de Qt: se puede probar con Python normal.
El mismo JSON lo leen la app web y el docker de Krita.
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any


ZONES: list[dict[str, str]] = [
    {"key": "skin", "label": "Piel", "default_body": "Cara y cuerpo"},
    {"key": "hair", "label": "Pelo", "default_body": "Pelo"},
    {"key": "eyes", "label": "Ojos", "default_body": "Ojos"},
    {"key": "outfit", "label": "Ropa", "default_body": "Cuerpo"},
    {"key": "armor", "label": "Armadura", "default_body": "Torso y brazos"},
    {"key": "accessories", "label": "Accesorios", "default_body": "Manos y cuello"},
    {"key": "intimate", "label": "Privado", "default_body": "Zona íntima"},
    {"key": "scars", "label": "Marcas y cicatrices", "default_body": "Según la marca"},
]
ZONE_BY_KEY = {zone["key"]: zone for zone in ZONES}
ZONE_KEYS = [zone["key"] for zone in ZONES]

ROLES: dict[str, str] = {
    "base": "Base",
    "shadow": "Sombra",
    "light": "Luz",
    "accent": "Acento",
    "detail": "Detalle",
}

BLENDS: dict[str, str] = {
    "normal": "Normal",
    "multiply": "Multiply",
    "add": "Add",
    "screen": "Screen",
    "overlay": "Overlay",
    "soft-light": "Soft Light",
    "color-dodge": "Color Dodge",
    "burn": "Burn",
    "linear-burn": "Linear Burn",
    "passthrough": "Pass Through",
}

# Krita usa IDs con guion bajo para estos modos.
KRITA_BLEND_IDS: dict[str, str] = {
    "normal": "normal",
    "multiply": "multiply",
    "add": "add",
    "screen": "screen",
    "overlay": "overlay",
    "soft-light": "soft_light",
    "color-dodge": "color_dodge",
    "burn": "burn",
    "linear-burn": "linear_burn",
    "passthrough": "pass_through",
}

BODY_PARTS: list[str] = [
    "Cara y cuerpo",
    "Cara",
    "Pelo",
    "Ojos",
    "Boca",
    "Torso",
    "Brazos",
    "Manos",
    "Piernas",
    "Pies",
    "Uñas",
    "Cicatrices",
    "Tatuajes",
    "Genitales",
    "Vello",
    "Ambiente",
    "Otro",
]

BASE_RECIPE: list[dict[str, Any]] = [
    {"name": "LINE", "blend": "normal", "opacity": 100, "purpose": "Lineart limpio"},
    {"name": "BASE", "blend": "normal", "opacity": 100, "purpose": "Colores planos"},
    {"name": "SHADOW", "blend": "multiply", "opacity": 45, "purpose": "Sombra general"},
    {"name": "AO", "blend": "multiply", "opacity": 25, "purpose": "Oclusión en grietas"},
    {"name": "LIGHT", "blend": "add", "opacity": 30, "purpose": "Luz principal"},
    {"name": "GLOW", "blend": "add", "opacity": 15, "purpose": "Brillo"},
    {"name": "FX", "blend": "overlay", "opacity": 20, "purpose": "Textura / ajuste"},
]

DEFAULT_ENVIRONMENT: dict[str, Any] = {
    "name": "",
    "time": "",
    "weather": "",
    "keyLight": "#ffb36b",
    "shadowTint": "#3a2a4d",
    "bounce": "#7a4a2a",
    "mood": "",
    "palette": [],
}


def _now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def default_data_dir() -> Path:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / "krita" / "grimorio-color"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "krita" / "grimorio-color"
    flatpak = Path.home() / ".var/app/org.kde.krita/data/krita"
    if flatpak.exists():
        return flatpak / "grimorio-color"
    return Path.home() / ".local/share/krita/grimorio-color"


DATA_FILE = default_data_dir() / "grimorio.json"
SEED_FILE = Path(__file__).resolve().parent / "seed.json"


def new_id(prefix: str = "id") -> str:
    return f"{prefix}-{os.urandom(6).hex()}"


def as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def as_str_list(value: Any, limit: int = 16) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = as_str(item)
        if text and text not in result:
            result.append(text)
        if len(result) >= limit:
            break
    return result


def normalize_hex(value: Any, fallback: str = "#808080") -> str:
    text = as_str(value)
    if not text:
        return fallback
    if not text.startswith("#"):
        text = "#" + text
    if re.fullmatch(r"#[0-9a-fA-F]{3}", text):
        text = "#" + "".join(char * 2 for char in text[1:])
    if re.fullmatch(r"#[0-9a-fA-F]{6}", text):
        return text.lower()
    return fallback


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    text = normalize_hex(value).lstrip("#")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def clamp_int(value: Any, low: int = 0, high: int = 100, default: int = 100) -> int:
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", as_str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "grimorio"


def gpl_safe(value: str, fallback: str = "Sin nombre") -> str:
    text = re.sub(r"[\t\r\n#]+", " ", as_str(value)).strip()
    return text or fallback


def zone_label(zone_key: str) -> str:
    if zone_key == "environment":
        return "Ambiente"
    zone = ZONE_BY_KEY.get(zone_key)
    return zone["label"] if zone else "Paleta"


def default_body_part(zone_key: str) -> str:
    if zone_key == "environment":
        return "Ambiente"
    zone = ZONE_BY_KEY.get(zone_key)
    return zone["default_body"] if zone else ""


def empty_palettes() -> dict[str, list[dict[str, Any]]]:
    return {zone_key: [] for zone_key in ZONE_KEYS}


def make_base_recipe() -> list[dict[str, Any]]:
    return [
        {
            "id": new_id("layer"),
            "name": item["name"],
            "blend": item["blend"],
            "opacity": item["opacity"],
            "purpose": item["purpose"],
        }
        for item in BASE_RECIPE
    ]


def default_environment() -> dict[str, Any]:
    env = dict(DEFAULT_ENVIRONMENT)
    env["palette"] = []
    return env


def normalize_swatch(raw: Any, zone_key: str, used_ids: set[str]) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    note = as_str(source.get("note"))
    purpose = as_str(source.get("purpose")) or note
    body_part = as_str(source.get("bodyPart")) or default_body_part(zone_key)
    role = as_str(source.get("role"))
    if role not in ROLES:
        role = "base"
    swatch = {
        "id": _unique_id(used_ids, source.get("id"), "color"),
        "name": as_str(source.get("name")) or "Sin nombre",
        "hex": normalize_hex(source.get("hex")),
        "role": role,
        "bodyPart": body_part,
        "purpose": purpose,
        "opacity": clamp_int(source.get("opacity"), 0, 100, 100),
        "note": note,
    }
    return swatch


def normalize_layer(raw: Any, used_ids: set[str]) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    blend = as_str(source.get("blend"))
    if blend not in BLENDS:
        blend = "normal"
    return {
        "id": _unique_id(used_ids, source.get("id"), "layer"),
        "name": as_str(source.get("name")) or "Capa",
        "blend": blend,
        "opacity": clamp_int(source.get("opacity"), 0, 100, 100),
        "purpose": as_str(source.get("purpose")),
    }


def normalize_environment(raw: Any, used_ids: set[str]) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    palette_raw = source.get("palette")
    palette = []
    if isinstance(palette_raw, list):
        palette = [
            normalize_swatch(item, "environment", used_ids)
            for item in palette_raw
            if isinstance(item, dict)
        ]
    return {
        "name": as_str(source.get("name")),
        "time": as_str(source.get("time")),
        "weather": as_str(source.get("weather")),
        "keyLight": normalize_hex(source.get("keyLight"), "#ffb36b"),
        "shadowTint": normalize_hex(source.get("shadowTint"), "#3a2a4d"),
        "bounce": normalize_hex(source.get("bounce"), "#7a4a2a"),
        "mood": as_str(source.get("mood")),
        "palette": palette,
    }


def normalize_image_ref(value: Any) -> str:
    text = as_str(value).replace("\\", "/")
    if not text:
        return ""
    path = Path(text)
    if path.is_absolute() or ".." in path.parts:
        return ""
    return str(path)


def images_dir() -> Path:
    return DATA_FILE.parent / "images"


def store_image(source: str | Path, prefix: str = "image") -> str:
    source_path = Path(source)
    if not source_path.is_file():
        raise ValueError("No se encontró la imagen.")
    extension = source_path.suffix.lower()
    if extension not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        raise ValueError("Formato de imagen no soportado.")
    target_dir = images_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    name = f"{prefix}-{new_id('img')}{extension}"
    shutil.copy2(source_path, target_dir / name)
    return f"images/{name}"


def resolve_image(reference: str | None) -> Path | None:
    text = normalize_image_ref(reference)
    if not text:
        return None
    path = DATA_FILE.parent / text
    return path if path.is_file() else None


def remove_image(reference: str | None) -> None:
    path = resolve_image(reference)
    if path is not None:
        try:
            path.unlink()
        except OSError:
            pass


def normalize_character(raw: Any, used_ids: set[str]) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    palettes = empty_palettes()
    palettes_raw = source.get("palettes")
    if isinstance(palettes_raw, dict):
        for zone_key in ZONE_KEYS:
            items = palettes_raw.get(zone_key)
            if isinstance(items, list):
                palettes[zone_key] = [
                    normalize_swatch(item, zone_key, used_ids)
                    for item in items
                    if isinstance(item, dict)
                ]

    recipe_raw = source.get("recipe")
    recipe = []
    if isinstance(recipe_raw, list):
        recipe = [
            normalize_layer(item, used_ids)
            for item in recipe_raw
            if isinstance(item, dict)
        ]

    examples_raw = source.get("zoneExamples")
    zone_examples: dict[str, str] = {}
    if isinstance(examples_raw, dict):
        for zone_key in ZONE_KEYS:
            reference = normalize_image_ref(examples_raw.get(zone_key))
            if reference:
                zone_examples[zone_key] = reference

    return {
        "id": _unique_id(used_ids, source.get("id"), "oc"),
        "name": as_str(source.get("name")) or "Sin nombre",
        "summary": as_str(source.get("summary")),
        "history": as_str(source.get("history")),
        "personality": as_str(source.get("personality")),
        "relationships": as_str(source.get("relationships")),
        "tags": as_str_list(source.get("tags")),
        "referenceImage": normalize_image_ref(source.get("referenceImage")),
        "zoneExamples": zone_examples,
        "palettes": palettes,
        "recipe": recipe,
        "environment": normalize_environment(source.get("environment"), used_ids),
    }


def normalize_state(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    used_ids: set[str] = set()
    characters = []
    characters_raw = source.get("characters")
    if isinstance(characters_raw, list):
        characters = [
            normalize_character(item, used_ids)
            for item in characters_raw
            if isinstance(item, dict)
        ]

    active_id = as_str(source.get("activeCharacterId"))
    if not any(character["id"] == active_id for character in characters):
        active_id = characters[0]["id"] if characters else None

    private_mode = source.get("privateMode")
    if not isinstance(private_mode, bool):
        private_mode = True

    return {
        "version": 1,
        "privateMode": private_mode,
        "activeCharacterId": active_id,
        "characters": characters,
    }


def empty_state() -> dict[str, Any]:
    return {
        "version": 1,
        "privateMode": True,
        "activeCharacterId": None,
        "characters": [],
    }


def seed_state() -> dict[str, Any]:
    if SEED_FILE.exists():
        try:
            return normalize_state(json.loads(SEED_FILE.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    state = empty_state()
    character = add_character(state, "Mi OC", "Un resumen de tres líneas para recordar quién es.")
    character["tags"] = ["nuevo"]
    return state


def load_state(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path else DATA_FILE
    if not target.exists():
        return seed_state()
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        _backup_bad_file(target)
        return seed_state()
    return normalize_state(raw)


def save_state(state: dict[str, Any], path: str | Path | None = None) -> Path:
    target = Path(path) if path else DATA_FILE
    normalized = normalize_state(state)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=target.name + ".", suffix=".tmp", dir=str(target.parent)
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(normalized, handle, ensure_ascii=False, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return target


def export_json(state: dict[str, Any], path: str | Path) -> Path:
    return save_state(state, path)


def import_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"No se pudo leer el archivo: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"El archivo no es un JSON válido: {exc}") from exc
    if not isinstance(raw, dict) or not isinstance(raw.get("characters"), list):
        raise ValueError("El JSON no contiene una lista «characters».")
    return normalize_state(raw)


def get_character(state: dict[str, Any], character_id: str | None) -> dict[str, Any] | None:
    if not character_id:
        return None
    for character in state.get("characters", []):
        if character.get("id") == character_id:
            return character
    return None


def active_character(state: dict[str, Any]) -> dict[str, Any] | None:
    character = get_character(state, state.get("activeCharacterId"))
    if character:
        return character
    characters = state.get("characters", [])
    return characters[0] if characters else None


def add_character(
    state: dict[str, Any],
    name: str,
    summary: str = "",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    character = {
        "id": new_id("oc"),
        "name": as_str(name) or "Sin nombre",
        "summary": as_str(summary),
        "history": "",
        "personality": "",
        "relationships": "",
        "tags": as_str_list(tags or []),
        "palettes": empty_palettes(),
        "recipe": make_base_recipe(),
        "environment": default_environment(),
    }
    state.setdefault("characters", []).append(character)
    state["activeCharacterId"] = character["id"]
    return character


def delete_character(state: dict[str, Any], character_id: str) -> bool:
    characters = state.get("characters", [])
    for index, character in enumerate(characters):
        if character.get("id") == character_id:
            del characters[index]
            if state.get("activeCharacterId") == character_id:
                state["activeCharacterId"] = characters[0]["id"] if characters else None
            return True
    return False


def add_swatch(
    character: dict[str, Any],
    zone_key: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    used_ids = _used_ids(character)
    swatch = normalize_swatch(data, zone_key, used_ids)
    if zone_key == "environment":
        character.setdefault("environment", default_environment()).setdefault("palette", []).append(swatch)
    else:
        character.setdefault("palettes", empty_palettes()).setdefault(zone_key, []).append(swatch)
    return swatch


def update_swatch(
    character: dict[str, Any],
    zone_key: str,
    swatch_id: str,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    found = find_swatch(character, zone_key, swatch_id)
    if not found:
        return None
    _, _, current = found
    used_ids = _used_ids(character) - {swatch_id}
    updated = normalize_swatch({**current, **data, "id": swatch_id}, zone_key, used_ids)
    current.clear()
    current.update(updated)
    return current


def delete_swatch(character: dict[str, Any], zone_key: str, swatch_id: str) -> bool:
    found = find_swatch(character, zone_key, swatch_id)
    if not found:
        return False
    items, index, _ = found
    del items[index]
    return True


def find_swatch(
    character: dict[str, Any],
    zone_key: str,
    swatch_id: str,
) -> tuple[list[dict[str, Any]], int, dict[str, Any]] | None:
    if zone_key == "environment":
        items = character.get("environment", {}).get("palette", [])
    else:
        items = character.get("palettes", {}).get(zone_key, [])
    for index, swatch in enumerate(items):
        if swatch.get("id") == swatch_id:
            return items, index, swatch
    return None


def add_layer(character: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    used_ids = _used_ids(character)
    layer = normalize_layer(data, used_ids)
    character.setdefault("recipe", []).append(layer)
    return layer


def update_layer(character: dict[str, Any], layer_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    for layer in character.get("recipe", []):
        if layer.get("id") == layer_id:
            used_ids = _used_ids(character) - {layer_id}
            updated = normalize_layer({**layer, **data, "id": layer_id}, used_ids)
            layer.clear()
            layer.update(updated)
            return layer
    return None


def delete_layer(character: dict[str, Any], layer_id: str) -> bool:
    recipe = character.get("recipe", [])
    for index, layer in enumerate(recipe):
        if layer.get("id") == layer_id:
            del recipe[index]
            return True
    return False


def move_layer(character: dict[str, Any], layer_id: str, direction: str) -> bool:
    recipe = character.get("recipe", [])
    for index, layer in enumerate(recipe):
        if layer.get("id") != layer_id:
            continue
        target = index - 1 if direction == "up" else index + 1
        if target < 0 or target >= len(recipe):
            return False
        recipe[index], recipe[target] = recipe[target], recipe[index]
        return True
    return False


def reset_recipe(character: dict[str, Any]) -> None:
    character["recipe"] = make_base_recipe()


def count_colors(character: dict[str, Any]) -> int:
    palettes = character.get("palettes", {})
    return sum(len(palettes.get(zone_key, [])) for zone_key in ZONE_KEYS)


def key_colors(character: dict[str, Any]) -> list[str]:
    result: list[str] = []
    for zone_key in ("skin", "hair", "eyes"):
        items = character.get("palettes", {}).get(zone_key, [])
        if items:
            result.append(items[0]["hex"])
        if len(result) == 3:
            break
    while len(result) < 3:
        result.append("#3a3440")
    return result[:3]


def rgb_to_hex(red: int, green: int, blue: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(
        max(0, min(255, int(round(red)))),
        max(0, min(255, int(round(green)))),
        max(0, min(255, int(round(blue)))),
    )


def mix_hex(first: str, second: str, amount: float) -> str:
    amount = max(0.0, min(1.0, float(amount)))
    a = hex_to_rgb(first)
    b = hex_to_rgb(second)
    return rgb_to_hex(
        a[0] + (b[0] - a[0]) * amount,
        a[1] + (b[1] - a[1]) * amount,
        a[2] + (b[2] - a[2]) * amount,
    )


def blend_multiply(base: str, tint: str, amount: float = 1.0) -> str:
    amount = max(0.0, min(1.0, float(amount)))
    br, bg, bb = hex_to_rgb(base)
    tr, tg, tb = hex_to_rgb(tint)
    return rgb_to_hex(
        br + (br * tr / 255.0 - br) * amount,
        bg + (bg * tg / 255.0 - bg) * amount,
        bb + (bb * tb / 255.0 - bb) * amount,
    )


def blend_add(base: str, tint: str, amount: float = 1.0) -> str:
    amount = max(0.0, min(1.0, float(amount)))
    br, bg, bb = hex_to_rgb(base)
    tr, tg, tb = hex_to_rgb(tint)
    return rgb_to_hex(
        br + (min(255, br + tr) - br) * amount,
        bg + (min(255, bg + tg) - bg) * amount,
        bb + (min(255, bb + tb) - bb) * amount,
    )


def hex_to_lab(value: str) -> tuple[float, float, float]:
    red, green, blue = (component / 255.0 for component in hex_to_rgb(value))

    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = linear(red), linear(green), linear(blue)
    x = (red * 0.4124564 + green * 0.3575761 + blue * 0.1804375) / 0.95047
    y = red * 0.2126729 + green * 0.7151522 + blue * 0.0721750
    z = (red * 0.0193339 + green * 0.1191920 + blue * 0.9503041) / 1.08883

    def pivot(value_: float) -> float:
        return value_ ** (1.0 / 3.0) if value_ > 0.008856 else 7.787 * value_ + 16.0 / 116.0

    fx, fy, fz = pivot(x), pivot(y), pivot(z)
    return 116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)


def delta_e(first: str, second: str) -> float:
    """CIE76: suficiente para “¿este color es el de la paleta?”."""
    lab_a = hex_to_lab(first)
    lab_b = hex_to_lab(second)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab_a, lab_b)))


def lighting_spec(character: dict[str, Any]) -> list[dict[str, Any]]:
    """Capas del rig de luz, de arriba abajo."""
    environment = character.get("environment") or {}
    recipe = {
        as_str(row.get("name")).upper(): row
        for row in character.get("recipe", [])
        if isinstance(row, dict)
    }

    def opacity(name: str, default: int) -> int:
        row = recipe.get(name)
        return clamp_int(row.get("opacity"), 0, 100, default) if row else default

    shadow = normalize_hex(environment.get("shadowTint"), "#3a2a4d")
    key_light = normalize_hex(environment.get("keyLight"), "#ffb36b")
    bounce = normalize_hex(environment.get("bounce"), "#7a4a2a")
    return [
        {"name": "SHADOW", "blend": "multiply", "color": shadow, "opacity": opacity("SHADOW", 45)},
        {"name": "AO", "blend": "multiply", "color": mix_hex(shadow, "#000000", 0.2), "opacity": opacity("AO", 25)},
        {"name": "LIGHT", "blend": "add", "color": key_light, "opacity": opacity("LIGHT", 30)},
        {"name": "GLOW", "blend": "add", "color": key_light, "opacity": opacity("GLOW", 15)},
        {"name": "BOUNCE", "blend": "add", "color": bounce, "opacity": 20},
    ]


def scene_preview(character: dict[str, Any], limit: int = 3) -> list[dict[str, str]]:
    """Colores clave teñidos por la luz del ambiente, para el preview."""
    specs = {item["name"]: item for item in lighting_spec(character)}
    shadow = specs["SHADOW"]
    light = specs["LIGHT"]
    bounce = specs["BOUNCE"]
    rows: list[dict[str, str]] = []
    for zone_key in ("skin", "hair", "eyes"):
        items = character.get("palettes", {}).get(zone_key, [])
        if not items:
            continue
        swatch = items[0]
        base = normalize_hex(swatch.get("hex"), "#808080")
        rows.append(
            {
                "zone": zone_key,
                "name": as_str(swatch.get("name")),
                "base": base,
                "shadow": blend_multiply(base, shadow["color"], shadow["opacity"] / 100.0),
                "light": blend_add(base, light["color"], light["opacity"] / 100.0),
                "bounce": blend_add(base, bounce["color"], bounce["opacity"] / 100.0),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def nearest_swatch(
    character: dict[str, Any],
    hex_value: str,
    include_private: bool = False,
) -> dict[str, Any] | None:
    target = normalize_hex(hex_value)
    best: dict[str, Any] | None = None
    for zone in ZONES:
        if zone["key"] == "intimate" and not include_private:
            continue
        for swatch in character.get("palettes", {}).get(zone["key"], []):
            distance = delta_e(target, swatch.get("hex", "#808080"))
            if best is None or distance < best["delta"]:
                best = {"swatch": swatch, "zone": zone["key"], "delta": distance}
    return best


def gpl_text(character: dict[str, Any], include_private: bool = False) -> str:
    lines = [
        "GIMP Palette",
        f"Name: Grimorio - {gpl_safe(character.get('name', 'OC'))}",
        "Columns: 8",
        "#",
    ]
    for zone in ZONES:
        if zone["key"] == "intimate" and not include_private:
            continue
        for swatch in character.get("palettes", {}).get(zone["key"], []):
            red, green, blue = hex_to_rgb(swatch.get("hex", "#808080"))
            lines.append(
                f"{red} {green} {blue}\t{gpl_safe(zone['label'])} · {gpl_safe(swatch.get('name', 'Color'))}"
            )
    return "\n".join(lines) + "\n"


def gpl_filename(character: dict[str, Any]) -> str:
    return f"grimorio-{slugify(character.get('name', 'oc'))}.gpl"


def export_gpl(character: dict[str, Any], path: str | Path, include_private: bool = False) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(gpl_text(character, include_private=include_private), encoding="utf-8")
    return target


def _unique_id(used_ids: set[str], preferred: Any, prefix: str) -> str:
    candidate = as_str(preferred)
    if not candidate or candidate in used_ids:
        candidate = new_id(prefix)
        while candidate in used_ids:
            candidate = new_id(prefix)
    used_ids.add(candidate)
    return candidate


def _used_ids(character: dict[str, Any]) -> set[str]:
    used: set[str] = set()
    for items in character.get("palettes", {}).values():
        for swatch in items:
            if swatch.get("id"):
                used.add(swatch["id"])
    for swatch in character.get("environment", {}).get("palette", []):
        if swatch.get("id"):
            used.add(swatch["id"])
    for layer in character.get("recipe", []):
        if layer.get("id"):
            used.add(layer["id"])
    return used


def _backup_bad_file(path: Path) -> None:
    backup = path.with_name(f"{path.name}.bad-{_now_stamp()}")
    try:
        path.replace(backup)
    except OSError:
        pass
