# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Interfaz del docker «Grimorio de Color» para Krita 5 y Krita 6.

La UI no depende de Krita: recibe un ``bridge`` con ``set_foreground``,
``set_background`` y ``create_layer_stack``. ``qt_compat`` unifica PyQt5
(Krita 5) y PyQt6 (Krita 6).
"""

from __future__ import annotations

import html
import os
import re
from datetime import datetime
from pathlib import Path

try:
    from .qt_compat import (
        DialogCode,
        MsgBox,
        QAction,
        QBrush,
        QCheckBox,
        QColor,
        QColorDialog,
        QComboBox,
        QDesktopServices,
        QDialog,
        QFileDialog,
        QPixmap,
        QFileSystemWatcher,
        QFormLayout,
        QFrame,
        FrameShape,
        QLocale,
        QSettings,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLinearGradient,
        QLineEdit,
        QMenu,
        QMessageBox,
        QPainter,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QTimer,
        QToolButton,
        QUrl,
        QVBoxLayout,
        QWidget,
        Qt,
        SizePolicy,
        ToolButtonPopupMode,
        exec_dialog,
        pyqtSignal,
    )
except ImportError:  # Modulo suelto para las pruebas.
    from qt_compat import (
        DialogCode,
        MsgBox,
        QAction,
        QBrush,
        QCheckBox,
        QColor,
        QColorDialog,
        QComboBox,
        QDesktopServices,
        QDialog,
        QFileDialog,
        QPixmap,
        QFileSystemWatcher,
        QFormLayout,
        QFrame,
        FrameShape,
        QLocale,
        QSettings,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLinearGradient,
        QLineEdit,
        QMenu,
        QMessageBox,
        QPainter,
        QPushButton,
        QScrollArea,
        QSlider,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QTimer,
        QToolButton,
        QUrl,
        QVBoxLayout,
        QWidget,
        Qt,
        SizePolicy,
        ToolButtonPopupMode,
        exec_dialog,
        pyqtSignal,
    )

try:
    from . import i18n, model
    from .i18n import tr
    from .krita_bridge import KritaBridge
except ImportError:  # Modulo suelto para las pruebas.
    import i18n
    import model
    from i18n import tr
    from krita_bridge import KritaBridge


STYLE_SHEET = """
QWidget {
    font-family: "DejaVu Sans", "Noto Sans", "Segoe UI", sans-serif;
    font-size: 12px;
    color: #f2eee8;
}
QWidget#grimorio_panel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1b1721, stop:1 #141217);
}
QDialog#grimorio_dialog, QMessageBox {
    background-color: #17151b;
}
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background-color: transparent;
}
QTabWidget::pane {
    background-color: transparent;
    border: none;
}
QTabBar::tab {
    background-color: transparent;
    color: #b8afc0;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 6px 8px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    color: #f2eee8;
    border-bottom: 2px solid #e8a05c;
}
QTabBar::tab:hover {
    color: #f2eee8;
    background-color: #211e27;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QLabel#title {
    font-family: "DejaVu Serif", "Georgia", serif;
    font-size: 18px;
    font-weight: 600;
    color: #f2eee8;
}
QLabel#subtitle {
    color: #b8afc0;
    font-size: 10px;
}
QLabel#character_name {
    font-family: "DejaVu Serif", "Georgia", serif;
    font-size: 17px;
    font-weight: 600;
    color: #f2eee8;
}
QLabel#field_label {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#card_title {
    color: #b8afc0;
    font-size: 10px;
    font-weight: 700;
}
QLabel#card_body {
    color: #f2eee8;
    font-size: 12px;
}
QLabel#tag_line {
    color: #e8a05c;
    font-size: 11px;
}
QLabel#hint {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#status {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#status[error="true"] {
    color: #c45c5c;
}
QLabel#swatch_name {
    font-weight: 600;
    color: #f2eee8;
}
QLabel#swatch_meta {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#swatch_note {
    color: #b8afc0;
    font-size: 11px;
    font-style: italic;
}
QLabel#swatch_hex {
    color: #b8afc0;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 10px;
}
QLabel#empty_note {
    color: #b8afc0;
    font-size: 11px;
    font-style: italic;
}
QLabel#private_hidden {
    color: #b8afc0;
    font-size: 11px;
    font-style: italic;
    padding: 6px 2px;
}
QLabel#guard_status {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#guard_status[state="ok"] {
    color: #8fd694;
}
QLabel#guard_status[state="warn"] {
    color: #f4bb78;
}
QLabel#guard_status[state="muted"] {
    color: #b8afc0;
}
QLabel#zone_title_skin, QLabel#zone_title_hair, QLabel#zone_title_eyes,
QLabel#zone_title_outfit, QLabel#zone_title_armor,
QLabel#zone_title_accessories, QLabel#zone_title_intimate,
QLabel#zone_title_scars, QLabel#zone_title_environment {
    font-size: 12px;
    font-weight: 600;
    color: #f2eee8;
}
QLabel#layer_name {
    font-weight: 600;
    color: #f2eee8;
}
QLabel#layer_purpose {
    color: #b8afc0;
    font-size: 11px;
}
QLabel#layer_index {
    color: #e8a05c;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 11px;
}
QLabel#layer_opacity {
    color: #b8afc0;
    font-family: "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 10px;
}
QLabel#role_badge {
    border-radius: 7px;
    padding: 1px 6px;
    font-size: 10px;
    font-weight: 600;
}
QLabel#role_badge[role="base"] {
    background-color: #2f5f86;
    color: #edf6fd;
}
QLabel#role_badge[role="shadow"] {
    background-color: #56447a;
    color: #f2ecfb;
}
QLabel#role_badge[role="light"] {
    background-color: #d9a94e;
    color: #1f1508;
}
QLabel#role_badge[role="accent"] {
    background-color: #a9503c;
    color: #fff2ee;
}
QLabel#role_badge[role="detail"] {
    background-color: #3f6b58;
    color: #eaf6ef;
}
QLabel#opacity_badge {
    background-color: #2a2632;
    border: 1px solid #3a3440;
    border-radius: 7px;
    color: #b8afc0;
    font-size: 10px;
    padding: 1px 5px;
}
QLabel#blend_badge {
    background-color: #3a2a1a;
    border: 1px solid #4a3722;
    border-radius: 7px;
    color: #f4bb78;
    font-size: 10px;
    padding: 1px 5px;
}
QFrame#header_rule {
    background-color: #3a3440;
    border: none;
}
QFrame#card {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 10px;
}
QFrame#oc_hero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #26212c, stop:1 #1b1820);
    border: 1px solid #3a3440;
    border-radius: 10px;
}
QLabel#oc_photo {
    background-color: #1b1920;
    border: 1px solid #2f2a38;
    border-radius: 8px;
    color: #b8afc0;
    font-size: 11px;
}
QLabel#oc_photo[empty="true"] {
    border: 1px dashed #4f475a;
}
QFrame#zone_example {
    background-color: #1b1920;
    border: 1px solid #2f2a38;
    border-radius: 8px;
}
QLabel#zone_example_photo {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 6px;
    color: #b8afc0;
    font-size: 10px;
}
QFrame#scene_preview {
    background-color: #1b1920;
    border: 1px solid #2f2a38;
    border-radius: 10px;
}
QFrame#zone_block {
    background-color: #1b1920;
    border: 1px solid #2f2a38;
    border-radius: 10px;
}
QFrame#swatch_card {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 9px;
}
QFrame#swatch_card:hover {
    background-color: #241f2a;
    border-color: #6a563f;
}
QFrame#layer_row {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 8px;
}
QFrame#layer_row:hover {
    border-color: #4f475a;
}
QPushButton {
    background-color: #2a2632;
    border: 1px solid #3a3440;
    border-radius: 8px;
    color: #f2eee8;
    padding: 4px 8px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #332e3c;
    border-color: #4f475a;
}
QPushButton:pressed {
    background-color: #211e27;
}
QPushButton:focus {
    border-color: #e8a05c;
}
QPushButton:disabled {
    background-color: #211e27;
    border-color: #2f2a38;
    color: #6f677c;
}
QPushButton[small="true"] {
    font-size: 11px;
    padding: 0 5px;
    min-height: 18px;
}
QPushButton[accent="true"] {
    color: #e8a05c;
}
QPushButton[accent="true"]:hover {
    color: #f4bb78;
    border-color: #6a563f;
}
QPushButton[danger="true"] {
    color: #c45c5c;
}
QPushButton[danger="true"]:hover {
    background-color: #3a211d;
    border-color: #c45c5c;
    color: #e08a7a;
}
QLabel#dialog_title {
    font-family: "DejaVu Serif", "Georgia", serif;
    font-size: 16px;
    font-weight: 700;
    color: #f2eee8;
}
QPushButton#dialog_close {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 7px;
    color: #b8afc0;
    font-size: 13px;
    padding: 0;
    min-width: 24px;
    max-width: 24px;
    min-height: 24px;
    max-height: 24px;
}
QPushButton#dialog_close:hover {
    background-color: #2a2632;
    border-color: #4f475a;
    color: #f2eee8;
}
QPushButton#btn_create_layers, QPushButton#btn_save_environment,
QPushButton#btn_create_lighting, QPushButton#dialog_save {
    background-color: #e8a05c;
    border-color: #e8a05c;
    color: #1a1512;
    font-weight: 600;
}
QPushButton#btn_create_layers:hover, QPushButton#btn_save_environment:hover,
QPushButton#btn_create_lighting:hover, QPushButton#dialog_save:hover {
    background-color: #f4bb78;
    border-color: #f4bb78;
    color: #1a1512;
}
QPushButton#btn_create_layers:pressed, QPushButton#btn_save_environment:pressed,
QPushButton#btn_create_lighting:pressed, QPushButton#dialog_save:pressed {
    background-color: #d38e4a;
    border-color: #d38e4a;
}
QToolButton#menu_button, QToolButton#web_button {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 8px;
    color: #f2eee8;
    font-size: 17px;
    padding: 0;
}
QToolButton#web_button {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.02em;
}
QToolButton#menu_button:hover, QToolButton#web_button:hover {
    background-color: #2a2632;
    border-color: #4f475a;
}
QToolButton#menu_button::menu-indicator {
    image: none;
    width: 0;
}
QComboBox, QLineEdit, QSpinBox, QTextEdit {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 8px;
    color: #f2eee8;
    padding: 4px 7px;
    selection-background-color: #e8a05c;
    selection-color: #1a1512;
}
QComboBox:hover, QLineEdit:hover, QSpinBox:hover, QTextEdit:hover {
    border-color: #4f475a;
}
QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QTextEdit:focus {
    border-color: #e8a05c;
}
QComboBox {
    min-height: 20px;
}
QComboBox::drop-down {
    border: none;
    width: 18px;
}
QComboBox QAbstractItemView {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 8px;
    padding: 3px;
    color: #f2eee8;
    selection-background-color: #3a2a1a;
    selection-color: #f4bb78;
}
QSpinBox::up-button, QSpinBox::down-button {
    width: 14px;
    background-color: #2a2632;
    border-left: 1px solid #3a3440;
}
QCheckBox {
    color: #b8afc0;
    font-size: 11px;
    spacing: 6px;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
    background-color: #211e27;
    border: 1px solid #4f475a;
    border-radius: 4px;
}
QCheckBox::indicator:hover {
    border-color: #e8a05c;
}
QCheckBox::indicator:checked {
    background-color: #e8a05c;
    border-color: #e8a05c;
}
QSlider::groove:horizontal {
    height: 4px;
    background-color: #3a3440;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background-color: #e8a05c;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 12px;
    margin: -5px 0;
    background-color: #e8a05c;
    border: 1px solid #1a1512;
    border-radius: 6px;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #3a3440;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #4f475a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background-color: transparent;
}
QToolTip {
    background-color: #2a2632;
    color: #f2eee8;
    border: 1px solid #4f475a;
    border-radius: 4px;
    padding: 5px 7px;
    font-size: 11px;
}
QMenu {
    background-color: #211e27;
    border: 1px solid #3a3440;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    color: #f2eee8;
    padding: 6px 14px;
    border-radius: 6px;
}
QMenu::item:selected {
    background-color: #3a2a1a;
    color: #f4bb78;
}
QMenu::separator {
    height: 1px;
    background-color: #3a3440;
    margin: 4px 6px;
}
"""

HEX_RE = re.compile(r"^#?[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$")


def normalize_hex_input(value: str) -> str | None:
    """Devuelve un HEX normalizado o ``None`` si el texto no es válido."""
    text = (value or "").strip()
    if not HEX_RE.match(text):
        return None
    return model.normalize_hex(text)


def clear_layout(layout) -> None:
    """Vacía un layout borrando sus widgets hijo."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
            continue
        child = item.layout()
        if child is not None:
            clear_layout(child)
            child.deleteLater()


