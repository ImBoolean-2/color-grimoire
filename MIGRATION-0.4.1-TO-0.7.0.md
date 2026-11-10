# Updating Color Grimoire: 0.4.1 → 0.7.0

**English** · [Español](#español)

This takes about five minutes. You do not need to export, convert or rename anything.

> **Do not delete anything.** The plugin makes its own backup the first time 0.7.0 opens your old file. Your projects, palettes, recipes, environments and images stay where they are.

## Before you start

- Close Krita. The data file is only safe to copy while Krita is closed.
- You need the `grimorio_color-0.7.0.zip` file from the Releases page.

## Step by step

1. **Close Krita** completely.

2. **(Optional) Make your own copy.** Open your data folder (paths below) and copy `grimorio.json` and the `images/` folder somewhere safe. This is a second safety net, not a requirement: the plugin creates a backup by itself.

3. **Install 0.7.0.** Open Krita and go to **Tools → Scripts → Import Python Plugins…**, select `grimorio_color-0.7.0.zip` and accept replacing the old version.

4. **Restart Krita.** Then open **Settings → Configure Krita → Python Plugin Manager** and check that **Color Grimoire** is enabled. Restart Krita once more.

5. **Open the docker**: **Settings → Dockers → Color Grimoire**. The first time it reads your 0.4.1 file, it converts it to the new format automatically and writes the backup. This happens once; you do not have to press anything.

6. **Check the backup.** Use **⋯ → Open data folder** and look for `grimorio.json.v1.bak`. That is your original 0.4.1 file. If a backup with that name already existed and your file had changed since, the new copy is named `grimorio.json.v1-<timestamp>.bak` (for example `grimorio.json.v1-20261110-143000.bak`).

7. **Open one of your projects** and check, in this order:
   - [ ] The project list still shows your characters.
   - [ ] **Palettes** shows your zones and colors.
   - [ ] **Layers** shows your recipe.
   - [ ] **Environment** shows your scene and its palette.
   - [ ] Your photo and zone examples still appear (they need the `images/` folder next to the JSON).
   - [ ] The **Private** zone is still hidden until you turn on **Show private**.
   - [ ] There is a new **Library** tab, empty until you save a palette there.

8. **Only if you use Loomis Head Guide:** update **both** plugins (Grimoire 0.7.0 and Loomis Head Guide 0.6.1). Save in Loomis first, then in Grimoire. Do not save in both at the same time. The head block is copied as-is; Grimoire never interprets it.

## The web app

The web app is not inside the ZIP. The first time the new version opens, it converts the old `localStorage` data to the new format and keeps a copy under the key `grimorio-color:v1-backup`. Nothing is deleted.

If you use **another browser or another computer**, the browser storage does not travel. Open the old browser, use **Export JSON**, then open the new one and use **Import JSON**. The `localStorage` backup only protects the browser where it was created.

## If something goes wrong

1. Close Krita.
2. In the data folder, delete or rename the current `grimorio.json`, then copy `grimorio.json.v1.bak` and rename the copy to `grimorio.json`.
3. Keep the `images/` folder where it is.
4. Reopen Krita and check your projects.

That file is your 0.4.1 data. With 0.7.0 installed it will be converted again the next time the docker opens, so this restores data — it is not a way to keep working on 0.4.1. **Downgrade is not supported**: the backup is the safety net.

## Data folder

| System | Folder |
| --- | --- |
| Linux (Flatpak) | `~/.var/app/org.kde.krita/data/krita/grimorio-color/` |
| Linux (native) | `~/.local/share/krita/grimorio-color/` |
| Windows | `%APPDATA%\krita\grimorio-color\` |
| macOS | `~/Library/Application Support/krita/grimorio-color/` |

The file is `grimorio.json`; the photos and zone examples are in `images/` next to it. **⋯ → Open data folder** opens it for you.

## What changes and what does not

| Stays exactly the same | New in 0.7.0 |
| --- | --- |
| Your projects/OCs, palettes, recipes, environments and images | Project types: character, scene and prop, each with its own starter zones |
| Private mode and the private zone | Zone editor: add, rename, reorder, mark private, delete |
| The Loomis `head` block | Palette library: save a zone and import it into another project |
| JSON, `.gpl`, print and Export/Import | Several environments per project, with one active |
| Spanish/English and custom translations | Sheet and print adapt to the project type |

Deleting a zone in the new editor does not delete its colors: the palette is kept as a hidden extra. That is why nothing disappears during the update.

---

## Español

**Actualizar Color Grimoire: 0.4.1 → 0.7.0**

Son unos cinco minutos. No tienes que exportar, convertir ni renombrar nada.

> **No borres nada.** El plugin crea su propio backup la primera vez que 0.7.0 abre tu archivo antiguo. Tus proyectos, paletas, recetas, ambientes e imágenes se quedan donde están.

### Antes de empezar

- Cierra Krita. El archivo de datos solo se copia con seguridad con Krita cerrado.
- Necesitas el `grimorio_color-0.7.0.zip` de la página de Releases.

### Paso a paso

1. **Cierra Krita** por completo.

2. **(Opcional) Haz tu propia copia.** Abre tu carpeta de datos (rutas abajo) y copia `grimorio.json` y la carpeta `images/` a un sitio seguro. Es una segunda red de seguridad, no hace falta: el plugin crea el backup solo.

3. **Instala 0.7.0.** Abre Krita y ve a **Tools → Scripts → Import Python Plugins…**, elige `grimorio_color-0.7.0.zip` y acepta reemplazar la versión anterior.

4. **Reinicia Krita.** Después abre **Settings → Configure Krita → Python Plugin Manager** y comprueba que **Color Grimoire** está activado. Reinicia Krita otra vez.

5. **Abre el docker**: **Settings → Dockers → Color Grimoire**. La primera vez lee tu archivo de 0.4.1, lo convierte al formato nuevo solo y escribe el backup. Pasa una vez; no hay que pulsar nada.

6. **Comprueba el backup.** Usa **⋯ → Abrir carpeta de datos** y busca `grimorio.json.v1.bak`. Es tu archivo original de 0.4.1. Si ya existía un backup con ese nombre y tu archivo había cambiado, la copia nueva se llama `grimorio.json.v1-<fecha>.bak` (por ejemplo `grimorio.json.v1-2026-11-10-1430.bak`).

7. **Abre uno de tus proyectos** y comprueba, en este orden:
   - [ ] La lista de proyectos sigue mostrando tus personajes.
   - [ ] **Paletas** muestra tus zonas y colores.
   - [ ] **Capas** muestra tu receta.
   - [ ] **Ambiente** muestra tu escena y su paleta.
   - [ ] Tu foto y los ejemplos de zona siguen apareciendo (necesitan la carpeta `images/` junto al JSON).
   - [ ] La zona **Privado** sigue oculta hasta activar **Mostrar privado**.
   - [ ] Hay una pestaña nueva, **Biblioteca**, vacía hasta que guardes una paleta ahí.

8. **Solo si usas Loomis Head Guide:** actualiza **los dos** plugins (Grimorio 0.7.0 y Loomis Head Guide 0.6.1). Guarda primero en Loomis y después en Grimorio. No guardes en los dos a la vez. El bloque de la cabeza se copia tal cual; Grimorio nunca lo interpreta.

### La app web

La app web no va dentro del ZIP. La primera vez que la abras, convierte los datos antiguos de `localStorage` al formato nuevo y guarda una copia en la clave `grimorio-color:v1-backup`. No se borra nada.

Si usas **otro navegador u otro equipo**, el almacenamiento del navegador no viaja. Abre el navegador viejo, usa **Export JSON**, y en el nuevo usa **Import JSON**. El backup de `localStorage` solo protege el navegador donde se creó.

### Si algo va mal

1. Cierra Krita.
2. En la carpeta de datos, borra o renombra el `grimorio.json` actual, copia `grimorio.json.v1.bak` y renombra la copia a `grimorio.json`.
3. Deja la carpeta `images/` donde está.
4. Vuelve a abrir Krita y revisa tus proyectos.

Ese archivo son tus datos de 0.4.1. Con 0.7.0 instalado se volverá a convertir la próxima vez que abras el docker, así que esto sirve para recuperar datos, no para seguir trabajando en 0.4.1. **El downgrade no está soportado**: el backup es la red de seguridad.

### Carpeta de datos

| Sistema | Carpeta |
| --- | --- |
| Linux (Flatpak) | `~/.var/app/org.kde.krita/data/krita/grimorio-color/` |
| Linux (nativo) | `~/.local/share/krita/grimorio-color/` |
| Windows | `%APPDATA%\krita\grimorio-color\` |
| macOS | `~/Library/Application Support/krita/grimorio-color/` |

El archivo es `grimorio.json`; las fotos y los ejemplos de zona están en `images/`, al lado. **⋯ → Abrir carpeta de datos** te abre la carpeta.

### Qué cambia y qué no

| Se queda igual | Nuevo en 0.7.0 |
| --- | --- |
| Tus proyectos/OCs, paletas, recetas, ambientes e imágenes | Tipos de proyecto: personaje, escenario y prop, cada uno con sus zonas iniciales |
| El modo privado y la zona privada | Editor de zonas: añadir, renombrar, reordenar, marcar privada, eliminar |
| El bloque `head` de Loomis | Biblioteca de paletas: guarda una zona e impórtala en otro proyecto |
| JSON, `.gpl`, impresión y Export/Import | Varios ambientes por proyecto, con uno activo |
| Español/inglés y traducciones propias | La ficha y la impresión se adaptan al tipo de proyecto |

Eliminar una zona en el editor nuevo no borra sus colores: la paleta se conserva como extra oculta. Por eso no desaparece nada durante la actualización.
