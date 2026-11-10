# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Traducciones ES/EN del docker.

Las cadenas fuente del código están en español; ``tr()`` devuelve la versión
inglesa cuando el idioma activo es ``en``. Así el mismo código sirve para las
dos comunidades sin duplicar la UI.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

LANGUAGE = "en"

EN: dict[str, str] = {
    # Cabecera y menú
    "Grimorio de Color": "Color Grimoire",
    "Paletas y recetas de tus proyectos": "Palettes and layer recipes for your projects",
    "Menú": "Menu",
    "Idioma": "Language",
    "Importar JSON…": "Import JSON…",
    "Exportar JSON…": "Export JSON…",
    "Exportar .gpl…": "Export .gpl…",
    "Abrir carpeta de datos": "Open data folder",
    "Recargar desde disco": "Reload from disk",
    "Abrir Grimorio web": "Open web Grimoire",
    "Configurar web del Grimorio…": "Set web Grimoire…",
    "Web del Grimorio": "Web Grimoire",
    "Ruta del index.html o URL:": "Path to index.html or URL:",
    "No se encontró el archivo.": "The file was not found.",
    "No se pudo abrir el navegador.": "Could not open the browser.",
    "Web del Grimorio configurada": "Web Grimoire configured",
    "El web Grimorio usa su propio almacenamiento; usa Exportar/Importar JSON para pasar los datos.": "The web Grimoire uses its own storage; use Export/Import JSON to move the data.",
    "Crear plantilla de traducción": "Create translation template",
    "Abrir carpeta de traducciones": "Open translations folder",
    "Recargar traducciones": "Reload translations",
    "Plantilla de traducción": "Translation template",
    "Se creó la plantilla en:": "Template created at:",
    "Copia translation-template.json, cambia code y name, y traduce los valores.": "Copy translation-template.json, change code and name, and translate the values.",
    "Traducciones recargadas": "Translations reloaded",
    "Foto del proyecto": "Project photo",
    "Elegir foto del proyecto": "Choose project photo",
    "Sin foto": "No photo",
    "Añadir foto": "Add photo",
    "Cambiar foto": "Change photo",
    "Quitar foto": "Remove photo",
    "Abrir foto": "Open photo",
    "¿Quitar la foto del proyecto?": "Remove the project photo?",
    "No se pudo cargar la imagen.": "Could not load the image.",
    "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)": "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
    "Ejemplo de la zona": "Zone example",
    "Añadir ejemplo": "Add example",
    "Quitar ejemplo": "Remove example",
    "Elegir ejemplo de la zona": "Choose zone example",
    "Sombra · Base · Luz": "Shadow · Base · Light",
    "Imagen de ejemplo": "Example image",
    "Proyecto": "Project",
    "Nuevo proyecto": "New project",
    "Editar": "Edit",
    "Editar la ficha del proyecto": "Edit the project sheet",
    "Eliminar": "Delete",
    "Eliminar el proyecto": "Delete the project",
    "Clave": "Key",
    "Clic = primer plano · clic derecho = fondo": "Click = foreground · right-click = background",
    "Clic: primer plano · clic derecho: fondo": "Click: foreground · right-click: background",
    "Aplicar opacidad del color": "Apply color opacity",
    "Si está marcado, el color se aplica con el alfa del swatch.": "If checked, the color uses the swatch alpha.",
    "Guardado": "Saved",
    "Guardado ": "Saved ",
    "Error al guardar": "Error saving",
    "Error al crear las capas": "Error creating layers",
    "Grupo creado en el documento": "Group created in the document",
    "Abre un documento en Krita": "Open a document in Krita",
    "Color aplicado ": "Color applied ",
    "No se pudo abrir la carpeta": "Could not open the folder",
    "Abrir carpeta": "Open folder",
    "Recargado desde disco": "Reloaded from disk",
    "JSON importado": "JSON imported",
    "JSON exportado": "JSON exported",
    "Paleta .gpl exportada": "Palette .gpl exported",
    "Color Guard": "Color Guard",
    "Snap": "Snap",
    "Marca para comparar el color actual con la paleta.": "Check to compare the current color with the palette.",
    "En paleta": "In palette",
    "Fuera de paleta": "Off-palette",
    "Sin colores en la paleta": "No palette colors",
    "Crear luces en Krita": "Create lighting rig",
    "Guarda el ambiente antes de crear las luces.": "Save the environment before creating the lights.",
    "Luces creadas": "Lighting rig created",
    "Error al crear las luces": "Error creating the lighting rig",
    "VISTA DE ESCENA": "SCENE PREVIEW",
    "Cómo cambian los colores clave con esta luz.": "How the key colors shift under this light.",
    "Lineart limpio": "Clean lineart",
    "Colores planos": "Flat colors",
    "Sombra general": "General shadow",
    "Oclusión en grietas": "Occlusion in creases",
    "Luz principal": "Main light",
    "Brillo": "Glow",
    "Textura / ajuste": "Texture / adjustment",
    # Tabs y ficha
    "Ficha": "Sheet",
    "Paletas": "Palettes",
    "Capas": "Layers",
    "Ambiente": "Environment",
    "Biblioteca": "Library",
    "Paletas reutilizables; se importan por copia.": "Reusable palettes; imported by copy.",
    "RESUMEN": "SUMMARY",
    "HISTORIA": "HISTORY",
    "PERSONALIDAD": "PERSONALITY",
    "RELACIONES": "RELATIONSHIPS",
    "Sin resumen todavía.": "No summary yet.",
    "Sin nombre": "Unnamed",
    "Crea un proyecto para empezar a guardar sus paletas por zona.": "Create a project to start saving palettes by zone.",
    "Todavía no hay proyectos. Crea uno con el botón + de la cabecera.": "No projects yet. Create one with the + button in the header.",
    "Sin detalles": "No details",
    "Editar ficha": "Edit sheet",
    # Zonas de paleta
    "Editar zonas": "Edit zones",
    "Zonas guardadas": "Zones saved",
    "Etiqueta": "Label",
    "Acciones": "Actions",
    "Añadir zona": "Add zone",
    "Guardar zonas": "Save zones",
    "Eliminar zona": "Delete zone",
    "Subir zona": "Move zone up",
    "Bajar zona": "Move zone down",
    "Privada": "Private",
    "Zona": "Zone",
    "Debe haber al menos una zona.": "There must be at least one zone.",
    "Cada zona necesita una etiqueta.": "Every zone needs a label.",
    # Paletas
    "Añadir": "Add",
    "Añadir color": "Add color",
    "Editar color": "Edit color",
    "Eliminar color": "Delete color",
    "Sin colores todavía.": "No colors yet.",
    "Mostrar privado": "Show private",
    "Oculto por privacidad. Activa «Mostrar privado».": "Hidden for privacy. Turn on “Show private”.",
    "Piel": "Skin",
    "Pelo": "Hair",
    "Ojos": "Eyes",
    "Ropa": "Clothing",
    "Armadura": "Armor",
    "Accesorios": "Accessories",
    "Privado": "Private",
    "Marcas y cicatrices": "Marks & scars",
    "Cara y cuerpo": "Face & body",
    "Cuerpo": "Body",
    "Torso y brazos": "Torso & arms",
    "Manos y cuello": "Hands & neck",
    "Zona íntima": "Intimate area",
    "Según la marca": "Depends on the mark",
    "Cara": "Face",
    "Boca": "Mouth",
    "Torso": "Torso",
    "Brazos": "Arms",
    "Manos": "Hands",
    "Piernas": "Legs",
    "Pies": "Feet",
    "Uñas": "Nails",
    "Cicatrices": "Scars",
    "Tatuajes": "Tattoos",
    "Genitales": "Genitals",
    "Vello": "Body hair",
    "Otro": "Other",
    # Roles y blends
    "Base": "Base",
    "Sombra": "Shadow",
    "Luz": "Light",
    "Acento": "Accent",
    "Detalle": "Detail",
    "Normal": "Normal",
    "Multiply": "Multiply",
    "Add": "Add",
    "Screen": "Screen",
    "Overlay": "Overlay",
    "Soft Light": "Soft Light",
    "Color Dodge": "Color Dodge",
    "Burn": "Burn",
    "Linear Burn": "Linear Burn",
    "Pass Through": "Pass Through",
    # Capas
    "RECETA DE CAPAS (": "LAYER RECIPE (",
    "Añadir capa": "Add layer",
    "Restaurar base": "Reset base",
    "Crear capas en Krita": "Create layers in Krita",
    "Arriba = encima en Krita. Los blend modes se aplican al crear.": "Top = topmost in Krita. Blend modes are applied on creation.",
    "Sin capas. Añade una o restaura la receta base.": "No layers. Add one or reset the base recipe.",
    "Subir capa": "Move layer up",
    "Bajar capa": "Move layer down",
    "Capa": "Layer",
    "Editar capa": "Edit layer",
    "Eliminar capa": "Delete layer",
    "Restaurar receta": "Reset recipe",
    "Se reemplazará la receta actual por la base (LINE, BASE, SHADOW…). ¿Continuar?": "Replace the current recipe with the base (LINE, BASE, SHADOW…). Continue?",
    "Crea un proyecto para definir su receta de capas.": "Create a project to define its layer recipe.",
    # Ambiente
    "AMBIENTE": "ENVIRONMENT",
    "PALETA DEL AMBIENTE": "ENVIRONMENT PALETTE",
    "Bosque de ceniza al atardecer": "Ash forest at dusk",
    "Atardecer, noche, amanecer…": "Dusk, night, dawn…",
    "Neblina, lluvia, despejado…": "Fog, rain, clear…",
    "Cálido, húmedo, contraluz…": "Warm, humid, backlit…",
    "Guardar ambiente": "Save environment",
    "Añadir color de ambiente": "Add environment color",
    "Crea un proyecto para describir la luz y la paleta de su ambiente.": "Create a project to describe its light and environment palette.",
    "Hora": "Time",
    "Clima": "Weather",
    "Mood": "Mood",
    "Luz clave": "Key light",
    "Sombra": "Shadow",
    "Rebote": "Bounce",
    "Sin colores de ambiente. Añade la luz y los reflejos.": "No environment colors. Add the light and reflections.",
    "Ambiente": "Environment",
    # Diálogos
    "Añadir color": "Add color",
    "Añadir proyecto": "Add project",
    "Editar proyecto": "Edit project",
    "Eliminar proyecto": "Delete project",
    "Añadir capa": "Add layer",
    "Nombre": "Name",
    "HEX": "HEX",
    "Rol": "Role",
    "Parte del cuerpo": "Body part",
    "Para qué": "Purpose",
    "Opacidad": "Opacity",
    "Nota": "Note",
    "Etiquetas": "Tags",
    "Resumen": "Summary",
    "Historia": "History",
    "Personalidad": "Personality",
    "Relaciones": "Relationships",
    "Blend mode": "Blend mode",
    "Propósito": "Purpose",
    "Guardar": "Save",
    "Cancelar": "Cancel",
    "Guardar color": "Save color",
    "Guardar capa": "Save layer",
    "Nombre del color": "Color name",
    "Color": "Color",
    "Rol en la paleta": "Palette role",
    "Nombre del ambiente": "Environment name",
    "Falta el nombre": "Missing name",
    "El color necesita un nombre.": "The color needs a name.",
    "HEX no válido": "Invalid HEX",
    "Escribe un color en formato #rrggbb (por ejemplo #c98d6b).": "Enter a color as #rrggbb (for example #c98d6b).",
    "El proyecto necesita un nombre.": "The project needs a name.",
    "La capa necesita un nombre.": "The layer needs a name.",
    "¿Eliminar «": "Delete “",
    "»?": "”?",
    "» con todas sus paletas y recetas?": "” with all its palettes and recipes?",
    "¿Eliminar la capa «": "Delete layer “",
    "» de la receta?": "” from the recipe?",
    "este proyecto": "this project",
    "este color": "this color",
    "esta capa": "this layer",
    "Importar JSON": "Import JSON",
    "Exportar JSON": "Export JSON",
    "Exportar .gpl": "Export .gpl",
    "JSON (*.json);;Todos los archivos (*)": "JSON (*.json);;All files (*)",
    "JSON (*.json)": "JSON (*.json)",
    "Paleta GIMP (*.gpl)": "GIMP palette (*.gpl)",
    "Se reemplazarán todas las fichas, paletas y recetas actuales. ¿Continuar?": "Replace all current sheets, palettes and recipes. Continue?",
    "Se reemplazará la receta actual por la base (LINE, BASE, SHADOW…). ¿Continuar?": "Replace the current recipe with the base (LINE, BASE, SHADOW…). Continue?",
    "Elegir color": "Choose color",
    "Elegir color…": "Choose color…",
    "Piel base, Sombra de cuello…": "Base skin, Neck shadow…",
    "Para qué sirve este color": "What this color is for",
    "Nota libre: mezcla, referencia, cuidado al pintar…": "Free note: mix, reference, caution when painting…",
    "Nombre del proyecto": "Project name",
    "fantasía, guerrera, guardia": "fantasy, warrior, guard",
    "Resumen de tres líneas para recordar quién es.": "Three lines to remember who they are.",
    "Origen, motivación, deudas pendientes…": "Origin, motivation, outstanding debts…",
    "Cómo es, qué evita, qué le relaja.": "How they are, what they avoid, what relaxes them.",
    "Familia, aliados, rivales, deudas.": "Family, allies, rivals, debts.",
    "Separados por comas.": "Comma-separated.",
    "SHADOW, LIGHT, FX…": "SHADOW, LIGHT, FX…",
    "Propósito de la capa": "Layer purpose",
    "Qué resuelve esta capa y qué hay que vigilar.": "What this layer solves and what to watch for.",
    "color": "color",
    "color de ambiente": "environment color",
    "Editar ": "Edit ",
    "Añadir ": "Add ",
    " colores": " colors",
    " colores · ": " colors · ",
    " capas en la receta": " layers in the recipe",
    "Cerrar": "Close",
    "Cerrar ficha": "Close sheet",
    "Cerrar color": "Close color",
    "Cerrar capa": "Close layer",
    "Cerrar el panel": "Close panel",
    "Elemento / parte del cuerpo": "Element / body part",
    "Aplicar receta": "Apply recipe",
    "Aplicar preset": "Apply preset",
    "Personaje": "Character",
    "Entorno": "Environment",
    "Prop": "Prop",
    "Se reemplazará la receta actual. ¿Continuar?": "The current recipe will be replaced. Continue?",
    "Preset aplicado; guarda el ambiente.": "Preset applied; save the environment.",
    "Amanecer": "Dawn",
    "Día": "Day",
    "Atardecer": "Sunset",
    "Noche": "Night",
    "Niebla": "Fog",
    "Tipo": "Type",
    "Escenario": "Scene",
    "Elemento": "Element",
    "Ambiente activo": "Active environment",
    "Añadir ambiente": "Add environment",
    "Duplicar": "Duplicate",
    "Cambiar tipo": "Change type",
    "¿Aplicar las zonas y la receta de este tipo? Las paletas actuales se conservan como zonas ocultas.": "Apply this type's zones and recipe? Current palettes are kept as hidden zones.",
    "No se puede eliminar el último ambiente.": "The last environment cannot be deleted.",
    "Eliminar ambiente": "Delete environment",
    "Ambiente sin nombre": "Unnamed environment",
    "Sin ambiente definido.": "No environment defined.",
    # Biblioteca
    "Crear desde zona": "Create from zone",
    "Guardar zona en biblioteca": "Save zone to library",
    "Cielo de atardecer": "Sunset sky",
    "Importar": "Import",
    "Renombrar": "Rename",
    "Renombrar paleta": "Rename palette",
    "Eliminar paleta": "Delete palette",
    "Paleta guardada en la biblioteca": "Palette saved to the library",
    "Paleta importada": "Palette imported",
    "Paleta renombrada": "Palette renamed",
    "Paleta eliminada": "Palette deleted",
    "No hay paletas en la biblioteca.": "No palettes in the library.",
    "Paleta sin nombre": "Unnamed palette",
}

