# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Prueba de la UI del Grimorio sin Krita (PyQt5 offscreen).

Ejecutar con el Python de Krita Flatpak:
    flatpak run --command=python3 org.kde.krita test_ui_offscreen.py

Usa un ``FakeBridge`` y un JSON temporal: no toca los datos reales.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
# El Flatpak de Krita trae QT_QPA_PLATFORMTHEME=gtk3; sin pantalla eso intenta
# abrir X11 y aborta antes de llegar a QApplication. Offscreen no lo necesita.
os.environ["QT_QPA_PLATFORMTHEME"] = ""

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

_TEMP_DIR = tempfile.TemporaryDirectory(prefix="grimorio-ui-")

import model  # noqa: E402

# Datos aislados y deterministas: load_state() devolverá el seed.
model.DATA_FILE = Path(_TEMP_DIR.name) / "grimorio.json"

_TRANSLATIONS = Path(_TEMP_DIR.name) / "translations"
_TRANSLATIONS.mkdir(parents=True, exist_ok=True)
(_TRANSLATIONS / "fr.json").write_text(
    json.dumps(
        {
            "code": "fr",
            "name": "Français",
            "strings": {
                "Ficha": "Fiche",
                "Grimorio de Color": "Grimoire de Couleur",
                "Paletas": "Palettes",
            },
        },
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

import ui  # noqa: E402
from qt_compat import QApplication, QColor, QPixmap, QSettings  # noqa: E402


class FakeBridge:
    def __init__(self):
        self.calls = []
        self.layer_character = None
        self.lighting_character = None
        self.foreground = ("#c98d6b", 255)

    def set_foreground(self, hex_color, opacity=100):
        self.calls.append(("foreground", hex_color, opacity))
        return True

    def set_background(self, hex_color, opacity=100):
        self.calls.append(("background", hex_color, opacity))
        return True

    def create_layer_stack(self, character):
        self.layer_character = character.get("name")
        self.calls.append(("layers", character.get("name")))
        return "Grimorio - " + str(character.get("name"))

    def create_lighting_rig(self, character):
        self.lighting_character = character.get("name")
        self.calls.append(("lighting", character.get("name")))
        return "Lighting — test"

    def foreground_color(self):
        return self.foreground


def main() -> int:
    app = QApplication.instance() or QApplication([])
    fake = FakeBridge()
    panel = ui.GrimorioPanel(bridge=fake)
    panel.resize(380, 920)
    panel.show()
    app.processEvents()

    out_dir = Path.home() / ".cache" / "grimorio-shots"
    out_dir.mkdir(parents=True, exist_ok=True)

    assert panel.character_combo.count() == 2, panel.character_combo.count()
    assert panel.tabs.count() == 4, panel.tabs.count()
    assert panel.state["characters"][0]["name"] == "Rowan Vale"
    assert panel.action_lang_en.isChecked() == (panel._language == "en")
    assert panel.action_lang_es.isChecked() == (panel._language == "es")

    # Ficha
    panel.tabs.setCurrentIndex(0)
    app.processEvents()
    assert panel.grab().save(str(out_dir / "grimorio-panel-ficha.png"))

    # Colores: primer plano, fondo y opacidad opcional
    panel.apply_color("#c98d6b", 100, background=False)
    panel.apply_color("#c98d6b", 100, background=True)
    assert ("foreground", "#c98d6b", 100) in fake.calls, fake.calls
    assert ("background", "#c98d6b", 100) in fake.calls, fake.calls

    panel.apply_opacity.setChecked(True)
    panel.apply_color("#123456", 45, background=False)
    assert ("foreground", "#123456", 45) in fake.calls, fake.calls
    panel.apply_opacity.setChecked(False)

    # Cambio de OC
    panel.character_combo.setCurrentIndex(1)
    app.processEvents()
    assert panel.state["activeCharacterId"] == panel.state["characters"][1]["id"]
    assert panel._character()["name"] == "Mika Sato", panel._character()["name"]
    panel.character_combo.setCurrentIndex(0)
    app.processEvents()

    # Crear capas
    panel.create_layers()
    assert fake.layer_character == "Rowan Vale", fake.layer_character
    panel.create_lighting_rig()
    assert fake.lighting_character == "Rowan Vale", fake.lighting_character

    # Color Guard
    panel.color_guard.setChecked(True)
    fake.foreground = ("#c98d6b", 255)
    panel._check_color_guard()
    assert "Base skin" in panel.guard_status.text(), panel.guard_status.text()
    fake.foreground = ("#123456", 255)
    panel._check_color_guard()
    assert panel._guard_target is not None
    assert not panel.guard_snap.isHidden()
    before = len(fake.calls)
    panel.guard_snap.click()
    assert len(fake.calls) > before, fake.calls
    panel.color_guard.setChecked(False)

    # Paletas visibles
    panel.tabs.setCurrentIndex(1)
    panel.palettes_scroll.verticalScrollBar().setValue(0)
    app.processEvents()
    assert panel.grab().save(str(out_dir / "grimorio-panel.png"))

    # Privado: mostrar y capturar la zona privada
    panel._set_private_visible(True)
    app.processEvents()
    assert panel.state["privateMode"] is False
    panel.palettes_scroll.verticalScrollBar().setValue(
        panel.palettes_scroll.verticalScrollBar().maximum()
    )
    app.processEvents()
    assert panel.grab().save(str(out_dir / "grimorio-panel-private.png"))
    panel._set_private_visible(False)
    app.processEvents()
    assert panel.state["privateMode"] is True

    # Capas
    panel.tabs.setCurrentIndex(2)
    panel.layers_scroll.verticalScrollBar().setValue(0)
    app.processEvents()
    assert panel.grab().save(str(out_dir / "grimorio-panel-capas.png"))

    # Ambiente: editar y guardar
    panel.tabs.setCurrentIndex(3)
    panel.env_name.setText("Prueba de ambiente")
    panel.env_time.setText("Noche")
    panel.env_weather.setText("Lluvia")
    panel.env_mood.setText("Frío")
    panel.env_key.set_value("#ffcc88")
    panel.env_shadow.set_value("#223344")
    panel.env_bounce.set_value("#665544")
    panel.save_environment()
    app.processEvents()
    environment = panel._character()["environment"]
    assert environment["name"] == "Prueba de ambiente", environment
    assert environment["keyLight"] == "#ffcc88", environment
    assert environment["shadowTint"] == "#223344", environment
    assert panel.grab().save(str(out_dir / "grimorio-panel-ambiente.png"))

    # Diálogo de color
    swatch = ui.SwatchDialog(parent=panel, default_body="Cara")
    swatch.name_edit.setText("Color de prueba")
    swatch.hex_edit.setText("#123456")
    swatch.purpose_edit.setText("Para probar")
    swatch.opacity_spin.setValue(60)
    swatch.body_combo.setCurrentText("Brazo")
    swatch.role_combo.setCurrentIndex(1)
    swatch.note_edit.setPlainText("Nota de prueba")
    data = swatch.data()
    assert data["name"] == "Color de prueba", data
    assert data["hex"] == "#123456", data
    assert data["purpose"] == "Para probar", data
    assert data["opacity"] == 60, data
    assert data["bodyPart"] == "Brazo", data
    assert data["role"] == "shadow", data
    swatch.show()
    app.processEvents()
    assert swatch.grab().save(str(out_dir / "grimorio-dialog-swatch.png"))
    swatch.close()

    # Diálogo de OC
    character_dialog = ui.CharacterDialog(parent=panel)
    character_dialog.name_edit.setText("OC de prueba")
    character_dialog.tags_edit.setText("test, temporal")
    character_dialog.summary_edit.setPlainText("Resumen de prueba")
    character_data = character_dialog.data()
    assert character_data["name"] == "OC de prueba", character_data
    assert character_data["tags"] == ["test", "temporal"], character_data
    character_dialog.show()
    app.processEvents()
    assert character_dialog.grab().save(str(out_dir / "grimorio-dialog-oc.png"))
    character_dialog.close()

    # Diálogo de capa
    layer_dialog = ui.LayerDialog(parent=panel)
    layer_dialog.name_edit.setText("TEST")
    layer_dialog.blend_combo.setCurrentIndex(1)
    layer_dialog.opacity_spin.setValue(40)
    layer_dialog.purpose_edit.setText("Prueba")
    layer_data = layer_dialog.data()
    assert layer_data["name"] == "TEST", layer_data
    assert layer_data["blend"] == "multiply", layer_data
    assert layer_data["opacity"] == 40, layer_data
    layer_dialog.show()
    app.processEvents()
    assert layer_dialog.grab().save(str(out_dir / "grimorio-dialog-layer.png"))
    layer_dialog.close()

    # Foto del OC y ejemplo de zona.
    image_path = Path(_TEMP_DIR.name) / "sample.png"
    image = QPixmap(40, 60)
    image.fill(QColor("#c98d6b"))
    assert image.save(str(image_path))
    character = panel._character()
    character["referenceImage"] = model.store_image(image_path, "oc")
    character.setdefault("zoneExamples", {})["skin"] = model.store_image(image_path, "zone-skin")
    panel._save()
    panel.refresh()
    app.processEvents()
    photo = panel.findChild(ui.QLabel, "oc_photo")
    assert photo is not None and photo.pixmap() is not None and not photo.pixmap().isNull()
    zone_photos = panel.findChildren(ui.QLabel, "zone_example_photo")
    assert zone_photos and any(
        label.pixmap() is not None and not label.pixmap().isNull() for label in zone_photos
    )

    # Botón web: ruta configurada y apertura simulada.
    web_index = Path(_TEMP_DIR.name) / "index.html"
    web_index.write_text("<html></html>", encoding="utf-8")
    panel.settings = QSettings(str(Path(_TEMP_DIR.name) / "settings.ini"))
    panel.settings.setValue("webAppPath", str(web_index))
    assert panel.web_target() == str(web_index)

    class FakeDesktopServices:
        calls = []

        @staticmethod
        def openUrl(url):
            FakeDesktopServices.calls.append(url)
            return True

    original_desktop = ui.QDesktopServices
    ui.QDesktopServices = FakeDesktopServices
    try:
        panel.web_button.click()
        assert FakeDesktopServices.calls
        assert FakeDesktopServices.calls[-1].toLocalFile() == str(web_index)
    finally:
        ui.QDesktopServices = original_desktop

    # Cambio de idioma con una traducción personalizada.
    panel.settings = QSettings(str(Path(_TEMP_DIR.name) / "settings.ini"))
    assert "fr" in panel.language_actions, list(panel.language_actions)
    panel.set_language("fr")
    app.processEvents()
    app.processEvents()
    assert panel._language == "fr", panel._language
    assert panel.tabs.tabText(0) == "Fiche", panel.tabs.tabText(0)
    assert panel.findChild(ui.QLabel, "title").text() == "Grimoire de Couleur"
    panel.set_language("en")
    app.processEvents()
    app.processEvents()
    assert panel._language == "en", panel._language
    assert panel.tabs.tabText(0) == "Sheet", panel.tabs.tabText(0)
    assert panel.findChild(ui.QLabel, "title").text() == "Color Grimoire"

    print("UI OK")
    for name in (
        "grimorio-panel-ficha.png",
        "grimorio-panel.png",
        "grimorio-panel-private.png",
        "grimorio-panel-capas.png",
        "grimorio-panel-ambiente.png",
        "grimorio-dialog-swatch.png",
        "grimorio-dialog-oc.png",
        "grimorio-dialog-layer.png",
    ):
        print(str(out_dir / name))

    panel.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
