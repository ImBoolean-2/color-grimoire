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

KINDS: tuple[str, ...] = ("character", "scene", "prop")
KIND_LABELS: dict[str, str] = {"character": "Personaje", "scene": "Escenario", "prop": "Prop"}
SCENE_ZONES: list[dict[str, Any]] = [
    {"key": "sky", "label": "Cielo", "defaultBody": "Cielo", "private": False},
    {"key": "foliage", "label": "Vegetación", "defaultBody": "Vegetación", "private": False},
    {"key": "terrain", "label": "Terreno", "defaultBody": "Terreno", "private": False},
    {"key": "water", "label": "Agua", "defaultBody": "Agua", "private": False},
    {"key": "architecture", "label": "Arquitectura", "defaultBody": "Arquitectura", "private": False},
    {"key": "props", "label": "Objetos", "defaultBody": "Objetos", "private": False},
    {"key": "fx", "label": "Efectos", "defaultBody": "Efectos", "private": False},
    {"key": "light", "label": "Luz", "defaultBody": "Luz", "private": False},
]
PROP_ZONES: list[dict[str, Any]] = [
    {"key": "base", "label": "Base", "defaultBody": "Base", "private": False},
    {"key": "shadow", "label": "Sombra", "defaultBody": "Sombra", "private": False},
    {"key": "light", "label": "Luz", "defaultBody": "Luz", "private": False},
    {"key": "accent", "label": "Acento", "defaultBody": "Acento", "private": False},
    {"key": "detail", "label": "Detalle", "defaultBody": "Detalle", "private": False},
]
ZONE_PRESETS: dict[str, list[dict[str, Any]]] = {
    "character": [
        {"key": z["key"], "label": z["label"], "defaultBody": z["default_body"],
         "private": z["key"] == "intimate"}
        for z in ZONES
    ],
    "scene": SCENE_ZONES,
    "prop": PROP_ZONES,
}

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

