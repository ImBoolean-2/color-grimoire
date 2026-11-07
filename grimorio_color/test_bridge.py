# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Prueba del puente a Krita y del punto de entrada del plugin, sin Krita.

Ejecutar con el Python del Flatpak (tiene PyQt5):
    flatpak run --command=python3 org.kde.krita test_bridge.py
"""

from __future__ import annotations

import builtins
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["QT_QPA_PLATFORMTHEME"] = ""

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))

from qt_compat import QApplication, QColor, QDockWidget  # noqa: E402


class FakeNode:
    def __init__(self, name):
        self._name = name
        self.blend = None
        self.opacity = None
        self.children = None
        self.added_to = None
        self.config = None
        self.inherit_alpha = False
        self.filter_name = None

    def name(self):
        return self._name

    def setBlendingMode(self, value):
        self.blend = value

    def setOpacity(self, value):
        self.opacity = value

    def setChildNodes(self, nodes):
        self.children = list(nodes)

    def addChildNode(self, child, above):
        child.added_to = self
        return True

    def setInheritAlpha(self, value):
        self.inherit_alpha = bool(value)

    def inheritAlpha(self):
        return self.inherit_alpha

    def remove(self):
        return True


class FakeDocument:
    def __init__(self):
        self.root = FakeNode("root")
        self.created_groups = []
        self.created_layers = []

    def rootNode(self):
        return self.root

    def createGroupLayer(self, name):
        group = FakeNode(name)
        self.created_groups.append(group)
        return group

    def createNode(self, name, nodeType):
        layer = FakeNode(name)
        layer.node_type = nodeType
        self.created_layers.append(layer)
        return layer

    def createFillLayer(self, name, filterName, configuration, selection):
        layer = FakeNode(name)
        layer.filter_name = filterName
        layer.config = configuration
        self.created_layers.append(layer)
        return layer

    def width(self):
        return 256

    def height(self):
        return 256

    def name(self):
        return "documento-de-prueba"


class FakeManaged:
    def __init__(self, qcolor):
        self.qcolor = qcolor

    def colorForCanvas(self, canvas):
        return self.qcolor


class FakeView:
    def __init__(self):
        self.foreground = None
        self.background = None
        self.foreground_managed = FakeManaged(QColor("#000000"))
        self.canvas_obj = object()

    def setForeGroundColor(self, color):
        self.foreground = color

    def setBackGroundColor(self, color):
        self.background = color

    def foregroundColor(self):
        return self.foreground_managed

    def canvas(self):
        return self.canvas_obj


class FakeWindow:
    def __init__(self, view):
        self.view = view

    def activeView(self):
        return self.view


class FakeKritaInstance:
    def __init__(self):
        self.view = FakeView()
        self.document = FakeDocument()

    def activeWindow(self):
        return FakeWindow(self.view)

    def activeDocument(self):
        return self.document


class FakeManagedColor:
    @staticmethod
    def fromQColor(qcolor):
        return qcolor


class FakeInfoObject:
    def __init__(self):
        self.props = {}

    def setProperty(self, key, value):
        self.props[key] = value

    def properties(self):
        return dict(self.props)


class FakeSelection:
    def select(self, *args):
        return None


class FakeKritaClass:
    _instance = FakeKritaInstance()

    @classmethod
    def instance(cls):
        return cls._instance


class FakeDockPosition:
    DockRight = "right"


class FakeDockWidgetFactoryBase:
    DockPosition = FakeDockPosition


class FakeDockWidgetFactory:
    def __init__(self, plugin_id, position, klass):
        self.plugin_id = plugin_id
        self.position = position
        self.klass = klass


class FakeApplication:
    def __init__(self):
        self.factories = []

    def addDockWidgetFactory(self, factory):
        self.factories.append(factory)


def install_fake_krita():
    fake = types.ModuleType("krita")
    fake.Krita = FakeKritaClass
    fake.ManagedColor = FakeManagedColor
    fake.DockWidget = QDockWidget
    fake.DockWidgetFactory = FakeDockWidgetFactory
    fake.DockWidgetFactoryBase = FakeDockWidgetFactoryBase
    fake.InfoObject = FakeInfoObject
    fake.Selection = FakeSelection
    sys.modules["krita"] = fake
    app = FakeApplication()
    builtins.Application = app
    return fake, app


class BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        install_fake_krita()
        import model

        cls.model = model
        cls.temp = tempfile.TemporaryDirectory(prefix="grimorio-bridge-")
        model.DATA_FILE = Path(cls.temp.name) / "grimorio.json"

        import krita_bridge

        cls.bridge = krita_bridge.KritaBridge()
        cls.state = model.seed_state()
        cls.character = model.active_character(cls.state)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_set_foreground_and_background(self):
        view = FakeKritaClass._instance.view
        self.assertTrue(self.bridge.set_foreground("#c98d6b", 60))
        self.assertIsInstance(view.foreground, QColor)
        self.assertAlmostEqual(view.foreground.alphaF(), 0.6, places=2)
        self.assertTrue(self.bridge.set_background("#123456", 100))
        self.assertIsInstance(view.background, QColor)
        self.assertAlmostEqual(view.background.alphaF(), 1.0, places=2)

    def test_create_layer_stack(self):
        doc = FakeKritaClass._instance.document
        doc.created_groups.clear()
        doc.created_layers.clear()
        name = self.bridge.create_layer_stack(self.character)
        self.assertEqual(name, "Grimorio - Rowan Vale")
        self.assertEqual(len(doc.created_groups), 1)
        self.assertEqual(len(doc.created_layers), 7)
        group = doc.created_groups[0]
        self.assertEqual(group.name(), "Grimorio - Rowan Vale")
        self.assertIsNotNone(group.children)
        # setChildNodes recibe de abajo arriba: FX es el fondo, LINE el top.
        self.assertEqual(group.children[0].name(), "FX")
        self.assertEqual(group.children[-1].name(), "LINE")
        by_name = {layer.name(): layer for layer in doc.created_layers}
        self.assertEqual(by_name["SHADOW"].blend, "multiply")
        self.assertEqual(by_name["LIGHT"].blend, "add")
        self.assertEqual(by_name["FX"].blend, "overlay")
        self.assertEqual(by_name["SHADOW"].opacity, 115)  # 45% de 255
        self.assertEqual(by_name["LINE"].opacity, 255)

    def test_create_lighting_rig(self):
        doc = FakeKritaClass._instance.document
        doc.created_groups.clear()
        doc.created_layers.clear()
        name = self.bridge.create_lighting_rig(self.character)
        self.assertEqual(name, "Lighting — Pine forest at dusk")
        self.assertEqual(len(doc.created_groups), 1)
        group = doc.created_groups[0]
        self.assertEqual([node.name() for node in group.children], ["BOUNCE", "GLOW", "LIGHT", "AO", "SHADOW"])
        self.assertTrue(group.inheritAlpha())
        by_name = {layer.name(): layer for layer in doc.created_layers}
        self.assertEqual(by_name["SHADOW"].blend, "multiply")
        self.assertEqual(by_name["LIGHT"].blend, "add")
        self.assertEqual(by_name["BOUNCE"].blend, "add")
        self.assertEqual(by_name["SHADOW"].config.props["color"], self.character["environment"]["shadowTint"])
        self.assertEqual(by_name["LIGHT"].config.props["color"], self.character["environment"]["keyLight"])
        self.assertEqual(by_name["SHADOW"].opacity, 115)
        self.assertEqual(by_name["LIGHT"].opacity, 76)
        self.assertEqual(by_name["BOUNCE"].opacity, 51)

    def test_foreground_color(self):
        view = FakeKritaClass._instance.view
        view.foreground_managed = FakeManaged(QColor("#c98d6b"))
        result = self.bridge.foreground_color()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "#c98d6b")
        self.assertEqual(result[1], 255)

    def test_create_layer_stack_without_document(self):
        original = FakeKritaClass._instance.document
        FakeKritaClass._instance.document = None
        try:
            with self.assertRaises(RuntimeError):
                self.bridge.create_layer_stack(self.character)
        finally:
            FakeKritaClass._instance.document = original


class EntryPointTests(unittest.TestCase):
    def test_plugin_registers_docker(self):
        qt_app = QApplication.instance() or QApplication([])
        fake, app = install_fake_krita()

        with tempfile.TemporaryDirectory(prefix="grimorio-entry-") as temp:
            import grimorio_color

            grimorio_color.model.DATA_FILE = Path(temp) / "grimorio.json"
            self.assertEqual(len(app.factories), 1)
            factory = app.factories[0]
            self.assertEqual(factory.plugin_id, "grimorio_color")
            self.assertEqual(factory.position, "right")
            docker = factory.klass()
            self.assertEqual(docker.windowTitle(), "Grimorio de Color")
            self.assertIsNotNone(docker.widget())
            self.assertEqual(docker.widget().objectName(), "grimorio_panel")
            docker.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