CUSTOM: dict[str, dict[str, str]] = {}
CUSTOM_NAMES: dict[str, str] = {}
BUILTIN: dict[str, str] = {"es": "Español", "en": "English"}


def available_languages() -> list[tuple[str, str]]:
    items = list(BUILTIN.items())
    for code, name in CUSTOM_NAMES.items():
        if code not in BUILTIN:
            items.append((code, name))
    return items


def set_language(language: str) -> None:
    global LANGUAGE
    code = str(language or "").strip().lower()
    supported = {item[0] for item in available_languages()}
    if code not in supported:
        code = detect_language()
    LANGUAGE = code


def get_language() -> str:
    return LANGUAGE


def detect_language() -> str:
    explicit = os.environ.get("GRIMORIO_LANG", "").strip().lower()
    if explicit:
        if explicit in BUILTIN or explicit in CUSTOM:
            return explicit
        prefix = explicit.split("_")[0].split("-")[0]
        if prefix in BUILTIN or prefix in CUSTOM:
            return prefix
    locale = (os.environ.get("LC_ALL") or os.environ.get("LANG") or "").strip().lower()
    prefix = locale.split("_")[0].split("-")[0] if locale else ""
    if prefix in BUILTIN or prefix in CUSTOM:
        return prefix
    return "en"


