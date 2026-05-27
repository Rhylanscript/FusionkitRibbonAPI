# FusionkitRibbonAPI

A Fusion 360 add-in that provides a shared **Fusionkit** ribbon tab that allows other add-ins to register panels and buttons into it.

Content add-ins never touch Fusion's ribbon or event system directly, they simply import this API and describe what they want.

Example of an add-in hooking into Fusion 360 UI through the API:
![Fusion360DiscordRPC using FusionkitRibbonAPI to modify Fusion UI][preview]

## Installation

1. Copy the `FusionkitRibbonAPI` folder into Fusion 360's add-ins directory:

    | OS      | Path                                                                     |
    | ------- | ------------------------------------------------------------------------ |
    | Windows | `%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\`                     |
    | macOS   | `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/` |

2. Open Fusion and press `Shift+S` to go to the **Add-Ins** tab
3. Find **FusionkitRibbonAPI** and enable **Run on Startup**. This ensures the API is always loaded before any content add-in that depends on it

## Usage in a content add-in

```python
import sys
import os

# FusionkitRibbonAPI adds itself to sys.path on startup,
# so this import works from any add-in.
import FusionkitRibbonAPI as fusionkit

# run() and stop() are necessary, or should be used in 
# nearly all cases.

def run(context):
    panel = fusionkit.register_panel("my_panel_id", "My Panel")

    panel.add_button(
        id         = "my_button",
        name       = "Do Something",
        tooltip    = "Does something useful.",
        icon_path  = "/absolute/path/to/icon/folder",
        on_execute = on_my_button_click,
        promoted   = True,   # show outside the panel flyout (leave empty for False)
    )

def stop(context):
    fusionkit.unregister_panel("my_panel_id")

def on_my_button():
    print("button clicked!")
```

### Updating a button after its creation

```python
panel.update_button("my_button", name="New Label", tooltip="New tooltip.")
```

### Graceful degradation (recommended but not necessary)

If your addin should work even without the API installed, use a fallback:

```python
try:
    import FusionkitRibbonAPI as fusionkit
    HAS_FUSIONKIT = True
except ImportError:
    HAS_FUSIONKIT = False

def run(context):
    if HAS_FUSIONKIT:
        _setup_ribbon()
    else:
        ui.messageBox(
            "FusionkitRibbonAPI is not installed.\n"
            "Ribbon controls will not be available.\n"
            "Install it from: https://github.com/rhylanscript/FusionkitRibbonAPI",
            "Fusionkit"
        )
```

## API Guide

### `fusionkit.__version__`

Version string, use for compatibility checks.

### `fusionkit.register_panel(panel_id, panel_name) -> FusionkitPanel`

Creates a panel in the Fusionkit tab. Idempotent - safe to call on every `run()`.

### `fusionkit.unregister_panel(panel_id)`

Removes the panel and all its controls, while the Fusionkit tab remains.

### `FusionkitPanel.add_button(id, name, tooltip, icon_path, on_execute, promoted=False)`

Adds a button to the panel. `on_execute` is a plain python callable with no arguments.

### `FusionkitPanel.update_button(id, name=None, tooltip=None)`

Updates a buttons label or tooltip after creation. Pass only the fields you want to change.

## Icon format

Fusion expects icon folders containing:

```text
my_icon/
├── 16x16.png
├── 32x32.png
└── 16x16@2x.png
```

Pass the folder path (**NOT** a file path) to `icon_path`.

## Version history

See [changelog][changelog] for full details of version changes!

<!-- REFERENCE LINKS -->
<!-- [repo]: https://github.com/rhylanscript/FusionkitRibbonAPI -->

<!-- FILE LINKS -->
[changelog]: CHANGELOG.md
[preview]: resources/preview.png
