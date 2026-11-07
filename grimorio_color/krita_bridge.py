# SPDX-FileCopyrightText: 2026 The Color Grimoire Authors
# SPDX-License-Identifier: GPL-3.0-or-later

"""Puente entre el Grimorio de Color y la API de Krita.

El modulo no importa ``krita`` al cargarse: la API se resuelve dentro de
``_api()`` para que la interfaz se pueda probar con PyQt5 fuera de Krita.
"""

from __future__ import annotations

from typing import Any

try:
    from .qt_compat import QColor
except ImportError:  # Ejecucion como modulo suelto (tests).
    from qt_compat import QColor

try:
    from . import model
except ImportError:  # Ejecucion como modulo suelto (tests).
    import model


class KritaBridge:
    """Operaciones minimas que el docker necesita de Krita."""

    def _api(self):
        """Devuelve las clases de Krita. Solo se importa dentro de Krita."""
        from krita import Krita, ManagedColor  # noqa: F401  (import perezoso)

        return Krita, ManagedColor

    def _active_view(self):
        Krita, _ = self._api()
        window = Krita.instance().activeWindow()
        if window is None:
            return None
        return window.activeView()

    def set_foreground(self, hex_color: str, opacity: int = 100) -> bool:
        """Pone el color como color de primer plano activo."""
        return self._set_color(hex_color, opacity, background=False)

    def set_background(self, hex_color: str, opacity: int = 100) -> bool:
        """Pone el color como color de fondo activo."""
        return self._set_color(hex_color, opacity, background=True)

    def _set_color(self, hex_color: str, opacity: int, background: bool) -> bool:
        try:
            Krita, ManagedColor = self._api()
            view = self._active_view()
            if view is None:
                return False
            qcolor = QColor(hex_color)
            if not qcolor.isValid():
                return False
            qcolor.setAlphaF(max(0, min(100, int(opacity))) / 100.0)
            managed = ManagedColor.fromQColor(qcolor)
            if background:
                view.setBackGroundColor(managed)
            else:
                view.setForeGroundColor(managed)
            return True
        except Exception:
            # Sin documento, sin ventana o sin API de Krita: la UI lo avisa.
            return False

    def create_layer_stack(self, character: dict[str, Any], document=None) -> str:
        """Crea un grupo con la receta del OC en el documento activo.

        ``document`` permite pasar un documento concreto (tests). Devuelve el
        nombre del grupo. Lanza ``RuntimeError`` si no hay documento abierto.
        """
        Krita, _ = self._api()
        if document is None:
            document = Krita.instance().activeDocument()
        if document is None:
            raise RuntimeError("Abre un documento en Krita para crear las capas.")

        name = str(character.get("name") or "OC").strip() or "OC"
        root = document.rootNode()
        group = document.createGroupLayer("Grimorio - " + name)
        if group is None:
            raise RuntimeError("No se pudo crear el grupo de capas.")
        root.addChildNode(group, None)

        layers = []
        for index, row in enumerate(character.get("recipe", [])):
            layer_name = str(row.get("name") or f"Capa {index + 1}").strip() or f"Capa {index + 1}"
            layer = document.createNode(layer_name, "paintlayer")
            if layer is None:
                raise RuntimeError(f"No se pudo crear la capa «{layer_name}».")
            blend = model.KRITA_BLEND_IDS.get(str(row.get("blend") or "normal"), "normal")
            try:
                layer.setBlendingMode(blend)
            except Exception:
                # Un modo desconocido no debe impedir crear el resto.
                try:
                    layer.setBlendingMode("normal")
                except Exception:
                    pass
            try:
                layer.setOpacity(int(round(float(row.get("opacity", 100)) * 255 / 100)))
            except (TypeError, ValueError):
                layer.setOpacity(255)
            layers.append(layer)

        # setChildNodes recibe la lista de abajo arriba: el primer nodo es el
        # fondo de la pila. La receta se muestra de arriba abajo.
        group.setChildNodes(list(reversed(layers)))
        return group.name()

    def create_lighting_rig(self, character: dict[str, Any], document=None) -> str:
        """Crea un grupo de capas de relleno con la luz del ambiente.

        Las capas son SHADOW (Multiply), AO (Multiply), LIGHT (Add),
        GLOW (Add) y BOUNCE (Add). El grupo hereda alfa para recortarse a lo
        que haya debajo. Devuelve el nombre del grupo.
        """
        Krita, _ = self._api()
        from krita import InfoObject, Selection

        if document is None:
            document = Krita.instance().activeDocument()
        if document is None:
            raise RuntimeError("Abre un documento en Krita para crear las luces.")

        environment = character.get("environment") or {}
        scene_name = str(environment.get("name") or "Scene").strip() or "Scene"
        group = document.createGroupLayer("Lighting — " + scene_name)
        if group is None:
            raise RuntimeError("No se pudo crear el grupo de luces.")
        document.rootNode().addChildNode(group, None)

        layers = []
        for spec in model.lighting_spec(character):
            info = InfoObject()
            info.setProperty("color", spec["color"])
            selection = Selection()
            selection.select(0, 0, document.width(), document.height(), 255)
            layer = document.createFillLayer(spec["name"], "color", info, selection)
            if layer is None:
                continue
            try:
                layer.setBlendingMode(spec["blend"])
            except Exception:
                try:
                    layer.setBlendingMode("normal")
                except Exception:
                    pass
            layer.setOpacity(int(round(float(spec["opacity"]) * 255 / 100)))
            layers.append(layer)

        if not layers:
            try:
                group.remove()
            except Exception:
                pass
            raise RuntimeError("No se pudieron crear las capas de luz.")

        # lighting_spec va de arriba abajo; setChildNodes espera de abajo arriba.
        group.setChildNodes(list(reversed(layers)))
        try:
            group.setInheritAlpha(True)
        except Exception:
            pass
        return group.name()

    def foreground_color(self) -> tuple[str, int] | None:
        """Color de primer plano activo como (hex, alpha 0-255), o None."""
        try:
            Krita, _ = self._api()
            view = self._active_view()
            if view is None:
                return None
            managed = view.foregroundColor()
            if managed is None:
                return None
            canvas = view.canvas()
            if canvas is None:
                return None
            qcolor = managed.colorForCanvas(canvas)
            if qcolor is None:
                return None
            return qcolor.name(), qcolor.alpha()
        except Exception:
            return None

    def active_document_name(self) -> str | None:
        """Nombre del documento activo, o ``None`` si no hay ninguno."""
        try:
            Krita, _ = self._api()
            document = Krita.instance().activeDocument()
            if document is None:
                return None
            return str(document.name())
        except Exception:
            return None
