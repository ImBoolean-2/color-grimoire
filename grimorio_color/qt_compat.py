# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Compatibilidad Qt para Krita 5 (PyQt5) y Krita 6 (PyQt6).

Krita 5.3 usa Qt5/PyQt5; Krita 6 usa Qt6/PyQt6. Este módulo importa el
binding disponible y expone un ``Qt`` con los enums que usa la UI, para no
tener que escribir dos versiones de cada widget.
"""

from __future__ import annotations

PYQT6 = False
try:
    from PyQt6.QtCore import (  # type: ignore[import-not-found]
        QFileSystemWatcher,
        QLocale,
        QSettings,
        QTimer,
        QUrl,
        Qt as _Qt,
        pyqtSignal,
    )
    from PyQt6.QtGui import (  # type: ignore[import-not-found]
        QAction,
        QBrush,
        QColor,
        QDesktopServices,
        QLinearGradient,
        QPainter,
        QPixmap,
    )
    from PyQt6.QtWidgets import (  # type: ignore[import-not-found]
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QDockWidget,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QMenu,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )

    PYQT6 = True

    class Qt:
        AlignCenter = _Qt.AlignmentFlag.AlignCenter
        AlignHCenter = _Qt.AlignmentFlag.AlignHCenter
        AlignLeft = _Qt.AlignmentFlag.AlignLeft
        AlignRight = _Qt.AlignmentFlag.AlignRight
        AlignTop = _Qt.AlignmentFlag.AlignTop
        AlignVCenter = _Qt.AlignmentFlag.AlignVCenter
        Horizontal = _Qt.Orientation.Horizontal
        KeepAspectRatio = _Qt.AspectRatioMode.KeepAspectRatio
        PointingHandCursor = _Qt.CursorShape.PointingHandCursor
        RichText = _Qt.TextFormat.RichText
        SmoothTransformation = _Qt.TransformationMode.SmoothTransformation
        RightButton = _Qt.MouseButton.RightButton
        ScrollBarAlwaysOff = _Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        StrongFocus = _Qt.FocusPolicy.StrongFocus
        TextSelectableByMouse = _Qt.TextInteractionFlag.TextSelectableByMouse
        WA_StyledBackground = _Qt.WidgetAttribute.WA_StyledBackground

    class MsgBox:
        Yes = QMessageBox.StandardButton.Yes
        No = QMessageBox.StandardButton.No

    class DialogCode:
        Accepted = QDialog.DialogCode.Accepted
        Rejected = QDialog.DialogCode.Rejected

    class SizePolicy:
        Expanding = QSizePolicy.Policy.Expanding
        Fixed = QSizePolicy.Policy.Fixed

    class ToolButtonPopupMode:
        InstantPopup = QToolButton.ToolButtonPopupMode.InstantPopup

    class FrameShape:
        NoFrame = QFrame.Shape.NoFrame

except ImportError:  # Krita 5.3 / PyQt5
    from PyQt5.QtCore import (  # type: ignore[import-not-found]
        QFileSystemWatcher,
        QLocale,
        QSettings,
        QTimer,
        QUrl,
        Qt,
        pyqtSignal,
    )
    from PyQt5.QtGui import (  # type: ignore[import-not-found]
        QBrush,
        QColor,
        QDesktopServices,
        QLinearGradient,
        QPainter,
        QPixmap,
    )
    from PyQt5.QtWidgets import (  # type: ignore[import-not-found]
        QAction,
        QApplication,
        QCheckBox,
        QColorDialog,
        QComboBox,
        QDialog,
        QDockWidget,
        QFileDialog,
        QFormLayout,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QLineEdit,
        QMenu,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSizePolicy,
        QSlider,
        QSpinBox,
        QTabWidget,
        QTextEdit,
        QToolButton,
        QVBoxLayout,
        QWidget,
    )

    MsgBox = QMessageBox
    DialogCode = QDialog
    SizePolicy = QSizePolicy
    ToolButtonPopupMode = QToolButton
    FrameShape = QFrame


def exec_dialog(dialog: QDialog) -> int:
    """``exec_`` en PyQt5, ``exec`` en PyQt6."""
    if hasattr(dialog, "exec"):
        return dialog.exec()
    return dialog.exec_()


def exec_application(app: QApplication) -> int:
    if hasattr(app, "exec"):
        return app.exec()
    return app.exec_()
