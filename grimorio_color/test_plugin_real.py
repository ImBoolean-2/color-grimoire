# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Carga el plugin con la API real de Krita usando kritarunner.

Ejecutar:
    flatpak run --env=QT_QPA_PLATFORM=offscreen --env=QT_QPA_PLATFORMTHEME= \
      --env=PYTHONPATH=$PWD/plugin \
      --command=kritarunner org.kde.krita --script test_plugin_real -f main
"""

from __future__ import annotations

import builtins
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent
sys.path.insert(0, str(PLUGIN_ROOT))

from krita import Krita  # noqa: E402

LOG_PATH = Path.home() / ".cache" / "grimorio-plugin-real.log"


def main(*_args) -> int:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("w", encoding="utf-8") as out:
        out.write("START\n")
        out.flush()
        app = Krita.instance()
        builtins.Application = app
        import grimorio_color

        grimorio_color.model.DATA_FILE = Path(tempfile.mkdtemp(prefix="grimorio-plugin-")) / "grimorio.json"
        out.write(f"PACKAGE {grimorio_color.__name__}\n")
        out.write(f"FACTORY_CLASS {grimorio_color.GrimorioDocker.__name__}\n")
        docker = grimorio_color.GrimorioDocker()
        out.write(f"DOCKER {docker.windowTitle()}\n")
        widget = docker.widget()
        out.write(f"WIDGET {widget.objectName() if widget else None}\n")
        out.write("DONE\n")
        out.flush()
        docker.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