def tr(text: str) -> str:
    if LANGUAGE == "es":
        return text
    if LANGUAGE == "en":
        return EN.get(text, text)
    translated = CUSTOM.get(LANGUAGE, {}).get(text, "")
    return translated or text


def load_translations(
    directory: str | Path,
    extra_directories: list[str | Path] | None = None,
) -> list[tuple[str, str]]:
    CUSTOM.clear()
    CUSTOM_NAMES.clear()
    paths = [Path(item) for item in (extra_directories or [])]
    paths.append(Path(directory))
    for path in paths:
        if not path.exists():
            continue
        for file in sorted(path.glob("*.json")):
            if file.name in {"translation-template.json", "template.json"}:
                continue
            try:
                raw = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            code = str(raw.get("code") or "").strip().lower()
            name = str(raw.get("name") or "").strip()
            strings = raw.get("strings")
            if not code or code in {"es", "en", "xx"} or not isinstance(strings, dict):
                continue
            cleaned = {
                str(key): str(value)
                for key, value in strings.items()
                if isinstance(value, str) and value.strip()
            }
            CUSTOM[code] = cleaned
            CUSTOM_NAMES[code] = name or code
    return available_languages()


def write_template(directory: str | Path) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    target = path / "translation-template.json"
    data = {
        "code": "xx",
        "name": "My language",
        "strings": {key: "" for key in EN},
    }
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def ensure_translations_dir(directory: str | Path) -> Path:
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    template = path / "translation-template.json"
    if not template.exists():
        write_template(path)
    readme = path / "README.txt"
    if not readme.exists():
        readme.write_text(
            "Color Grimoire translations\n"
            "===========================\n\n"
            "1. Copy translation-template.json to <code>.json, for example fr.json.\n"
            "2. Set \"code\" to the language code (fr, de, ...) and \"name\" to the language name.\n"
            "3. Translate the VALUES in \"strings\". The keys are the Spanish source strings.\n"
            "   Empty or missing values fall back to Spanish.\n"
            "4. In Krita: ... -> Language -> Reload translations (or restart Krita).\n\n"
            "The translation-template.json file is ignored by the plugin.\n",
            encoding="utf-8",
        )
    return path
