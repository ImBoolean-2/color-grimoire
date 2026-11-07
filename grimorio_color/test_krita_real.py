# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Prueba real de la API de Krita con kritarunner (offscreen).

Ejecutar:
    flatpak run --env=QT_QPA_PLATFORM=offscreen --env=QT_QPA_PLATFORMTHEME= \
      --env=PYTHONPATH=/home/valentino/proyectos/grimorio-color/plugin/grimorio_color \
      --command=kritarunner org.kde.krita --script test_krita_real -f main
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import model  # noqa: E402
import krita_bridge  # noqa: E402
from krita import Krita  # noqa: E402

LOG_PATH = Path.home() / ".cache" / "grimorio-krita-real.log"


def walk(node, out, depth=0):
    for child in node.childNodes():
        out.write(
            "  " * depth
            + f"- {child.name()} | {child.type()} | blend={child.blendingMode()} | opacity={child.opacity()}\n"
        )
        walk(child, out, depth + 1)


def main(*_args) -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("w", encoding="utf-8") as out:
        out.write("START\n")
        out.flush()
        app = Krita.instance()
        out.write(f"KRITA {app.version()}\n")
        out.flush()

        document = app.createDocument(256, 256, "Grimorio real test", "RGBA", "U8", "sRGB-elle-V2-srgbtrc.icc", 72.0)
        out.write(f"CREATED {document.name() if document else None}\n")
        out.flush()
        window = app.activeWindow()
        out.write(f"WINDOW {window}\n")
        out.flush()
        if window is not None:
            window.addView(document)
            active = app.activeDocument()
            out.write(f"ACTIVE {active.name() if active else None}\n")
        else:
            out.write("NO_WINDOW (se prueba la pila de capas con el documento directo)\n")
        out.flush()

        bridge = krita_bridge.KritaBridge()
        state = model.seed_state()
        character = model.active_character(state)
        group_name = bridge.create_layer_stack(character, document=document)
        out.write(f"GROUP {group_name}\n")
        stack = document.nodeByName(group_name)
        if stack is not None:
            out.write("STACK " + ",".join(node.name() for node in stack.childNodes()) + "\n")
        out.write("ROOT\n")
        walk(document.rootNode(), out)

        light_name = bridge.create_lighting_rig(character, document=document)
        out.write(f"LIGHT_GROUP {light_name}\n")
        light_group = document.nodeByName(light_name)
        if light_group is not None:
            out.write(f"LIGHT_INHERIT {light_group.inheritAlpha()}\n")
            out.write("LIGHT_CHILDREN " + ",".join(node.name() for node in light_group.childNodes()) + "\n")
            for node in light_group.childNodes():
                config = {}
                if hasattr(node, "filterConfig") and node.filterConfig() is not None:
                    config = node.filterConfig().properties()
                out.write(
                    f"  {node.name()} blend={node.blendingMode()} opacity={node.opacity()} color={config.get('color')}\n"
                )
        out.write("ROOT2\n")
        walk(document.rootNode(), out)

        out.write("BLENDS\n")
        for key, krita_id in model.KRITA_BLEND_IDS.items():
            layer = document.createNode(f"blend-{key}", "paintlayer")
            document.rootNode().addChildNode(layer, None)
            layer.setBlendingMode(krita_id)
            out.write(f"{key} -> {krita_id} -> {layer.blendingMode()}\n")
        out.write("DONE\n")
        out.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