def make_small_button(text: str, object_name: str, tooltip: str = "") -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setProperty("small", "true")
    button.setFixedSize(22, 22)
    button.setCursor(Qt.PointingHandCursor)
    if tooltip:
        button.setToolTip(tooltip)
    return button


def make_badge(text: str, object_name: str, role: str | None = None) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setAlignment(Qt.AlignCenter)
    label.setSizePolicy(SizePolicy.Fixed, SizePolicy.Fixed)
    if role is not None:
        label.setProperty("role", role)
    return label


def add_form_label(grid: QGridLayout, row: int, text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("field_label")
    label.setMinimumWidth(64)
    label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    grid.addWidget(label, row, 0)
    return label


class ColorButton(QPushButton):
    """Muestra un color real y distingue clic izquierdo de clic derecho."""

    rightClicked = pyqtSignal()

    def __init__(self, hex_color: str = "#808080", size: int = 28, parent=None):
        super().__init__(parent)
        self._hex = model.normalize_hex(hex_color)
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(self._hex)
        self.setFocusPolicy(Qt.StrongFocus)
        self._apply_color()

    @property
    def hex_color(self) -> str:
        return self._hex

    def set_color(self, value: str) -> None:
        normalized = model.normalize_hex(value, self._hex)
        self._hex = normalized
        self._apply_color()

    def _apply_color(self) -> None:
        self.setStyleSheet(
            "QPushButton {"
            f" background-color: {self._hex};"
            " border: 1px solid #4f475a;"
            " border-radius: 6px;"
            " padding: 0;"
            " min-height: 0;"
            " }"
            "QPushButton:hover { border: 2px solid #e8a05c; }"
            "QPushButton:focus { border: 2px solid #e8a05c; }"
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.RightButton:
            self.rightClicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)


class ColorField(QWidget):
    """ColorButton + campo HEX sincronizados."""

    colorChanged = pyqtSignal(str)

    def __init__(self, hex_color: str = "#808080", parent=None):
        super().__init__(parent)
        self._last_valid = model.normalize_hex(hex_color)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.button = ColorButton(self._last_valid, 26)
        self.button.setToolTip(tr("Elegir color…"))
        self.button.clicked.connect(self._pick_color)
        self.edit = QLineEdit(self._last_valid)
        self.edit.setMaxLength(7)
        self.edit.setFixedWidth(82)
        self.edit.setToolTip("HEX, por ejemplo #c98d6b")
        self.edit.textEdited.connect(self._preview)
        self.edit.editingFinished.connect(self._commit)
        layout.addWidget(self.button)
        layout.addWidget(self.edit)
        layout.addStretch(1)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._last_valid), self, tr("Elegir color"))
        if color.isValid():
            self.set_value(color.name())
            self.colorChanged.emit(self._last_valid)

    def _preview(self, text: str) -> None:
        candidate = normalize_hex_input(text)
        if candidate:
            self.button.set_color(candidate)

    def _commit(self) -> None:
        candidate = normalize_hex_input(self.edit.text())
        if candidate:
            self.set_value(candidate)
            self.colorChanged.emit(candidate)
        else:
            self.set_value(self._last_valid)

    def set_value(self, value: str) -> None:
        normalized = model.normalize_hex(value, self._last_valid)
        self._last_valid = normalized
        self.edit.setText(normalized)
        self.button.set_color(normalized)

    def value(self) -> str:
        return normalize_hex_input(self.edit.text()) or self._last_valid


class GrimorioDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("grimorio_dialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setStyleSheet(STYLE_SHEET)
        self.setMinimumWidth(360)
        self.dialog_title = title

    def header(self) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        title = QLabel(self.dialog_title)
        title.setObjectName("dialog_title")
        row.addWidget(title, 1)
        close = QPushButton("✕")
        close.setObjectName("dialog_close")
        close.setToolTip(tr("Cerrar"))
        close.clicked.connect(self.reject)
        row.addWidget(close, 0)
        return box

    def button_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addStretch(1)
        cancel = QPushButton(tr("Cancelar"))
        cancel.setObjectName("dialog_cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton(tr("Guardar"))
        save.setObjectName("dialog_save")
        save.setDefault(True)
        save.clicked.connect(self.accept)
        row.addWidget(cancel)
        row.addWidget(save)
        return row


class SwatchDialog(GrimorioDialog):
    def __init__(
        self,
        parent=None,
        swatch: dict | None = None,
        environment: bool = False,
        default_body: str = "",
    ):
        title = tr("color de ambiente") if environment else tr("color")
        super().__init__((tr("Editar ") if swatch else tr("Añadir ")) + title, parent)
        self.environment = environment
        self.default_body = default_body
        source = swatch or {}

        hex_value = model.normalize_hex(source.get("hex", "#c98d6b"), "#c98d6b")
        self.name_edit = QLineEdit(str(source.get("name") or ""))
        self.name_edit.setPlaceholderText(tr("Piel base, Sombra de cuello…"))
        self.name_edit.setCursorPosition(0)

        self.hex_button = ColorButton(hex_value, 30)
        self.hex_button.setToolTip(tr("Elegir color…"))
        self.hex_button.clicked.connect(self._pick_color)
        self.hex_edit = QLineEdit(hex_value)
        self.hex_edit.setMaxLength(7)
        self.hex_edit.setFixedWidth(88)
        self.hex_edit.textEdited.connect(self._preview_hex)
        self.hex_edit.editingFinished.connect(self._commit_hex)
        hex_row = QWidget()
        hex_layout = QHBoxLayout(hex_row)
        hex_layout.setContentsMargins(0, 0, 0, 0)
        hex_layout.setSpacing(6)
        hex_layout.addWidget(self.hex_button)
        hex_layout.addWidget(self.hex_edit)
        hex_layout.addStretch(1)

        self.role_combo = QComboBox()
        for key, label in model.ROLES.items():
            self.role_combo.addItem(tr(label), key)
        role = str(source.get("role") or "base")
        index = self.role_combo.findData(role)
        self.role_combo.setCurrentIndex(index if index >= 0 else 0)

        self.body_combo = QComboBox()
        self.body_combo.setEditable(True)
        self.body_combo.addItems([tr(part) for part in model.BODY_PARTS])
        self.body_combo.setCurrentText(
            tr(str(source.get("bodyPart") or default_body or model.default_body_part("skin")))
        )

        self.purpose_edit = QLineEdit(str(source.get("purpose") or ""))
        self.purpose_edit.setPlaceholderText(tr("Para qué sirve este color"))
        self.purpose_edit.setCursorPosition(0)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(int(source.get("opacity", 100)))
        self.opacity_spin.setFixedWidth(58)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.opacity_spin.value())
        self.opacity_spin.valueChanged.connect(self.opacity_slider.setValue)
        self.opacity_slider.valueChanged.connect(self.opacity_spin.setValue)
        opacity_row = QWidget()
        opacity_layout = QHBoxLayout(opacity_row)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(8)
        opacity_layout.addWidget(self.opacity_spin)
        opacity_layout.addWidget(self.opacity_slider, 1)

        self.note_edit = QTextEdit()
        self.note_edit.setFixedHeight(58)
        self.note_edit.setPlaceholderText(tr("Nota libre: mezcla, referencia, cuidado al pintar…"))
        self.note_edit.setTabChangesFocus(True)
        self.note_edit.setPlainText(str(source.get("note") or ""))

        form = QFormLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.addRow(tr("Nombre"), self.name_edit)
        form.addRow(tr("HEX"), hex_row)
        form.addRow(tr("Rol"), self.role_combo)
        form.addRow(tr("Parte del cuerpo"), self.body_combo)
        form.addRow(tr("Para qué"), self.purpose_edit)
        form.addRow(tr("Opacidad"), opacity_row)
        form.addRow(tr("Nota"), self.note_edit)

        if environment:
            for widget in (self.role_combo, self.body_combo):
                label = form.labelForField(widget)
                if label is not None:
                    label.setVisible(False)
                widget.setVisible(False)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 12)
        outer.setSpacing(10)
        outer.addWidget(self.header())
        outer.addLayout(form)
        outer.addStretch(1)
        outer.addLayout(self.button_row())

        self.resize(380, 450 if environment else 510)
        self.name_edit.setFocus()

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.hex_button.hex_color), self, tr("Elegir color"))
        if color.isValid():
            self.hex_edit.setText(color.name())
            self.hex_button.set_color(color.name())

    def _preview_hex(self, text: str) -> None:
        candidate = normalize_hex_input(text)
        if candidate:
            self.hex_button.set_color(candidate)

    def _commit_hex(self) -> None:
        candidate = normalize_hex_input(self.hex_edit.text())
        if candidate:
            self.hex_edit.setText(candidate)
            self.hex_button.set_color(candidate)
        else:
            self.hex_edit.setText(self.hex_button.hex_color)

    def accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, tr("Falta el nombre"), tr("El color necesita un nombre."))
            self.name_edit.setFocus()
            return
        if normalize_hex_input(self.hex_edit.text()) is None:
            QMessageBox.warning(
                self,
                tr("HEX no válido"),
                tr("Escribe un color en formato #rrggbb (por ejemplo #c98d6b)."),
            )
            self.hex_edit.setFocus()
            return
        super().accept()

    def data(self) -> dict:
        data = {
            "name": self.name_edit.text().strip(),
            "hex": normalize_hex_input(self.hex_edit.text()) or self.hex_button.hex_color,
            "purpose": self.purpose_edit.text().strip(),
            "opacity": int(self.opacity_spin.value()),
            "note": self.note_edit.toPlainText().strip(),
        }
        if not self.environment:
            data["role"] = self.role_combo.currentData() or "base"
            data["bodyPart"] = self.body_combo.currentText().strip()
        return data


