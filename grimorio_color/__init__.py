# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

__version__ = "0.7.0"

from krita import DockWidget, DockWidgetFactory, DockWidgetFactoryBase

from .ui import GrimorioPanel


class GrimorioDocker(DockWidget):
    def __init__(self):
        super().__init__()
        self.panel = GrimorioPanel()
        self.setWidget(self.panel)
        self.setWindowTitle("Grimorio de Color")

    def canvasChanged(self, canvas):
        pass


Application.addDockWidgetFactory(
    DockWidgetFactory(
        "grimorio_color",
        DockWidgetFactoryBase.DockPosition.DockRight,
        GrimorioDocker,
    )
)