SCENERY_BODY_PARTS: list[str] = [
    "Cielo", "Agua", "Vegetación", "Terreno", "Roca", "Madera",
    "Metal", "Cristal", "Tela", "FX",
]
ALL_BODY_PARTS: list[str] = BODY_PARTS + [
    part for part in SCENERY_BODY_PARTS if part not in BODY_PARTS
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

RECIPE_PRESETS: dict[str, list[dict[str, Any]]] = {
    "character": BASE_RECIPE,
    "scene": [
        {"name": "SKY", "blend": "normal", "opacity": 100, "purpose": "Cielo / fondo lejano"},
        {"name": "FAR", "blend": "normal", "opacity": 100, "purpose": "Plano lejano"},
        {"name": "MID", "blend": "normal", "opacity": 100, "purpose": "Plano medio"},
        {"name": "FG", "blend": "normal", "opacity": 100, "purpose": "Primer plano"},
        {"name": "ATMO", "blend": "overlay", "opacity": 20, "purpose": "Atmósfera / profundidad"},
        {"name": "FX", "blend": "overlay", "opacity": 15, "purpose": "Textura / ajuste"},
    ],
    "prop": [
        {"name": "LINE", "blend": "normal", "opacity": 100, "purpose": "Lineart / silueta"},
        {"name": "BASE", "blend": "normal", "opacity": 100, "purpose": "Colores planos"},
        {"name": "SHADOW", "blend": "multiply", "opacity": 45, "purpose": "Sombra"},
        {"name": "LIGHT", "blend": "add", "opacity": 30, "purpose": "Luz"},
        {"name": "FX", "blend": "overlay", "opacity": 15, "purpose": "Textura / ajuste"},
    ],
}
RECIPE_PRESET_LABELS: dict[str, str] = {
    "character": "Personaje",
    "scene": "Entorno",
    "prop": "Prop",
}

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

ENVIRONMENT_PRESETS: dict[str, dict[str, Any]] = {
    "dawn": {"name": "Amanecer", "time": "Amanecer", "weather": "Despejado",
             "keyLight": "#ffd2a1", "shadowTint": "#4a3a5c", "bounce": "#b06a4a",
             "mood": "Frío en sombra, cálido en luz", "palette": []},
    "day": {"name": "Día", "time": "Mediodía", "weather": "Despejado",
            "keyLight": "#fff3d6", "shadowTint": "#5a6a7a", "bounce": "#c9a07a",
            "mood": "Luz alta y neutra", "palette": []},
    "sunset": {"name": "Atardecer", "time": "Atardecer", "weather": "Despejado",
               "keyLight": "#ff9a5c", "shadowTint": "#3a2a5c", "bounce": "#8a4a3a",
               "mood": "Cálido en luz, frío en sombra", "palette": []},
    "night": {"name": "Noche", "time": "Noche", "weather": "Despejado",
              "keyLight": "#9ab8ff", "shadowTint": "#1a1f3a", "bounce": "#3a4a6a",
              "mood": "Frío, luz de luna", "palette": []},
    "fog": {"name": "Niebla", "time": "Amanecer", "weather": "Niebla",
            "keyLight": "#d8d8d0", "shadowTint": "#6a7078", "bounce": "#8a8a80",
            "mood": "Bajo contraste, aire húmedo", "palette": []},
}
ENVIRONMENT_PRESET_LABELS: dict[str, str] = {
    "dawn": "Amanecer", "day": "Día", "sunset": "Atardecer",
    "night": "Noche", "fog": "Niebla",
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


def palette_zone_label(zone_key: str, zones: list[dict[str, Any]] | None = None) -> str:
    if isinstance(zone_key, dict):
        # Compatibilidad: permite palette_zone_label(character, "sky").
        character = zone_key
        zone_key = as_str(zones) if not isinstance(zones, list) else ""
        zones = palette_zones(character)
    for zone in zones or []:
        if zone.get("key") == zone_key:
            return as_str(zone.get("label")) or zone_key
    zone = ZONE_BY_KEY.get(zone_key)
    return zone["label"] if zone else zone_key


def default_body_part(zone_key: str) -> str:
    if zone_key == "environment":
        return "Ambiente"
    zone = ZONE_BY_KEY.get(zone_key)
    return zone["default_body"] if zone else ""


def empty_palettes(zones: list[dict[str, Any]] | None = None) -> dict[str, list[dict[str, Any]]]:
    zone_list = zones if isinstance(zones, list) and zones else default_zones("character")
    return {zone["key"]: [] for zone in zone_list}


def palette_zone_keys(character: dict[str, Any]) -> list[str]:
    """Claves de paleta visibles: zonas del proyecto (si existen) + extras."""
    palettes = character.get("palettes", {})
    keys: list[str] = [zone["key"] for zone in palette_zones(character)]
    if not isinstance(palettes, dict):
        return keys
    for key in palettes:
        if key not in keys:
            keys.append(key)
    return keys


def make_recipe(preset: str = "character") -> list[dict[str, Any]]:
    layers = RECIPE_PRESETS.get(preset, RECIPE_PRESETS["character"])
    return [
        {
            "id": new_id("layer"),
            "name": item["name"],
            "blend": item["blend"],
            "opacity": item["opacity"],
            "purpose": item["purpose"],
        }
        for item in layers
    ]


def make_base_recipe() -> list[dict[str, Any]]:
    return make_recipe("character")


def default_environment() -> dict[str, Any]:
    env = dict(DEFAULT_ENVIRONMENT)
    env["palette"] = []
    return env


def default_zones(kind: str = "character") -> list[dict[str, Any]]:
    return [dict(zone) for zone in ZONE_PRESETS.get(kind, ZONE_PRESETS["character"])]


def normalize_kind(raw: Any) -> str:
    kind = as_str(raw).lower()
    return kind if kind in ZONE_PRESETS else "character"


def normalize_zones(raw: Any, kind: str) -> list[dict[str, Any]]:
    defaults = default_zones(kind)
    if not isinstance(raw, list):
        return defaults
    result: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        key = as_str(item.get("key"))
        if not key or any(zone["key"] == key for zone in result):
            continue
        private = item.get("private")
        if not isinstance(private, bool):
            private = key == "intimate"
        result.append({
            "key": key,
            "label": as_str(item.get("label")) or key,
            "defaultBody": as_str(item.get("defaultBody")) or as_str(item.get("label")) or key,
            "private": private,
        })
    return result or defaults


def palette_zones(character: dict[str, Any]) -> list[dict[str, Any]]:
    zones = character.get("zones")
    if isinstance(zones, list):
        result: list[dict[str, Any]] = []
        for zone in zones:
            if isinstance(zone, dict):
                key = as_str(zone.get("key"))
                if key:
                    result.append({
                        "key": key,
                        "label": as_str(zone.get("label")) or key,
                        "defaultBody": as_str(zone.get("defaultBody")) or key,
                        "private": bool(zone.get("private", key == "intimate")),
                    })
        if result:
            return result
    return default_zones("character")


def palette_zone_private(character: dict[str, Any], zone_key: str) -> bool:
    for zone in palette_zones(character):
        if zone["key"] == zone_key:
            return bool(zone.get("private", zone_key == "intimate"))
    return zone_key == "intimate"


def _zone_default_body(character: dict[str, Any], zone_key: str) -> str:
    for zone in palette_zones(character):
        if zone["key"] == zone_key:
            return as_str(zone.get("defaultBody")) or default_body_part(zone_key)
    return default_body_part(zone_key)


def _zone_key(value: Any) -> str:
    text = unicodedata.normalize("NFKD", as_str(value)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9_-]+", "-", text.lower()).strip("-")
    return text or "zona"


def add_zone(
    character: dict[str, Any],
    key: Any,
    label: str = "",
    default_body: str = "",
    private: bool = False,
) -> dict[str, Any] | None:
    zones = palette_zones(character)
    zone_key = _zone_key(key)
    if any(zone["key"] == zone_key for zone in zones):
        return None
    zone = {
        "key": zone_key,
        "label": as_str(label) or zone_key,
        "defaultBody": as_str(default_body) or as_str(label) or zone_key,
        "private": bool(private),
    }
    zones.append(zone)
    character["zones"] = zones
    character.setdefault("palettes", {}).setdefault(zone_key, [])
    return zone


def update_zone(character: dict[str, Any], key: str, data: dict[str, Any]) -> dict[str, Any] | None:
    zones = palette_zones(character)
    for zone in zones:
        if zone["key"] != key:
            continue
        if "label" in data:
            zone["label"] = as_str(data.get("label")) or zone["key"]
        if "defaultBody" in data:
            zone["defaultBody"] = as_str(data.get("defaultBody")) or zone["label"]
        if isinstance(data.get("private"), bool):
            zone["private"] = data["private"]
        character["zones"] = zones
        return zone
    return None


def delete_zone(character: dict[str, Any], key: str) -> bool:
    zones = palette_zones(character)
    if len(zones) <= 1:
        return False
    remaining = [zone for zone in zones if zone["key"] != key]
    if len(remaining) == len(zones):
        return False
    character["zones"] = remaining
    # La paleta se conserva como extra opaco, no se borra.
    return True


def move_zone(character: dict[str, Any], key: str, direction: str) -> bool:
    zones = palette_zones(character)
    index = next((i for i, zone in enumerate(zones) if zone["key"] == key), -1)
    if index < 0:
        return False
    target = index - 1 if direction == "up" else index + 1
    if target < 0 or target >= len(zones):
        return False
    zones[index], zones[target] = zones[target], zones[index]
    character["zones"] = zones
    return True


def normalize_swatch(
    raw: Any,
    zone_key: str,
    used_ids: set[str],
    default_body: Any = None,
) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    note = as_str(source.get("note"))
    purpose = as_str(source.get("purpose")) or note
    body_part = as_str(source.get("bodyPart")) or as_str(default_body) or default_body_part(zone_key)
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


def normalize_palettes(
    raw: Any,
    used_ids: set[str],
    zones: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Normaliza las zonas del proyecto y conserva como bloque opaco las extra.

    Las zonas desconocidas (custom, legacy) no se interpretan: se copian en
    profundo para que no se pierdan al guardar desde el Grimorio.
    """
    source = raw if isinstance(raw, dict) else {}
    zone_list = zones if isinstance(zones, list) and zones else default_zones("character")
    palettes = empty_palettes(zone_list)
    for zone in zone_list:
        zone_key = zone["key"]
        items = source.get(zone_key)
        if isinstance(items, list):
            palettes[zone_key] = [
                normalize_swatch(item, zone_key, used_ids, zone.get("defaultBody"))
                for item in items
                if isinstance(item, dict)
            ]
    for zone_key, items in source.items():
        if zone_key in palettes or not isinstance(items, list):
            continue
        palettes[zone_key] = _deep_copy(items)
        for item in items:
            if isinstance(item, dict):
                item_id = as_str(item.get("id"))
                if item_id:
                    used_ids.add(item_id)
    return palettes


def normalize_library(raw: Any, used_ids: set[str]) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    result: list[dict[str, Any]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        swatches_raw = item.get("swatches")
        swatches: list[dict[str, Any]] = []
        if isinstance(swatches_raw, list):
            swatches = [
                normalize_swatch(swatch, "library", used_ids, "Otro")
                for swatch in swatches_raw
                if isinstance(swatch, dict)
            ]
        result.append({
            "id": _unique_id(used_ids, item.get("id"), "lib"),
            "name": as_str(item.get("name")) or "Paleta sin nombre",
            "swatches": swatches,
        })
    return result


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


def _deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def normalize_head(raw: Any) -> dict[str, Any]:
    """Bloque opaco del generador de cabezas (Loomis): se conserva tal cual.

    El Grimorio no lo interpreta; solo lo guarda para que viaje en el JSON.
    La copia es profunda para no compartir listas ni diccionarios con el origen
    y para conservar claves desconocidas o legacy.
    """
    if not isinstance(raw, dict):
        return {}
    return _deep_copy(raw)


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
        "id": _unique_id(used_ids, source.get("id"), "env"),
        "name": as_str(source.get("name")),
        "time": as_str(source.get("time")),
        "weather": as_str(source.get("weather")),
        "keyLight": normalize_hex(source.get("keyLight"), "#ffb36b"),
        "shadowTint": normalize_hex(source.get("shadowTint"), "#3a2a4d"),
        "bounce": normalize_hex(source.get("bounce"), "#7a4a2a"),
        "mood": as_str(source.get("mood")),
        "palette": palette,
    }


def normalize_environments(
    source: dict[str, Any],
    used_ids: set[str],
) -> tuple[list[dict[str, Any]], str]:
    raw_list = source.get("environments")
    environments: list[dict[str, Any]] = []
    if isinstance(raw_list, list):
        for item in raw_list:
            if isinstance(item, dict):
                environments.append(normalize_environment(item, used_ids))
    if not environments:
        legacy = source.get("environment")
        environments = [normalize_environment(legacy if isinstance(legacy, dict) else {}, used_ids)]
    else:
        legacy = source.get("environment")
        if isinstance(legacy, dict):
            legacy_id = as_str(legacy.get("id"))
            known = {env["id"] for env in environments}
            if legacy_id and legacy_id not in known:
                environments.append(normalize_environment(legacy, used_ids))
    active_id = as_str(source.get("activeEnvironmentId"))
    if not any(env["id"] == active_id for env in environments):
        active_id = environments[0]["id"]
    return environments, active_id


def active_environment(character: dict[str, Any]) -> dict[str, Any]:
    environments = character.get("environments")
    active_id = as_str(character.get("activeEnvironmentId"))
    if isinstance(environments, list) and environments:
        for env in environments:
            if isinstance(env, dict) and env.get("id") == active_id:
                return env
        return environments[0]
    return character.get("environment") or default_environment()


def sync_environment_mirror(character: dict[str, Any]) -> None:
    environment = active_environment(character)
    if not isinstance(character.get("environments"), list) or not character["environments"]:
        character["environments"] = [_deep_copy(environment)]
    environment = active_environment(character)
    if not as_str(environment.get("id")):
        environment["id"] = new_id("env")
    character["activeEnvironmentId"] = environment.get("id")
    character["environment"] = _deep_copy(environment)


def add_environment(
    character: dict[str, Any],
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    used_ids = _used_ids(character)
    environment = normalize_environment(data if isinstance(data, dict) else {}, used_ids)
    character.setdefault("environments", []).append(environment)
    character["activeEnvironmentId"] = environment["id"]
    sync_environment_mirror(character)
    return environment


def duplicate_environment(
    character: dict[str, Any],
    environment_id: str | None = None,
) -> dict[str, Any] | None:
    source = None
    for env in character.get("environments", []):
        if isinstance(env, dict) and (environment_id is None or env.get("id") == environment_id):
            source = env
            break
    if source is None:
        return None
    used_ids = _used_ids(character) - {
        swatch.get("id") for swatch in source.get("palette", []) if isinstance(swatch, dict)
    }
    copy = _deep_copy(source)
    copy["id"] = new_id("env")
    copy["name"] = (as_str(copy.get("name")) or "Ambiente") + " (copia)"
    copy = normalize_environment(copy, used_ids)
    character.setdefault("environments", []).append(copy)
    character["activeEnvironmentId"] = copy["id"]
    sync_environment_mirror(character)
    return copy


def delete_environment(character: dict[str, Any], environment_id: str) -> bool:
    environments = character.get("environments")
    if not isinstance(environments, list) or len(environments) <= 1:
        return False
    before = len(environments)
    character["environments"] = [
        env for env in environments
        if isinstance(env, dict) and env.get("id") != environment_id
    ]
    if len(character["environments"]) == before:
        return False
    if character.get("activeEnvironmentId") == environment_id:
        character["activeEnvironmentId"] = character["environments"][0]["id"]
    sync_environment_mirror(character)
    return True


def set_active_environment(character: dict[str, Any], environment_id: str) -> bool:
    for env in character.get("environments", []):
        if isinstance(env, dict) and env.get("id") == environment_id:
            character["activeEnvironmentId"] = environment_id
            sync_environment_mirror(character)
            return True
    return False


def update_environment(
    character: dict[str, Any],
    environment_id: str,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    for env in character.get("environments", []):
        if not isinstance(env, dict) or env.get("id") != environment_id:
            continue
        current_ids = {
            swatch.get("id") for swatch in env.get("palette", []) if isinstance(swatch, dict)
        }
        used_ids = _used_ids(character) - current_ids - {environment_id}
        updated = normalize_environment({**env, **data, "id": environment_id}, used_ids)
        env.clear()
        env.update(updated)
        if character.get("activeEnvironmentId") == environment_id:
            sync_environment_mirror(character)
        return env
    return None


def _state_used_ids(state: dict[str, Any]) -> set[str]:
    used: set[str] = set()
    for character in state.get("characters", []):
        if isinstance(character, dict):
            used |= _used_ids(character)
    for palette in state.get("library", []):
        if not isinstance(palette, dict):
            continue
        palette_id = as_str(palette.get("id"))
        if palette_id:
            used.add(palette_id)
        for swatch in palette.get("swatches", []):
            if isinstance(swatch, dict) and swatch.get("id"):
                used.add(swatch["id"])
    return used


def add_library_palette(state: dict[str, Any], name: str, swatches: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    used = _state_used_ids(state)
    normalized: list[dict[str, Any]] = []
    for swatch in swatches or []:
        if isinstance(swatch, dict):
            normalized.append(normalize_swatch({**swatch, "id": ""}, "library", used, "Otro"))
    palette = {
        "id": _unique_id(used, None, "lib"),
        "name": as_str(name) or "Paleta sin nombre",
        "swatches": normalized,
    }
    state.setdefault("library", []).append(palette)
    return palette


def library_add_from_zone(
    state: dict[str, Any],
    character: dict[str, Any],
    zone_key: str,
    name: str | None = None,
) -> dict[str, Any]:
    if zone_key == "environment":
        source = active_environment(character).get("palette", [])
    else:
        source = character.get("palettes", {}).get(zone_key, [])
    label = palette_zone_label(zone_key, palette_zones(character))
    return add_library_palette(
        state,
        name or f"{as_str(character.get('name')) or 'Proyecto'} · {label}",
        source if isinstance(source, list) else [],
    )


def rename_library_palette(state: dict[str, Any], palette_id: str, name: str) -> dict[str, Any] | None:
    for palette in state.get("library", []):
        if isinstance(palette, dict) and palette.get("id") == palette_id:
            palette["name"] = as_str(name) or "Paleta sin nombre"
            return palette
    return None


def delete_library_palette(state: dict[str, Any], palette_id: str) -> bool:
    before = len(state.get("library", []))
    state["library"] = [
        palette for palette in state.get("library", [])
        if not (isinstance(palette, dict) and palette.get("id") == palette_id)
    ]
    return len(state["library"]) != before


def import_library_palette(
    character: dict[str, Any],
    zone_key: str,
    palette: dict[str, Any],
) -> list[dict[str, Any]]:
    """Copia una paleta de la biblioteca a una zona, con ids nuevos."""
    if not isinstance(palette, dict):
        return []
    used_ids = _used_ids(character)
    default_body = _zone_default_body(character, zone_key)
    if zone_key == "environment":
        target = active_environment(character).setdefault("palette", [])
    else:
        target = character.setdefault(
            "palettes", empty_palettes(palette_zones(character))
        ).setdefault(zone_key, [])
    created: list[dict[str, Any]] = []
    for swatch in palette.get("swatches", []):
        if not isinstance(swatch, dict):
            continue
        item = normalize_swatch({**swatch, "id": ""}, zone_key, used_ids, default_body)
        target.append(item)
        created.append(item)
    if zone_key == "environment":
        sync_environment_mirror(character)
    return created


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
    character_id = _unique_id(used_ids, source.get("id"), "oc")
    kind = normalize_kind(source.get("kind"))
    zones = normalize_zones(source.get("zones"), kind)
    palettes = normalize_palettes(source.get("palettes"), used_ids, zones)

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
        for zone in zones:
            reference = normalize_image_ref(examples_raw.get(zone["key"]))
            if reference:
                zone_examples[zone["key"]] = reference

    environments, active_id = normalize_environments(source, used_ids)
    active = next((env for env in environments if env["id"] == active_id), environments[0])

    return {
        "id": character_id,
        "name": as_str(source.get("name")) or "Sin nombre",
        "summary": as_str(source.get("summary")),
        "history": as_str(source.get("history")),
        "personality": as_str(source.get("personality")),
        "relationships": as_str(source.get("relationships")),
        "tags": as_str_list(source.get("tags")),
        "referenceImage": normalize_image_ref(source.get("referenceImage")),
        "zoneExamples": zone_examples,
        "kind": kind,
        "zones": zones,
        "palettes": palettes,
        "recipe": recipe,
        "environment": _deep_copy(active),
        "environments": environments,
        "activeEnvironmentId": active_id,
        "head": normalize_head(source.get("head")),
    }


def migrate_state(raw: Any) -> dict[str, Any]:
    source = _deep_copy(raw) if isinstance(raw, dict) else {}
    if source.get("version") == 2:
        return source
    source["version"] = 2
    characters = source.get("characters")
    if isinstance(characters, list):
        for character in characters:
            if not isinstance(character, dict):
                continue
            kind = normalize_kind(character.get("kind"))
            character["kind"] = kind
            if not isinstance(character.get("zones"), list) or not character["zones"]:
                character["zones"] = default_zones(kind)
            if not isinstance(character.get("environments"), list) or not character["environments"]:
                legacy = character.get("environment")
                character["environments"] = [
                    _deep_copy(legacy if isinstance(legacy, dict) else default_environment())
                ]
            character.setdefault("activeEnvironmentId", "")
    source.setdefault("library", [])
    return source


def normalize_state(raw: Any) -> dict[str, Any]:
    source = migrate_state(raw)
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

    library = normalize_library(source.get("library"), used_ids)

    return {
        "version": 2,
        "privateMode": private_mode,
        "activeCharacterId": active_id,
        "characters": characters,
        "library": library,
    }


def empty_state() -> dict[str, Any]:
    return {
        "version": 2,
        "privateMode": True,
        "activeCharacterId": None,
        "characters": [],
        "library": [],
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
    if isinstance(raw, dict) and raw.get("version") != 2:
        _backup_before_migration(target)
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
    kind: str = "character",
) -> dict[str, Any]:
    kind = normalize_kind(kind)
    zones = default_zones(kind)
    env = default_environment()
    env["id"] = new_id("env")
    character = {
        "id": new_id("oc"),
        "name": as_str(name) or "Sin nombre",
        "summary": as_str(summary),
        "history": "",
        "personality": "",
        "relationships": "",
        "tags": as_str_list(tags or []),
        "kind": kind,
        "zones": zones,
        "palettes": empty_palettes(zones),
        "recipe": make_recipe(kind),
        "environment": _deep_copy(env),
        "environments": [env],
        "activeEnvironmentId": env["id"],
        "head": {},
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
    swatch = normalize_swatch(
        data, zone_key, used_ids, _zone_default_body(character, zone_key)
    )
    if zone_key == "environment":
        active_environment(character).setdefault("palette", []).append(swatch)
        sync_environment_mirror(character)
    else:
        zones = palette_zones(character)
        character.setdefault("palettes", empty_palettes(zones)).setdefault(zone_key, []).append(swatch)
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
    updated = normalize_swatch(
        {**current, **data, "id": swatch_id},
        zone_key,
        used_ids,
        _zone_default_body(character, zone_key),
    )
    current.clear()
    current.update(updated)
    if zone_key == "environment":
        sync_environment_mirror(character)
    return current


def delete_swatch(character: dict[str, Any], zone_key: str, swatch_id: str) -> bool:
    found = find_swatch(character, zone_key, swatch_id)
    if not found:
        return False
    items, index, _ = found
    del items[index]
    if zone_key == "environment":
        sync_environment_mirror(character)
    return True


def find_swatch(
    character: dict[str, Any],
    zone_key: str,
    swatch_id: str,
) -> tuple[list[dict[str, Any]], int, dict[str, Any]] | None:
    if zone_key == "environment":
        items = active_environment(character).get("palette", [])
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


def reset_recipe(character: dict[str, Any], preset: str = "character") -> None:
    character["recipe"] = make_recipe(preset)


def count_colors(character: dict[str, Any]) -> int:
    total = 0
    for items in (character.get("palettes") or {}).values():
        if isinstance(items, list):
            total += len(items)
    environment = active_environment(character)
    env_palette = environment.get("palette")
    if isinstance(env_palette, list):
        total += len(env_palette)
    return total


def key_colors(character: dict[str, Any], include_private: bool = False) -> list[str]:
    result: list[str] = []
    for zone_key in palette_zone_keys(character):
        if palette_zone_private(character, zone_key) and not include_private:
            continue
        items = (character.get("palettes") or {}).get(zone_key, [])
        if not isinstance(items, list):
            continue
        for swatch in items:
            if isinstance(swatch, dict):
                result.append(normalize_hex(swatch.get("hex"), "#808080"))
                break
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
    environment = active_environment(character)
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


def scene_preview(
    character: dict[str, Any],
    limit: int = 3,
    include_private: bool = False,
) -> list[dict[str, str]]:
    """Colores clave teñidos por la luz del ambiente, para el preview."""
    specs = {item["name"]: item for item in lighting_spec(character)}
    shadow = specs["SHADOW"]
    light = specs["LIGHT"]
    bounce = specs["BOUNCE"]
    rows: list[dict[str, str]] = []
    for zone_key in palette_zone_keys(character):
        if palette_zone_private(character, zone_key) and not include_private:
            continue
        items = (character.get("palettes") or {}).get(zone_key, [])
        if not isinstance(items, list) or not items:
            continue
        swatch = next((item for item in items if isinstance(item, dict)), None)
        if swatch is None:
            continue
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
    for zone_key in palette_zone_keys(character):
        if palette_zone_private(character, zone_key) and not include_private:
            continue
        items = (character.get("palettes") or {}).get(zone_key, [])
        if not isinstance(items, list):
            continue
        for swatch in items:
            if not isinstance(swatch, dict):
                continue
            candidate = normalize_hex(swatch.get("hex"), "#808080")
            distance = delta_e(target, candidate)
            if best is None or distance < best["delta"]:
                best = {"swatch": swatch, "zone": zone_key, "delta": distance}
    return best


def gpl_text(character: dict[str, Any], include_private: bool = False) -> str:
    zones = palette_zones(character)
    lines = [
        "GIMP Palette",
        f"Name: Grimorio - {gpl_safe(character.get('name', 'OC'))}",
        "Columns: 8",
        "#",
    ]
    for zone_key in palette_zone_keys(character):
        if palette_zone_private(character, zone_key) and not include_private:
            continue
        items = (character.get("palettes") or {}).get(zone_key, [])
        if not isinstance(items, list):
            continue
        for swatch in items:
            if not isinstance(swatch, dict):
                continue
            hex_value = normalize_hex(swatch.get("hex"), "#808080")
            red, green, blue = hex_to_rgb(hex_value)
            lines.append(
                f"{red} {green} {blue}\t{gpl_safe(palette_zone_label(zone_key, zones))} · {gpl_safe(swatch.get('name', 'Color'))}"
            )
    environment = active_environment(character)
    env_palette = environment.get("palette")
    if isinstance(env_palette, list):
        env_name = gpl_safe(environment.get("name") or "Ambiente")
        for swatch in env_palette:
            if not isinstance(swatch, dict):
                continue
            hex_value = normalize_hex(swatch.get("hex"), "#808080")
            red, green, blue = hex_to_rgb(hex_value)
            lines.append(
                f"{red} {green} {blue}\t{gpl_safe('Ambiente · ' + env_name)} · {gpl_safe(swatch.get('name', 'Color'))}"
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
    palettes = character.get("palettes")
    if isinstance(palettes, dict):
        for items in palettes.values():
            if not isinstance(items, list):
                continue
            for swatch in items:
                if isinstance(swatch, dict) and swatch.get("id"):
                    used.add(swatch["id"])
    environments = character.get("environments")
    if isinstance(environments, list):
        for environment in environments:
            if not isinstance(environment, dict):
                continue
            if environment.get("id"):
                used.add(environment["id"])
            palette = environment.get("palette")
            if not isinstance(palette, list):
                continue
            for swatch in palette:
                if isinstance(swatch, dict) and swatch.get("id"):
                    used.add(swatch["id"])
    mirror = character.get("environment")
    if isinstance(mirror, dict):
        palette = mirror.get("palette")
        if isinstance(palette, list):
            for swatch in palette:
                if isinstance(swatch, dict) and swatch.get("id"):
                    used.add(swatch["id"])
    for layer in character.get("recipe", []):
        if isinstance(layer, dict) and layer.get("id"):
            used.add(layer["id"])
    return used


def _backup_before_migration(path: Path) -> None:
    standard = path.with_name(path.name + ".v1.bak")
    try:
        current = path.read_bytes()
    except OSError:
        return
    if not standard.exists():
        try:
            shutil.copy2(path, standard)
        except OSError:
            pass
        return
    try:
        if standard.read_bytes() == current:
            return
    except OSError:
        return
    for candidate in path.parent.glob(path.name + ".v1-*.bak"):
        try:
            if candidate.read_bytes() == current:
                return
        except OSError:
            continue
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    try:
        shutil.copy2(path, path.with_name(f"{path.name}.v1-{stamp}.bak"))
    except OSError:
        pass


def _backup_bad_file(path: Path) -> None:
    backup = path.with_name(f"{path.name}.bad-{_now_stamp()}")
    try:
        path.replace(backup)
    except OSError:
        pass