class CharacterDialog(GrimorioDialog):
    def __init__(self, parent=None, character: dict | None = None):
        super().__init__(tr("Editar OC") if character else tr("Nuevo OC"), parent)
        source = character or {}

        self.name_edit = QLineEdit(str(source.get("name") or ""))
        self.name_edit.setPlaceholderText(tr("Nombre del OC"))
        self.name_edit.setCursorPosition(0)
        self.tags_edit = QLineEdit(", ".join(source.get("tags") or []))
        self.tags_edit.setPlaceholderText(tr("fantasía, guerrera, guardia"))
        self.tags_edit.setCursorPosition(0)
        self.summary_edit = self._text_edit(str(source.get("summary") or ""), 64)
        self.history_edit = self._text_edit(str(source.get("history") or ""), 104)
        self.personality_edit = self._text_edit(str(source.get("personality") or ""), 70)
        self.relationships_edit = self._text_edit(str(source.get("relationships") or ""), 70)

        form = QFormLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(7)
        form.addRow(tr("Nombre"), self.name_edit)
        form.addRow(tr("Etiquetas"), self.tags_edit)
        form.addRow(tr("Resumen"), self.summary_edit)
        form.addRow(tr("Historia"), self.history_edit)
        form.addRow(tr("Personalidad"), self.personality_edit)
        form.addRow(tr("Relaciones"), self.relationships_edit)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 12)
        outer.setSpacing(10)
        outer.addWidget(self.header())
        outer.addLayout(form)
        outer.addStretch(1)
        outer.addLayout(self.button_row())

        self.resize(440, 580)
        self.name_edit.setFocus()

    @staticmethod
    def _text_edit(text: str, height: int) -> QTextEdit:
        widget = QTextEdit()
        widget.setFixedHeight(height)
        widget.setTabChangesFocus(True)
        widget.setPlainText(text)
        return widget

    def accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, tr("Falta el nombre"), tr("El OC necesita un nombre."))
            self.name_edit.setFocus()
            return
        super().accept()

    def data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "tags": model.as_str_list([part for part in self.tags_edit.text().split(",")]),
            "summary": self.summary_edit.toPlainText().strip(),
            "history": self.history_edit.toPlainText().strip(),
            "personality": self.personality_edit.toPlainText().strip(),
            "relationships": self.relationships_edit.toPlainText().strip(),
        }


class LayerDialog(GrimorioDialog):
    def __init__(self, parent=None, layer: dict | None = None):
        super().__init__(tr("Editar capa") if layer else tr("Añadir capa"), parent)
        source = layer or {}

        self.name_edit = QLineEdit(str(source.get("name") or ""))
        self.name_edit.setPlaceholderText(tr("SHADOW, LIGHT, FX…"))
        self.name_edit.setCursorPosition(0)

        self.blend_combo = QComboBox()
        for key, label in model.BLENDS.items():
            self.blend_combo.addItem(tr(label), key)
        blend = str(source.get("blend") or "normal")
        index = self.blend_combo.findData(blend)
        self.blend_combo.setCurrentIndex(index if index >= 0 else 0)

        self.opacity_spin = QSpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setValue(int(source.get("opacity", 100)))
        self.opacity_spin.setFixedWidth(58)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.opacity_spin.value())
        self.opacity_spin.valueChanged.connect(self.opacity_slider.setValue)
        self.opacity_slider.valueChanged.connect(self.opacity_spin.setValue)
        opacity_row = QWidget()
        opacity_layout = QHBoxLayout(opacity_row)
        opacity_layout.setContentsMargins(0, 0, 0, 0)
        opacity_layout.setSpacing(8)
        opacity_layout.addWidget(self.opacity_spin)
        opacity_layout.addWidget(self.opacity_slider, 1)

        self.purpose_edit = QLineEdit(str(source.get("purpose") or ""))
        self.purpose_edit.setPlaceholderText(tr("Propósito de la capa"))
        self.purpose_edit.setCursorPosition(0)

        form = QFormLayout()
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.addRow(tr("Nombre"), self.name_edit)
        form.addRow(tr("Blend mode"), self.blend_combo)
        form.addRow(tr("Opacidad"), opacity_row)
        form.addRow(tr("Propósito"), self.purpose_edit)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 14, 14, 12)
        outer.setSpacing(10)
        outer.addWidget(self.header())
        outer.addLayout(form)
        outer.addStretch(1)
        outer.addLayout(self.button_row())

        self.resize(380, 340)
        self.name_edit.setFocus()

    def accept(self) -> None:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, tr("Falta el nombre"), tr("La capa necesita un nombre."))
            self.name_edit.setFocus()
            return
        super().accept()

    def data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "blend": self.blend_combo.currentData() or "normal",
            "opacity": int(self.opacity_spin.value()),
            "purpose": self.purpose_edit.text().strip(),
        }


