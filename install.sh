#!/usr/bin/env bash
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -d "$HOME/.var/app/org.kde.krita/data/krita" ]]; then
  DEST="$HOME/.var/app/org.kde.krita/data/krita/pykrita"
else
  DEST="$HOME/.local/share/krita/pykrita"
fi

if [[ ! -d "$SRC/grimorio_color" ]]; then
  echo "No encuentro $SRC/grimorio_color" >&2
  exit 1
fi

mkdir -p "$DEST"
rm -rf "$DEST/grimorio_color"
cp -a "$SRC/grimorio_color" "$DEST/grimorio_color"
cp "$SRC/grimorio_color.desktop" "$DEST/grimorio_color.desktop"
rm -rf "$DEST/grimorio_color/__pycache__"
rm -f "$DEST/grimorio_color/seed.personal.json"

echo "Instalado en: $DEST"
echo
echo "Abre Krita."
echo "Settings → Configure Krita → Python Plugin Manager"
echo "Activa 'Color Grimoire' y reinicia Krita."
echo "El panel estará en Settings → Dockers → Color Grimoire."