class GrimorioPanel(QWidget):
    """Panel principal del docker."""

    def __init__(self, bridge=None, parent=None):
        super().__init__(parent)
        self.setObjectName("grimorio_panel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLE_SHEET)
        self.setMinimumWidth(340)
        self.resize(400, 900)
        self.setSizePolicy(SizePolicy.Expanding, SizePolicy.Expanding)

        self.settings = QSettings("GrimorioColor", "Docker")
        self._translations_dir = model.DATA_FILE.parent / "translations"
        self._bundled_translations = Path(__file__).resolve().parent / "translations"
        try:
            i18n.ensure_translations_dir(self._translations_dir)
            i18n.load_translations(
                self._translations_dir,
                extra_directories=[self._bundled_translations],
            )
        except OSError:
            pass
        supported = {code for code, _ in i18n.available_languages()}
        env_lang = os.environ.get("GRIMORIO_LANG", "").strip().lower()
        env_prefix = env_lang.split("_")[0].split("-")[0]
        if env_lang in supported:
            self._language = env_lang
        elif env_prefix in supported:
            self._language = env_prefix
        else:
            saved = str(self.settings.value("language", "") or "").strip().lower()
            if saved in supported:
                self._language = saved
            else:
                self._language = i18n.detect_language()
        i18n.set_language(self._language)
        self._language = i18n.get_language()

        self.bridge = bridge if bridge is not None else KritaBridge()
        self.state = model.load_state()
        self._loading = False
        self._shown_character_id = None
        self._last_saved_text = self._read_disk_text()

        self._build_ui()

        self._guard_timer = QTimer(self)
        self._guard_timer.setInterval(300)
        self._guard_timer.timeout.connect(self._check_color_guard)
        self._guard_target = None

        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._arm_watcher()

        self.refresh()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 10)
        layout.setSpacing(8)

        layout.addWidget(self._build_header())

        rule = QFrame()
        rule.setObjectName("header_rule")
        rule.setFixedHeight(1)
        layout.addWidget(rule)

        layout.addWidget(self._build_character_row())
        layout.addWidget(self._build_key_strip())

        self.tabs = QTabWidget()
        self.tabs.setObjectName("tabs")
        self.sheet_scroll, self.sheet_body = self._make_scroll_tab()
        self.palettes_scroll, self.palettes_body = self._make_scroll_tab()
        self.layers_scroll, self.layers_body = self._make_scroll_tab()
        self.environment_scroll, self.environment_body = self._make_scroll_tab()
        self.tabs.addTab(self.sheet_scroll, tr("Ficha"))
        self.tabs.addTab(self.palettes_scroll, tr("Paletas"))
        self.tabs.addTab(self.layers_scroll, tr("Capas"))
        self.tabs.addTab(self.environment_scroll, tr("Ambiente"))
        layout.addWidget(self.tabs, 1)

        layout.addWidget(self._build_footer())

    def _build_header(self) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        titles = QVBoxLayout()
        titles.setContentsMargins(0, 0, 0, 0)
        titles.setSpacing(1)
        title = QLabel(tr("Grimorio de Color"))
        title.setObjectName("title")
        subtitle = QLabel(tr("Paletas y recetas de tus OCs"))
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        row.addLayout(titles, 1)

        menu_button = QToolButton()
        menu_button.setObjectName("menu_button")
        menu_button.setText("⋯")
        menu_button.setToolTip(tr("Menú"))
        menu_button.setFixedSize(28, 28)
        menu_button.setCursor(Qt.PointingHandCursor)
        menu_button.setPopupMode(ToolButtonPopupMode.InstantPopup)

        menu = QMenu(menu_button)
        self.action_import = QAction(tr("Importar JSON…"), menu)
        self.action_export = QAction(tr("Exportar JSON…"), menu)
        self.action_export_gpl = QAction(tr("Exportar .gpl…"), menu)
        self.action_open_folder = QAction(tr("Abrir carpeta de datos"), menu)
        self.action_reload = QAction(tr("Recargar desde disco"), menu)
        self.action_import.triggered.connect(self.import_json)
        self.action_export.triggered.connect(self.export_json)
        self.action_export_gpl.triggered.connect(self.export_gpl)
        self.action_open_folder.triggered.connect(self.open_data_folder)
        self.action_reload.triggered.connect(self.reload_from_disk)
        menu.addAction(self.action_import)
        menu.addAction(self.action_export)
        menu.addAction(self.action_export_gpl)
        menu.addSeparator()
        menu.addAction(self.action_open_folder)
        menu.addAction(self.action_reload)
        menu.addSeparator()
        self.action_web = QAction(tr("Abrir Grimorio web"), menu)
        self.action_set_web = QAction(tr("Configurar web del Grimorio…"), menu)
        self.action_web.triggered.connect(self.open_web_app)
        self.action_set_web.triggered.connect(self.configure_web_app)
        menu.addAction(self.action_web)
        menu.addAction(self.action_set_web)
        menu.addSeparator()
        language_menu = menu.addMenu(tr("Idioma"))
        self.language_actions = {}
        for code, name in i18n.available_languages():
            action = QAction(name, language_menu)
            action.setCheckable(True)
            action.setChecked(self._language == code)
            action.triggered.connect(lambda checked=False, code=code: self.set_language(code))
            language_menu.addAction(action)
            self.language_actions[code] = action
            if code == "es":
                self.action_lang_es = action
            if code == "en":
                self.action_lang_en = action
        language_menu.addSeparator()
        self.action_translation_template = QAction(
            tr("Crear plantilla de traducción"), language_menu
        )
        self.action_open_translations = QAction(
            tr("Abrir carpeta de traducciones"), language_menu
        )
        self.action_reload_translations = QAction(
            tr("Recargar traducciones"), language_menu
        )
        self.action_translation_template.triggered.connect(self.create_translation_template)
        self.action_open_translations.triggered.connect(self.open_translations_folder)
        self.action_reload_translations.triggered.connect(self.reload_translations)
        language_menu.addAction(self.action_translation_template)
        language_menu.addAction(self.action_open_translations)
        language_menu.addAction(self.action_reload_translations)
        menu_button.setMenu(menu)

        self.web_button = QToolButton()
        self.web_button.setObjectName("web_button")
        self.web_button.setText("web")
        self.web_button.setToolTip(
            tr("Abrir Grimorio web")
            + "\n"
            + tr("El web Grimorio usa su propio almacenamiento; usa Exportar/Importar JSON para pasar los datos.")
        )
        self.web_button.setFixedSize(28, 28)
        self.web_button.setCursor(Qt.PointingHandCursor)
        self.web_button.clicked.connect(self.open_web_app)

        row.addWidget(self.web_button, 0, Qt.AlignTop)
        row.addWidget(menu_button, 0, Qt.AlignTop)
        return box

    def _build_character_row(self) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(4)

        label = QLabel(tr("OC"))
        label.setObjectName("field_label")
        row.addWidget(label)

        self.character_combo = QComboBox()
        self.character_combo.setObjectName("character_combo")
        self.character_combo.setMinimumWidth(80)
        self.character_combo.setSizePolicy(SizePolicy.Expanding, SizePolicy.Fixed)
        self.character_combo.currentIndexChanged.connect(self._on_character_changed)
        row.addWidget(self.character_combo, 1)

        self.btn_new_character = QPushButton("+")
        self.btn_new_character.setObjectName("btn_new_character")
        self.btn_new_character.setProperty("small", "true")
        self.btn_new_character.setFixedSize(26, 26)
        self.btn_new_character.setToolTip(tr("Nuevo OC"))
        self.btn_new_character.setCursor(Qt.PointingHandCursor)
        self.btn_new_character.clicked.connect(self.new_character)
        row.addWidget(self.btn_new_character)

        self.btn_edit_character = QPushButton(tr("Editar"))
        self.btn_edit_character.setObjectName("btn_edit_character")
        self.btn_edit_character.setProperty("small", "true")
        self.btn_edit_character.setFixedHeight(26)
        self.btn_edit_character.setToolTip(tr("Editar la ficha del OC"))
        self.btn_edit_character.clicked.connect(self.edit_character)
        row.addWidget(self.btn_edit_character)

        self.btn_delete_character = QPushButton(tr("Eliminar"))
        self.btn_delete_character.setObjectName("btn_delete_character")
        self.btn_delete_character.setProperty("small", "true")
        self.btn_delete_character.setProperty("danger", "true")
        self.btn_delete_character.setFixedHeight(26)
        self.btn_delete_character.setToolTip(tr("Eliminar el OC"))
        self.btn_delete_character.clicked.connect(self.delete_character)
        row.addWidget(self.btn_delete_character)

        return box

    def _build_key_strip(self) -> QWidget:
        box = QWidget()
        row = QHBoxLayout(box)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        label = QLabel(tr("Clave"))
        label.setObjectName("field_label")
        row.addWidget(label)

        self.key_buttons: list[ColorButton] = []
        for index in range(3):
            button = ColorButton("#3a3440", 28)
            button.setObjectName(f"key_color_{index}")
            button.clicked.connect(
                lambda checked=False, i=index: self._apply_key_color(i, background=False)
            )
            button.rightClicked.connect(
                lambda i=index: self._apply_key_color(i, background=True)
            )
            self.key_buttons.append(button)
            row.addWidget(button)

        row.addStretch(1)
        self.key_count_label = QLabel("")
        self.key_count_label.setObjectName("hint")
        row.addWidget(self.key_count_label)
        return box

    def _build_footer(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.setContentsMargins(0, 2, 0, 0)
        layout.setSpacing(4)

        hint = QLabel(tr("Clic = primer plano · clic derecho = fondo"))
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        guard_row = QHBoxLayout()
        guard_row.setContentsMargins(0, 0, 0, 0)
        guard_row.setSpacing(6)
        self.color_guard = QCheckBox("Color Guard")
        self.color_guard.setObjectName("color_guard")
        self.color_guard.setToolTip(
            tr("Marca para comparar el color actual con la paleta.")
        )
        self.color_guard.toggled.connect(self._set_guard_enabled)
        guard_row.addWidget(self.color_guard)
        self.guard_status = QLabel("")
        self.guard_status.setObjectName("guard_status")
        self.guard_status.setWordWrap(True)
        guard_row.addWidget(self.guard_status, 1)
        self.guard_snap = QPushButton(tr("Snap"))
        self.guard_snap.setObjectName("btn_guard_snap")
        self.guard_snap.setProperty("small", "true")
        self.guard_snap.setFixedHeight(22)
        self.guard_snap.hide()
        self.guard_snap.clicked.connect(self._snap_guard_color)
        guard_row.addWidget(self.guard_snap)
        layout.addLayout(guard_row)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        self.apply_opacity = QCheckBox(tr("Aplicar opacidad del color"))
        self.apply_opacity.setObjectName("apply_opacity")
        self.apply_opacity.setChecked(False)
        self.apply_opacity.setToolTip(
            tr("Si está marcado, el color se aplica con el alfa del swatch.")
        )
        row.addWidget(self.apply_opacity)
        row.addStretch(1)
        self.status = QLabel(tr("Guardado"))
        self.status.setObjectName("status")
        self.status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(self.status)
        layout.addLayout(row)
        return box

    def _make_scroll_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(FrameShape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body = QWidget()
        body.setObjectName("scroll_body")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(body)
        return scroll, layout

    # ------------------------------------------------------------- refresh
    def refresh(self) -> None:
        tab_index = self.tabs.currentIndex()
        same_character = self.state.get("activeCharacterId") == self._shown_character_id
        scrolls = (
            self.sheet_scroll,
            self.palettes_scroll,
            self.layers_scroll,
            self.environment_scroll,
        )
        positions = [
            scroll.verticalScrollBar().value() if same_character else 0 for scroll in scrolls
        ]

        self._loading = True
        try:
            self._fill_character_combo()
            character = self._character()
            self._fill_key_strip(character)
            self._fill_sheet(character)
            self._fill_palettes(character)
            self._fill_layers(character)
            self._fill_environment(character)

            has_character = character is not None
            self.btn_edit_character.setEnabled(has_character)
            self.btn_delete_character.setEnabled(has_character)
            self.action_export_gpl.setEnabled(has_character)
            self.tabs.setCurrentIndex(tab_index)
        finally:
            self._loading = False

        self._shown_character_id = self.state.get("activeCharacterId")
        QTimer.singleShot(0, lambda: self._restore_scroll(scrolls, positions))

    def _restore_scroll(self, scrolls, positions) -> None:
        for scroll, value in zip(scrolls, positions):
            scroll.verticalScrollBar().setValue(value)

    def _character(self) -> dict | None:
        return model.active_character(self.state)

    def _fill_character_combo(self) -> None:
        self.character_combo.blockSignals(True)
        self.character_combo.clear()
        for character in self.state.get("characters", []):
            self.character_combo.addItem(
                str(character.get("name") or tr("Sin nombre")), character.get("id")
            )
        active = self.state.get("activeCharacterId")
        index = self.character_combo.findData(active) if active else -1
        if index < 0 and self.character_combo.count():
            index = 0
        self.character_combo.setCurrentIndex(index)
        self.character_combo.setEnabled(self.character_combo.count() > 0)
        self.character_combo.blockSignals(False)

    def _fill_key_strip(self, character: dict | None) -> None:
        colors = model.key_colors(character) if character else ["#3a3440"] * 3
        labels = (tr("Piel"), tr("Pelo"), tr("Ojos"))
        for button, label, color in zip(self.key_buttons, labels, colors):
            button.set_color(color)
            button.setEnabled(character is not None)
            button.setToolTip(
                f"{label} · {color}\n{tr('Clic: primer plano · clic derecho: fondo')}"
            )
        if character:
            self.key_count_label.setText(f"{model.count_colors(character)}{tr(' colores')}")
        else:
            self.key_count_label.setText("")
        self.key_count_label.setVisible(character is not None)

    def _fill_sheet(self, character: dict | None) -> None:
        clear_layout(self.sheet_body)
        if character is None:
            self._add_placeholder(
                self.sheet_body,
                tr("Todavía no hay OCs. Crea uno con el botón + de la cabecera."),
            )
            self.sheet_body.addStretch(1)
            return

        top = QFrame()
        top.setObjectName("oc_hero")
        hero = QHBoxLayout(top)
        hero.setContentsMargins(10, 9, 10, 9)
        hero.setSpacing(10)

        photo_path = model.resolve_image(str(character.get("referenceImage") or ""))
        photo = QLabel()
        photo.setObjectName("oc_photo")
        photo.setFixedSize(132, 172)
        photo.setAlignment(Qt.AlignCenter)
        if photo_path is not None:
            pixmap = QPixmap(str(photo_path))
            if not pixmap.isNull():
                photo.setPixmap(
                    pixmap.scaled(
                        132, 172, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                )
        current_pixmap = photo.pixmap()
        if current_pixmap is None or current_pixmap.isNull():
            photo.setText(tr("Sin foto"))
            photo.setProperty("empty", "true")
        hero.addWidget(photo, 0, Qt.AlignTop)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(5)

        name = QLabel(str(character.get("name") or tr("Sin nombre")))
        name.setObjectName("character_name")
        name.setWordWrap(True)
        name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        info.addWidget(name)

        tags = character.get("tags") or []
        if tags:
            tag_label = QLabel(self._tags_html(tags))
            tag_label.setObjectName("tag_line")
            tag_label.setTextFormat(Qt.RichText)
            tag_label.setWordWrap(True)
            info.addWidget(tag_label)

        stats = QLabel(
            f"{model.count_colors(character)}{tr(' colores · ')}"
            f"{len(character.get('recipe', []))}{tr(' capas en la receta')}"
        )
        stats.setObjectName("hint")
        stats.setWordWrap(True)
        info.addWidget(stats)

        edit = QPushButton(tr("Editar ficha"))
        edit.setObjectName("btn_edit_character_details")
        edit.setProperty("small", "true")
        edit.setFixedHeight(24)
        edit.clicked.connect(self.edit_character)
        info.addWidget(edit, 0, Qt.AlignLeft)

        photo_row = QHBoxLayout()
        photo_row.setContentsMargins(0, 0, 0, 0)
        photo_row.setSpacing(4)
        set_photo = QPushButton(tr("Cambiar foto") if photo_path else tr("Añadir foto"))
        set_photo.setObjectName("btn_set_photo")
        set_photo.setProperty("small", "true")
        set_photo.setProperty("accent", "true")
        set_photo.setFixedHeight(22)
        set_photo.clicked.connect(self.set_reference_image)
        photo_row.addWidget(set_photo)
        if photo_path is not None:
            remove_photo = QPushButton(tr("Quitar foto"))
            remove_photo.setObjectName("btn_remove_photo")
            remove_photo.setProperty("small", "true")
            remove_photo.setProperty("danger", "true")
            remove_photo.setFixedHeight(22)
            remove_photo.clicked.connect(self.remove_reference_image)
            photo_row.addWidget(remove_photo)
            open_photo = QPushButton(tr("Abrir foto"))
            open_photo.setObjectName("btn_open_photo")
            open_photo.setProperty("small", "true")
            open_photo.setFixedHeight(22)
            open_photo.clicked.connect(self.open_reference_image)
            photo_row.addWidget(open_photo)
        photo_row.addStretch(1)
        info.addLayout(photo_row)

        hero.addLayout(info, 1)
        self.sheet_body.addWidget(top)

        cards = (
            (tr("RESUMEN"), "summary"),
            (tr("HISTORIA"), "history"),
            (tr("PERSONALIDAD"), "personality"),
            (tr("RELACIONES"), "relationships"),
        )
        for title, key in cards:
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 9)
            card_layout.setSpacing(4)
            heading = QLabel(title)
            heading.setObjectName("card_title")
            card_layout.addWidget(heading)
            value = str(character.get(key) or "").strip()
            body = QLabel(value or "—")
            body.setObjectName("card_body")
            body.setWordWrap(True)
            body.setTextInteractionFlags(Qt.TextSelectableByMouse)
            card_layout.addWidget(body)
            self.sheet_body.addWidget(card)

        self.sheet_body.addStretch(1)

    @staticmethod
    def _tags_html(tags: list[str]) -> str:
        parts = [
            f'<span style="color:#f4bb78;">#{html.escape(str(tag))}</span>'
            for tag in tags
        ]
        return '<span style="color:#b8afc0;"> · </span>'.join(parts)

    def _fill_palettes(self, character: dict | None) -> None:
        clear_layout(self.palettes_body)
        if character is None:
            self._add_placeholder(
                self.palettes_body,
                tr("Crea un OC para empezar a guardar sus paletas por zona."),
            )
            self.palettes_body.addStretch(1)
            return

        private_mode = bool(self.state.get("privateMode", True))
        for zone in model.ZONES:
            zone_key = zone["key"]
            items = character.get("palettes", {}).get(zone_key, [])
            block = QFrame()
            block.setObjectName("zone_block")
            block_layout = QVBoxLayout(block)
            block_layout.setContentsMargins(9, 8, 9, 9)
            block_layout.setSpacing(6)

            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(6)
            title = QLabel(f"{tr(zone['label'])} ({len(items)})")
            title.setObjectName(f"zone_title_{zone_key}")
            title.setToolTip(tr(str(zone.get("default_body", ""))))
            header.addWidget(title, 1)

            add_button = QPushButton(tr("Añadir"))
            add_button.setObjectName(f"btn_add_swatch_{zone_key}")
            add_button.setProperty("small", "true")
            add_button.setProperty("accent", "true")
            add_button.setFixedHeight(22)
            add_button.clicked.connect(
                lambda checked=False, z=zone_key: self.add_swatch(z)
            )
            example_button = QPushButton("▣")
            example_button.setObjectName(f"btn_example_{zone_key}")
            example_button.setProperty("small", "true")
            example_button.setProperty("accent", "true")
            example_button.setToolTip(tr("Ejemplo de la zona"))
            example_button.setFixedSize(22, 22)
            example_button.clicked.connect(
                lambda checked=False, z=zone_key: self.set_zone_example(z)
            )
            if zone_key == "intimate":
                toggle = QCheckBox(tr("Mostrar privado"))
                toggle.setObjectName("private_toggle")
                toggle.setChecked(not private_mode)
                toggle.toggled.connect(self._set_private_visible)
                header.addWidget(toggle)
            header.addWidget(example_button)
            header.addWidget(add_button)
            block_layout.addLayout(header)

            hidden = zone_key == "intimate" and private_mode
            if hidden:
                add_button.setVisible(False)
                example_button.setVisible(False)
                note = QLabel(tr("Oculto por privacidad. Activa «Mostrar privado»."))
                note.setObjectName("private_hidden")
                note.setWordWrap(True)
                block_layout.addWidget(note)
            else:
                ramp = self._zone_ramp(items)
                if ramp:
                    ramp_label = QLabel()
                    ramp_label.setObjectName("zone_ramp")
                    ramp_label.setFixedHeight(10)
                    ramp_label.setScaledContents(True)
                    ramp_image = QPixmap(320, 10)
                    painter = QPainter(ramp_image)
                    gradient = QLinearGradient(0, 0, 320, 0)
                    gradient.setColorAt(0.0, QColor(ramp[0]))
                    gradient.setColorAt(0.5, QColor(ramp[1]))
                    gradient.setColorAt(1.0, QColor(ramp[2]))
                    painter.fillRect(ramp_image.rect(), QBrush(gradient))
                    painter.end()
                    ramp_label.setPixmap(ramp_image)
                    ramp_label.setToolTip(
                        tr("Sombra · Base · Luz")
                        + f": {ramp[0]} / {ramp[1]} / {ramp[2]}"
                    )
                    block_layout.addWidget(ramp_label)

                example_ref = str(
                    (character.get("zoneExamples") or {}).get(zone_key) or ""
                )
                example_path = model.resolve_image(example_ref)
                if example_path is not None:
                    example_frame = QFrame()
                    example_frame.setObjectName("zone_example")
                    example_layout = QHBoxLayout(example_frame)
                    example_layout.setContentsMargins(6, 6, 6, 6)
                    example_layout.setSpacing(6)
                    example_photo = QLabel()
                    example_photo.setObjectName("zone_example_photo")
                    example_photo.setFixedSize(104, 72)
                    example_photo.setAlignment(Qt.AlignCenter)
                    example_pixmap = QPixmap(str(example_path))
                    if not example_pixmap.isNull():
                        example_photo.setPixmap(
                            example_pixmap.scaled(
                                104,
                                72,
                                Qt.KeepAspectRatio,
                                Qt.SmoothTransformation,
                            )
                        )
                    else:
                        example_photo.setText(tr("Sin foto"))
                    example_layout.addWidget(example_photo)
                    example_label = QLabel(tr("Imagen de ejemplo"))
                    example_label.setObjectName("hint")
                    example_label.setWordWrap(True)
                    example_layout.addWidget(example_label, 1)
                    example_remove = QPushButton(tr("Quitar ejemplo"))
                    example_remove.setObjectName(f"btn_remove_example_{zone_key}")
                    example_remove.setProperty("small", "true")
                    example_remove.setProperty("danger", "true")
                    example_remove.setFixedHeight(22)
                    example_remove.clicked.connect(
                        lambda checked=False, z=zone_key: self.remove_zone_example(z)
                    )
                    example_layout.addWidget(example_remove)
                    block_layout.addWidget(example_frame)

                if not items:
                    empty = QLabel(tr("Sin colores todavía."))
                    empty.setObjectName("empty_note")
                    block_layout.addWidget(empty)
                for swatch in items:
                    block_layout.addWidget(self._swatch_card(zone_key, swatch))

            self.palettes_body.addWidget(block)

        self.palettes_body.addStretch(1)

    @staticmethod
    def _zone_ramp(items: list[dict]) -> list[str] | None:
        if not items:
            return None
        by_role = {
            str(swatch.get("role") or ""): str(swatch.get("hex") or "")
            for swatch in items
        }
        base = by_role.get("base") or str(items[0].get("hex") or "")
        shadow = by_role.get("shadow") or (
            str(items[1].get("hex") or "") if len(items) > 1 else base
        )
        light = by_role.get("light") or (
            str(items[2].get("hex") or "") if len(items) > 2 else base
        )
        base = model.normalize_hex(base, "")
        if not base:
            return None
        shadow = model.normalize_hex(shadow, base)
        light = model.normalize_hex(light, base)
        return [shadow, base, light]

    def _swatch_card(self, zone_key: str, swatch: dict) -> QFrame:
        card = QFrame()
        card.setObjectName("swatch_card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        swatch_id = str(swatch.get("id") or "")
        hex_value = str(swatch.get("hex") or "#808080")
        opacity = int(swatch.get("opacity", 100))
        color_button = ColorButton(hex_value, 44)
        color_button.setObjectName(f"swatch_color_{swatch_id}")
        color_button.setToolTip(
            f"{hex_value}\n{tr('Clic: primer plano · clic derecho: fondo')}"
        )
        color_button.clicked.connect(
            lambda checked=False, s=swatch: self.apply_color(
                s.get("hex", "#808080"), s.get("opacity", 100), background=False
            )
        )
        color_button.rightClicked.connect(
            lambda s=swatch: self.apply_color(
                s.get("hex", "#808080"), s.get("opacity", 100), background=True
            )
        )
        layout.addWidget(color_button, 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(3)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(4)
        name = QLabel(str(swatch.get("name") or tr("Sin nombre")))
        name.setObjectName("swatch_name")
        name.setWordWrap(True)
        top.addWidget(name, 1)
        if zone_key != "environment":
            role = str(swatch.get("role") or "base")
            role_badge = make_badge(
                tr(str(model.ROLES.get(role, role))).upper(), "role_badge", role=role
            )
            top.addWidget(role_badge, 0, Qt.AlignTop)
        opacity_badge = make_badge(f"{opacity}%", "opacity_badge")
        top.addWidget(opacity_badge, 0, Qt.AlignTop)
        content.addLayout(top)

        meta_parts = [
            str(swatch.get("bodyPart") or "").strip(),
            str(swatch.get("purpose") or "").strip(),
        ]
        meta_text = " · ".join(part for part in meta_parts if part) or tr("Sin detalles")
        meta = QLabel(meta_text)
        meta.setObjectName("swatch_meta")
        meta.setWordWrap(True)
        content.addWidget(meta)

        bottom = QHBoxLayout()
        bottom.setContentsMargins(0, 0, 0, 0)
        bottom.setSpacing(4)
        hex_label = QLabel(hex_value)
        hex_label.setObjectName("swatch_hex")
        bottom.addWidget(hex_label)
        bottom.addStretch(1)

        edit = make_small_button(
            "✎", f"btn_edit_swatch_{swatch_id}", tr("Editar color")
        )
        edit.clicked.connect(
            lambda checked=False, z=zone_key, s=swatch: self.edit_swatch(z, s)
        )
        bottom.addWidget(edit)
        delete = make_small_button(
            "✕", f"btn_delete_swatch_{swatch_id}", tr("Eliminar color")
        )
        delete.setProperty("danger", "true")
        delete.clicked.connect(
            lambda checked=False, z=zone_key, s=swatch: self.delete_swatch(z, s)
        )
        bottom.addWidget(delete)
        content.addLayout(bottom)

        note = str(swatch.get("note") or "").strip()
        purpose = str(swatch.get("purpose") or "").strip()
        if note and note != purpose:
            note_label = QLabel(note)
            note_label.setObjectName("swatch_note")
            note_label.setWordWrap(True)
            content.addWidget(note_label)

        layout.addLayout(content, 1)
        return card

    def _fill_layers(self, character: dict | None) -> None:
        clear_layout(self.layers_body)
        if character is None:
            self._add_placeholder(
                self.layers_body,
                tr("Crea un OC para definir su receta de capas."),
            )
            self.layers_body.addStretch(1)
            return

        recipe = character.get("recipe", [])
        heading = QLabel(f"{tr('RECETA DE CAPAS (')}{len(recipe)})")
        heading.setObjectName("card_title")
        self.layers_body.addWidget(heading)

        first_row = QHBoxLayout()
        first_row.setContentsMargins(0, 0, 0, 0)
        first_row.setSpacing(6)
        add_layer_button = QPushButton(tr("Añadir capa"))
        add_layer_button.setObjectName("btn_add_layer")
        add_layer_button.setProperty("small", "true")
        add_layer_button.setProperty("accent", "true")
        add_layer_button.setFixedHeight(24)
        add_layer_button.clicked.connect(self.add_layer)
        reset_button = QPushButton(tr("Restaurar base"))
        reset_button.setObjectName("btn_reset_recipe")
        reset_button.setProperty("small", "true")
        reset_button.setFixedHeight(24)
        reset_button.clicked.connect(self.reset_recipe)
        first_row.addWidget(add_layer_button)
        first_row.addWidget(reset_button)
        first_row.addStretch(1)
        self.layers_body.addLayout(first_row)

        create_button = QPushButton(tr("Crear capas en Krita"))
        create_button.setObjectName("btn_create_layers")
        create_button.setFixedHeight(28)
        create_button.clicked.connect(self.create_layers)
        self.layers_body.addWidget(create_button)

        note = QLabel(tr("Arriba = encima en Krita. Los blend modes se aplican al crear."))
        note.setObjectName("hint")
        note.setWordWrap(True)
        self.layers_body.addWidget(note)

        if not recipe:
            empty = QLabel(tr("Sin capas. Añade una o restaura la receta base."))
            empty.setObjectName("empty_note")
            empty.setWordWrap(True)
            self.layers_body.addWidget(empty)

        last = len(recipe) - 1
        for index, layer in enumerate(recipe):
            layer_id = str(layer.get("id") or "")
            row_frame = QFrame()
            row_frame.setObjectName("layer_row")
            row_layout = QHBoxLayout(row_frame)
            row_layout.setContentsMargins(8, 7, 8, 7)
            row_layout.setSpacing(6)

            number = QLabel(f"{index + 1}")
            number.setObjectName("layer_index")
            number.setFixedWidth(16)
            number.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            row_layout.addWidget(number)

            content = QVBoxLayout()
            content.setContentsMargins(0, 0, 0, 0)
            content.setSpacing(2)
            top = QHBoxLayout()
            top.setContentsMargins(0, 0, 0, 0)
            top.setSpacing(4)
            name = QLabel(str(layer.get("name") or tr("Capa")))
            name.setObjectName("layer_name")
            name.setWordWrap(True)
            top.addWidget(name, 1)
            blend = str(layer.get("blend") or "normal")
            blend_badge = make_badge(
                tr(str(model.BLENDS.get(blend, blend))), "blend_badge"
            )
            top.addWidget(blend_badge, 0, Qt.AlignTop)
            opacity = QLabel(f"{int(layer.get('opacity', 100))}%")
            opacity.setObjectName("layer_opacity")
            opacity.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            top.addWidget(opacity, 0, Qt.AlignTop)
            content.addLayout(top)

            purpose = QLabel(tr(str(layer.get("purpose") or "").strip()) or "—")
            purpose.setObjectName("layer_purpose")
            purpose.setWordWrap(True)
            content.addWidget(purpose)
            row_layout.addLayout(content, 1)

            buttons = QGridLayout()
            buttons.setContentsMargins(0, 0, 0, 0)
            buttons.setHorizontalSpacing(3)
            buttons.setVerticalSpacing(3)
            up = make_small_button("↑", f"btn_layer_up_{layer_id}", tr("Subir capa"))
            up.setEnabled(index > 0)
            up.clicked.connect(
                lambda checked=False, lid=layer_id: self.move_layer(lid, "up")
            )
            down = make_small_button(
                "↓", f"btn_layer_down_{layer_id}", tr("Bajar capa")
            )
            down.setEnabled(index < last)
            down.clicked.connect(
                lambda checked=False, lid=layer_id: self.move_layer(lid, "down")
            )
            edit = make_small_button(
                "✎", f"btn_layer_edit_{layer_id}", tr("Editar capa")
            )
            edit.clicked.connect(
                lambda checked=False, l=layer: self.edit_layer(l)
            )
            delete = make_small_button(
                "✕", f"btn_layer_delete_{layer_id}", tr("Eliminar capa")
            )
            delete.setProperty("danger", "true")
            delete.clicked.connect(
                lambda checked=False, l=layer: self.delete_layer(l)
            )
            buttons.addWidget(up, 0, 0)
            buttons.addWidget(down, 0, 1)
            buttons.addWidget(edit, 1, 0)
            buttons.addWidget(delete, 1, 1)
            row_layout.addLayout(buttons)
            self.layers_body.addWidget(row_frame)

        self.layers_body.addStretch(1)

    def _fill_environment(self, character: dict | None) -> None:
        clear_layout(self.environment_body)
        if character is None:
            self._add_placeholder(
                self.environment_body,
                tr("Crea un OC para describir la luz y la paleta de su ambiente."),
            )
            self.environment_body.addStretch(1)
            return

        environment = character.get("environment") or model.default_environment()
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 9, 10, 10)
        card_layout.setSpacing(8)

        title = QLabel(tr("AMBIENTE"))
        title.setObjectName("card_title")
        card_layout.addWidget(title)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        grid.setColumnStretch(1, 1)

        self.env_name = QLineEdit(str(environment.get("name") or ""))
        self.env_name.setPlaceholderText(tr("Bosque de ceniza al atardecer"))
        self.env_time = QLineEdit(str(environment.get("time") or ""))
        self.env_time.setPlaceholderText(tr("Atardecer, noche, amanecer…"))
        self.env_weather = QLineEdit(str(environment.get("weather") or ""))
        self.env_weather.setPlaceholderText(tr("Neblina, lluvia, despejado…"))
        self.env_mood = QLineEdit(str(environment.get("mood") or ""))
        self.env_mood.setPlaceholderText(tr("Cálido, húmedo, contraluz…"))
        self.env_key = ColorField(str(environment.get("keyLight") or "#ffb36b"))
        self.env_shadow = ColorField(str(environment.get("shadowTint") or "#3a2a4d"))
        self.env_bounce = ColorField(str(environment.get("bounce") or "#7a4a2a"))

        for widget in (self.env_name, self.env_time, self.env_weather, self.env_mood):
            widget.setCursorPosition(0)

        rows = (
            (tr("Nombre"), self.env_name),
            (tr("Hora"), self.env_time),
            (tr("Clima"), self.env_weather),
            (tr("Mood"), self.env_mood),
            (tr("Luz clave"), self.env_key),
            (tr("Sombra"), self.env_shadow),
            (tr("Rebote"), self.env_bounce),
        )
        for row, (label_text, widget) in enumerate(rows):
            add_form_label(grid, row, label_text)
            grid.addWidget(widget, row, 1)
        card_layout.addLayout(grid)

        save_button = QPushButton(tr("Guardar ambiente"))
        save_button.setObjectName("btn_save_environment")
        save_button.setFixedHeight(28)
        save_button.clicked.connect(self.save_environment)
        card_layout.addWidget(save_button)

        light_button = QPushButton(tr("Crear luces en Krita"))
        light_button.setObjectName("btn_create_lighting")
        light_button.setFixedHeight(28)
        light_button.clicked.connect(self.create_lighting_rig)
        card_layout.addWidget(light_button)
        light_hint = QLabel(tr("Guarda el ambiente antes de crear las luces."))
        light_hint.setObjectName("hint")
        light_hint.setWordWrap(True)
        card_layout.addWidget(light_hint)
        self.environment_body.addWidget(card)

        preview = model.scene_preview(character)
        if preview:
            preview_frame = QFrame()
            preview_frame.setObjectName("scene_preview")
            preview_layout = QVBoxLayout(preview_frame)
            preview_layout.setContentsMargins(10, 9, 10, 10)
            preview_layout.setSpacing(6)
            preview_title = QLabel(tr("VISTA DE ESCENA"))
            preview_title.setObjectName("card_title")
            preview_layout.addWidget(preview_title)
            preview_note = QLabel(tr("Cómo cambian los colores clave con esta luz."))
            preview_note.setObjectName("hint")
            preview_note.setWordWrap(True)
            preview_layout.addWidget(preview_note)

            preview_grid = QGridLayout()
            preview_grid.setHorizontalSpacing(6)
            preview_grid.setVerticalSpacing(4)
            headers = ("", tr("Base"), tr("Sombra"), tr("Luz"), tr("Rebote"))
            for column, text in enumerate(headers):
                label = QLabel(text)
                label.setObjectName("field_label")
                preview_grid.addWidget(label, 0, column)
            for row_index, item in enumerate(preview, start=1):
                zone = QLabel(tr(model.zone_label(item["zone"])))
                zone.setObjectName("hint")
                preview_grid.addWidget(zone, row_index, 0)
                for column, (key, label) in enumerate(
                    (
                        ("base", tr("Base")),
                        ("shadow", tr("Sombra")),
                        ("light", tr("Luz")),
                        ("bounce", tr("Rebote")),
                    ),
                    start=1,
                ):
                    chip = ColorButton(item[key], 26)
                    chip.setToolTip(f"{item['name']} · {label}: {item[key]}")
                    chip.clicked.connect(
                        lambda checked=False, value=item[key]: self.apply_color(
                            value, 100, background=False
                        )
                    )
                    preview_grid.addWidget(chip, row_index, column, alignment=Qt.AlignLeft)
            preview_layout.addLayout(preview_grid)
            self.environment_body.addWidget(preview_frame)

        palette_header = QHBoxLayout()
        palette_header.setContentsMargins(0, 2, 0, 0)
        palette_header.setSpacing(6)
        palette_title = QLabel(tr("PALETA DEL AMBIENTE"))
        palette_title.setObjectName("card_title")
        palette_header.addWidget(palette_title, 1)
        add_color = QPushButton(tr("Añadir color de ambiente"))
        add_color.setObjectName("btn_add_env_color")
        add_color.setProperty("small", "true")
        add_color.setProperty("accent", "true")
        add_color.setFixedHeight(23)
        add_color.clicked.connect(lambda: self.add_swatch("environment"))
        palette_header.addWidget(add_color)
        self.environment_body.addLayout(palette_header)

        palette = environment.get("palette", [])
        if not palette:
            empty = QLabel(tr("Sin colores de ambiente. Añade la luz y los reflejos."))
            empty.setObjectName("empty_note")
            empty.setWordWrap(True)
            self.environment_body.addWidget(empty)
        for swatch in palette:
            self.environment_body.addWidget(self._swatch_card("environment", swatch))

        self.environment_body.addStretch(1)

    def _add_placeholder(self, layout, text: str) -> None:
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        label = QLabel(text)
        label.setObjectName("empty_note")
        label.setWordWrap(True)
        card_layout.addWidget(label)
        layout.addWidget(card)

    # ---------------------------------------------------------- personajes
    def _on_character_changed(self, index: int) -> None:
        if self._loading or index < 0:
            return
        character_id = self.character_combo.itemData(index)
        if not character_id or character_id == self.state.get("activeCharacterId"):
            return
        self.state["activeCharacterId"] = character_id
        self._save()
        self.refresh()

    def new_character(self) -> None:
        dialog = CharacterDialog(parent=self)
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()

        character = model.add_character(
            self.state, data["name"], data["summary"], data["tags"]
        )
        character["history"] = data["history"]
        character["personality"] = data["personality"]
        character["relationships"] = data["relationships"]
        self._save()
        self.refresh()

    def edit_character(self) -> None:
        character = self._character()
        if character is None:
            return
        dialog = CharacterDialog(parent=self, character=character)
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()

        character["name"] = data["name"]
        character["tags"] = data["tags"]
        character["summary"] = data["summary"]
        character["history"] = data["history"]
        character["personality"] = data["personality"]
        character["relationships"] = data["relationships"]
        self._save()
        self.refresh()

    def delete_character(self) -> None:
        character = self._character()
        if character is None:
            return
        name = str(character.get("name") or tr("este OC"))
        answer = QMessageBox.question(
            self,
            "Eliminar OC",
            f"¿Eliminar «{name}» con todas sus paletas y recetas?",
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        if model.delete_character(self.state, character.get("id")):
            self._save()
            self.refresh()

    # --------------------------------------------------------------- imágenes
    def set_reference_image(self) -> None:
        character = self._character()
        if character is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Elegir foto del OC"),
            str(Path.home()),
            tr("Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)"),
        )
        if not path:
            return
        try:
            reference = model.store_image(path, "oc")
        except Exception as exc:
            QMessageBox.critical(self, tr("Foto del OC"), str(exc))
            return
        previous = str(character.get("referenceImage") or "")
        character["referenceImage"] = reference
        if previous and previous != reference:
            model.remove_image(previous)
        self._save()
        self.refresh()

    def remove_reference_image(self) -> None:
        character = self._character()
        if character is None:
            return
        reference = str(character.get("referenceImage") or "")
        if not reference:
            return
        answer = QMessageBox.question(
            self,
            tr("Quitar foto"),
            tr("¿Quitar la foto del OC?"),
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        model.remove_image(reference)
        character["referenceImage"] = ""
        self._save()
        self.refresh()

    def open_reference_image(self) -> None:
        character = self._character()
        if character is None:
            return
        path = model.resolve_image(str(character.get("referenceImage") or ""))
        if path is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def set_zone_example(self, zone_key: str) -> None:
        character = self._character()
        if character is None:
            return
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Elegir ejemplo de la zona"),
            str(Path.home()),
            tr("Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)"),
        )
        if not path:
            return
        try:
            reference = model.store_image(path, f"zone-{zone_key}")
        except Exception as exc:
            QMessageBox.critical(self, tr("Ejemplo de la zona"), str(exc))
            return
        examples = character.setdefault("zoneExamples", {})
        previous = str(examples.get(zone_key) or "")
        examples[zone_key] = reference
        if previous and previous != reference:
            model.remove_image(previous)
        self._save()
        self.refresh()

    def remove_zone_example(self, zone_key: str) -> None:
        character = self._character()
        if character is None:
            return
        examples = character.get("zoneExamples") or {}
        reference = str(examples.pop(zone_key, "") or "")
        if reference:
            model.remove_image(reference)
        self._save()
        self.refresh()

    # --------------------------------------------------------------- colores
    def _apply_key_color(self, index: int, background: bool) -> None:
        character = self._character()
        if character is None:
            return
        colors = model.key_colors(character)
        self.apply_color(colors[index], 100, background=background)

    def apply_color(self, hex_color: str, opacity: int = 100, background: bool = False) -> bool:
        normalized = model.normalize_hex(hex_color)
        value = int(opacity) if self.apply_opacity.isChecked() else 100
        value = max(0, min(100, value))
        try:
            if background:
                applied = self.bridge.set_background(normalized, value)
            else:
                applied = self.bridge.set_foreground(normalized, value)
        except Exception:
            applied = False
        if not applied:
            self._set_status(tr("Abre un documento en Krita"))
            return False
        self._set_status(f"Color aplicado {normalized}")
        return True

    def add_swatch(self, zone_key: str) -> None:
        character = self._character()
        if character is None:
            return
        environment = zone_key == "environment"
        dialog = SwatchDialog(
            parent=self,
            environment=environment,
            default_body=model.default_body_part(zone_key),
        )
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()
        model.add_swatch(character, zone_key, data)
        self._save()
        self.refresh()

    def edit_swatch(self, zone_key: str, swatch: dict) -> None:
        character = self._character()
        if character is None:
            return
        swatch_id = str(swatch.get("id") or "")
        dialog = SwatchDialog(
            parent=self,
            swatch=swatch,
            environment=zone_key == "environment",
        )
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()
        model.update_swatch(character, zone_key, swatch_id, data)
        self._save()
        self.refresh()

    def delete_swatch(self, zone_key: str, swatch: dict) -> None:
        character = self._character()
        if character is None:
            return
        swatch_id = str(swatch.get("id") or "")
        name = str(swatch.get("name") or tr("este color"))
        answer = QMessageBox.question(
            self,
            tr("Eliminar color"),
            f"¿Eliminar «{name}»?",
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        if model.delete_swatch(character, zone_key, swatch_id):
            self._save()
            self.refresh()

    def _set_private_visible(self, checked: bool) -> None:
        if self._loading:
            return
        self.state["privateMode"] = not checked
        self._save()
        self.refresh()

    # ---------------------------------------------------------------- capas
    def add_layer(self) -> None:
        character = self._character()
        if character is None:
            return
        dialog = LayerDialog(parent=self)
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()
        model.add_layer(character, data)
        self._save()
        self.refresh()

    def edit_layer(self, layer: dict) -> None:
        character = self._character()
        if character is None:
            return
        layer_id = str(layer.get("id") or "")
        dialog = LayerDialog(parent=self, layer=layer)
        try:
            if exec_dialog(dialog) != DialogCode.Accepted:
                return
            data = dialog.data()
        finally:
            dialog.deleteLater()
        model.update_layer(character, layer_id, data)
        self._save()
        self.refresh()

    def delete_layer(self, layer: dict) -> None:
        character = self._character()
        if character is None:
            return
        layer_id = str(layer.get("id") or "")
        name = str(layer.get("name") or tr("esta capa"))
        answer = QMessageBox.question(
            self,
            tr("Eliminar capa"),
            f"¿Eliminar la capa «{name}» de la receta?",
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        if model.delete_layer(character, layer_id):
            self._save()
            self.refresh()

    def move_layer(self, layer_id: str, direction: str) -> None:
        character = self._character()
        if character is None:
            return
        if model.move_layer(character, layer_id, direction):
            self._save()
            self.refresh()

    def reset_recipe(self) -> None:
        character = self._character()
        if character is None:
            return
        answer = QMessageBox.question(
            self,
            tr("Restaurar receta"),
            tr("Se reemplazará la receta actual por la base (LINE, BASE, SHADOW…). ¿Continuar?"),
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        model.reset_recipe(character)
        self._save()
        self.refresh()

    def create_layers(self) -> None:
        character = self._character()
        if character is None:
            return
        try:
            self.bridge.create_layer_stack(character)
        except RuntimeError as exc:
            QMessageBox.information(self, tr("Crear capas en Krita"), str(exc))
            self._set_status(tr("Abre un documento en Krita"))
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("Crear capas en Krita"),
                f"No se pudieron crear las capas:\n{exc}",
            )
            self._set_status(tr("Error al crear las capas"), error=True)
            return
        self._set_status(tr("Grupo creado en el documento"))

    def create_lighting_rig(self) -> None:
        character = self._character()
        if character is None:
            return
        try:
            name = self.bridge.create_lighting_rig(character)
        except RuntimeError as exc:
            QMessageBox.information(self, tr("Crear luces en Krita"), str(exc))
            self._set_status(tr("Abre un documento en Krita"))
            return
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("Crear luces en Krita"),
                f"No se pudieron crear las luces:\n{exc}",
            )
            self._set_status(tr("Error al crear las luces"), error=True)
            return
        self._set_status(tr("Luces creadas") + ": " + name)

    # --------------------------------------------------------- color guard
    def _set_guard_enabled(self, checked: bool) -> None:
        if checked:
            self._guard_timer.start()
            self._check_color_guard()
            return
        self._guard_timer.stop()
        self._guard_target = None
        self.guard_snap.hide()
        self.guard_status.setText("")
        self._refresh_guard_style()

    def _check_color_guard(self) -> None:
        if not self.color_guard.isChecked():
            return
        character = self._character()
        if character is None:
            self.guard_status.setText("")
            self.guard_snap.hide()
            return
        foreground = self.bridge.foreground_color()
        if not foreground:
            self.guard_status.setText(tr("Abre un documento en Krita"))
            self.guard_status.setProperty("state", "muted")
            self.guard_snap.hide()
            self._guard_target = None
            self._refresh_guard_style()
            return
        hex_value, _alpha = foreground
        include_private = not bool(self.state.get("privateMode", True))
        match = model.nearest_swatch(character, hex_value, include_private=include_private)
        if not match:
            self.guard_status.setText(tr("Sin colores en la paleta"))
            self.guard_status.setProperty("state", "muted")
            self.guard_snap.hide()
            self._guard_target = None
            self._refresh_guard_style()
            return
        swatch = match["swatch"]
        name = str(swatch.get("name") or "")
        swatch_hex = str(swatch.get("hex") or "")
        delta = float(match["delta"])
        if delta <= 3.0:
            self.guard_status.setText(f"{tr('En paleta')} · {name} {swatch_hex}")
            self.guard_status.setProperty("state", "ok")
            self.guard_snap.hide()
            self._guard_target = None
        else:
            zone = tr(model.zone_label(match["zone"]))
            self.guard_status.setText(
                f"{tr('Fuera de paleta')} · {zone} · {name} {swatch_hex} · ΔE {delta:.1f}"
            )
            self.guard_status.setProperty("state", "warn")
            self.guard_snap.show()
            self._guard_target = swatch
        self._refresh_guard_style()

    def _snap_guard_color(self) -> None:
        target = self._guard_target
        if not target:
            return
        self.apply_color(
            str(target.get("hex") or "#808080"),
            int(target.get("opacity", 100)),
            background=False,
        )
        self._check_color_guard()

    def _refresh_guard_style(self) -> None:
        style = self.guard_status.style()
        style.unpolish(self.guard_status)
        style.polish(self.guard_status)

    # ------------------------------------------------------------ ambiente
    def save_environment(self) -> None:
        character = self._character()
        if character is None:
            return
        fields = (
            (tr("Luz clave"), self.env_key),
            (tr("Sombra"), self.env_shadow),
            (tr("Rebote"), self.env_bounce),
        )
        for label, field in fields:
            if normalize_hex_input(field.edit.text()) is None:
                QMessageBox.warning(
                    self,
                    tr("HEX no válido"),
                    f"{label}: escribe un color en formato #rrggbb.",
                )
                field.edit.setFocus()
                return
        environment = character.setdefault("environment", model.default_environment())
        environment["name"] = self.env_name.text().strip()
        environment["time"] = self.env_time.text().strip()
        environment["weather"] = self.env_weather.text().strip()
        environment["mood"] = self.env_mood.text().strip()
        environment["keyLight"] = self.env_key.value()
        environment["shadowTint"] = self.env_shadow.value()
        environment["bounce"] = self.env_bounce.value()
        environment.setdefault("palette", [])
        self._save()
        self.refresh()

    # ------------------------------------------------------------ archivos
    def import_json(self) -> None:
        start_dir = model.DATA_FILE.parent
        if not start_dir.exists():
            start_dir = Path.home()
        path, _ = QFileDialog.getOpenFileName(
            self, tr("Importar JSON"), str(start_dir), tr("JSON (*.json);;Todos los archivos (*)")
        )
        if not path:
            return
        answer = QMessageBox.question(
            self,
            tr("Importar JSON"),
            tr("Se reemplazarán todas las fichas, paletas y recetas actuales. ¿Continuar?"),
            MsgBox.Yes | MsgBox.No,
            MsgBox.No,
        )
        if answer != MsgBox.Yes:
            return
        try:
            imported = model.import_json(path)
            model.save_state(imported)
        except (ValueError, OSError) as exc:
            QMessageBox.critical(self, tr("Importar JSON"), str(exc))
            return
        self.state = imported
        self._last_saved_text = self._read_disk_text()
        self._arm_watcher()
        self.refresh()
        self._set_status(tr("JSON importado"))

    def export_json(self) -> None:
        folder = model.DATA_FILE.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            folder = Path.home()
        default_name = f"grimorio-color-backup-{datetime.now():%Y-%m-%d}.json"
        path, _ = QFileDialog.getSaveFileName(
            self, tr("Exportar JSON"), str(folder / default_name), tr("JSON (*.json)")
        )
        if not path:
            return
        if not path.lower().endswith(".json"):
            path += ".json"
        try:
            model.export_json(self.state, path)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(self, tr("Exportar JSON"), str(exc))
            return
        self._set_status(tr("JSON exportado"))

    def export_gpl(self) -> None:
        character = self._character()
        if character is None:
            return
        folder = model.DATA_FILE.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            folder = Path.home()
        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("Exportar .gpl"),
            str(folder / model.gpl_filename(character)),
            tr("Paleta GIMP (*.gpl)"),
        )
        if not path:
            return
        if not path.lower().endswith(".gpl"):
            path += ".gpl"
        try:
            model.export_gpl(
                character,
                path,
                include_private=not bool(self.state.get("privateMode", True)),
            )
        except OSError as exc:
            QMessageBox.critical(self, tr("Exportar .gpl"), str(exc))
            return
        self._set_status(tr("Paleta .gpl exportada"))

    def open_data_folder(self) -> None:
        folder = model.DATA_FILE.parent
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.warning(self, tr("Abrir carpeta"), str(exc))
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
            self._set_status(tr("No se pudo abrir la carpeta"))

    def web_target(self) -> str | None:
        configured = str(self.settings.value("webAppPath", "") or "").strip()
        if configured:
            return configured
        default = Path.home() / "proyectos" / "grimorio-color" / "index.html"
        return str(default) if default.is_file() else None

    def configure_web_app(self) -> None:
        current = self.web_target() or ""
        value, accepted = QInputDialog.getText(
            self,
            tr("Web del Grimorio"),
            tr("Ruta del index.html o URL:"),
            text=current,
        )
        if not accepted:
            return
        value = str(value).strip()
        if value:
            self.settings.setValue("webAppPath", value)
            self._set_status(tr("Web del Grimorio configurada"))
        else:
            self.settings.remove("webAppPath")

    def open_web_app(self) -> None:
        target = self.web_target()
        if not target:
            self.configure_web_app()
            target = self.web_target()
        if not target:
            return
        if target.lower().startswith(("http://", "https://", "file://")):
            url = QUrl(target)
        else:
            path = Path(target).expanduser()
            if not path.is_file():
                QMessageBox.warning(
                    self, tr("Web del Grimorio"), tr("No se encontró el archivo.")
                )
                return
            url = QUrl.fromLocalFile(str(path))
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(
                self, tr("Web del Grimorio"), tr("No se pudo abrir el navegador.")
            )

    def reload_from_disk(self) -> None:
        self.state = model.load_state()
        self._last_saved_text = self._read_disk_text()
        self._arm_watcher()
        self.refresh()
        self._set_status(tr("Recargado desde disco"))

    # --------------------------------------------------------------- guardado
    def _save(self) -> bool:
        try:
            model.save_state(self.state)
        except Exception:
            self._set_status(tr("Error al guardar"), error=True)
            return False
        self._last_saved_text = self._read_disk_text()
        self._arm_watcher()
        self._set_status(tr("Guardado ") + datetime.now().strftime("%H:%M"))
        return True

    def set_language(self, language: str) -> None:
        supported = {code for code, _ in i18n.available_languages()}
        code = str(language or "").strip().lower()
        if code not in supported:
            code = i18n.detect_language()
        if code == getattr(self, "_language", None):
            return
        self._language = code
        i18n.set_language(code)
        self.settings.setValue("language", code)
        QTimer.singleShot(0, self._rebuild_ui)

    def _rebuild_ui(self) -> None:
        tab_index = self.tabs.currentIndex() if hasattr(self, "tabs") else 0
        was_guard = bool(getattr(self, "color_guard", None) and self.color_guard.isChecked())
        try:
            self._guard_timer.stop()
        except Exception:
            pass
        self._guard_target = None
        old = self.layout()
        if old is not None:
            holder = QWidget()
            holder.setLayout(old)
            holder.deleteLater()
        for child in self.findChildren(QWidget):
            child.deleteLater()
        self._build_ui()
        if 0 <= tab_index < self.tabs.count():
            self.tabs.setCurrentIndex(tab_index)
        if was_guard:
            self.color_guard.setChecked(True)
        self.refresh()

    def create_translation_template(self) -> None:
        try:
            folder = i18n.ensure_translations_dir(self._translations_dir)
        except OSError as exc:
            QMessageBox.warning(self, tr("Plantilla de traducción"), str(exc))
            return
        template = folder / "translation-template.json"
        QMessageBox.information(
            self,
            tr("Plantilla de traducción"),
            tr("Se creó la plantilla en:")
            + f"\n{template}\n"
            + tr("Copia translation-template.json, cambia code y name, y traduce los valores."),
        )
        self.open_translations_folder()

    def open_translations_folder(self) -> None:
        try:
            folder = i18n.ensure_translations_dir(self._translations_dir)
        except OSError as exc:
            QMessageBox.warning(self, tr("Abrir carpeta de traducciones"), str(exc))
            return
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder))):
            self._set_status(tr("No se pudo abrir la carpeta"))

    def reload_translations(self) -> None:
        try:
            i18n.load_translations(
                self._translations_dir,
                extra_directories=[self._bundled_translations],
            )
        except OSError:
            pass
        supported = {code for code, _ in i18n.available_languages()}
        if self._language not in supported:
            self._language = i18n.detect_language()
            i18n.set_language(self._language)
            self.settings.setValue("language", self._language)
        QTimer.singleShot(0, self._rebuild_ui)

    def _set_status(self, text: str, error: bool = False) -> None:
        self.status.setText(text)
        self.status.setProperty("error", "true" if error else "false")
        style = self.status.style()
        style.unpolish(self.status)
        style.polish(self.status)

    @staticmethod
    def _read_disk_text() -> str | None:
        try:
            return model.DATA_FILE.read_text(encoding="utf-8")
        except OSError:
            return None

    def _arm_watcher(self) -> None:
        path = str(model.DATA_FILE)
        if model.DATA_FILE.exists() and path not in self._watcher.files():
            self._watcher.addPath(path)

    def _on_file_changed(self, path: str) -> None:
        QTimer.singleShot(150, self._reload_if_external)

    def _reload_if_external(self) -> None:
        text = self._read_disk_text()
        if text is None:
            self._arm_watcher()
            return
        if text == self._last_saved_text:
            self._arm_watcher()
            return
        try:
            self.state = model.load_state()
        except Exception:
            return
        self._last_saved_text = text
        self.refresh()
        self._set_status(tr("Recargado desde disco"))
        self._arm_watcher()
