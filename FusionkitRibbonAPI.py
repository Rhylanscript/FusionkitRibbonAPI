"""
`FusionkitRibbonAPI.py`

Fusionkit Ribbon API - entrypoint and public interface.

This add-in must be loaded before any content add-in that uses
it. Set `runOnStartup: true` in the manifest to ensure this.

Public API (import from content add-ins):
----------------------------------------------
```python
import FusionkitRibbonAPI as fusionkit

panel = fusionkit.register_panel("my_panel_id", "My Panel")

panel.add_button(
    id          = "my_button",
    name        = "Do Something",
    tooltip     = "Does something useful.",
    icon_path   = "path/to/icons",
    on_execute  = my_callable,
    promoted    = True,
)

panel.update_button("my_button", name="New Label")

fusionkit.unregister_panel("my_panel_id")
```
----------------------------------------------
"""

__version__ = "0.1.0"

import sys
import os

# Register this module instance under its public name immediately so
# `import FusionkitRibbonAPI` in content add-ins always resolves to
# this same object regardless of how Fusion named it internally
sys.modules["FusionkitRibbonAPI"] = sys.modules[__name__]

# Add this files dir to sys.path so content add-ins can
# import this module regardless of their own location.
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path: sys.path.insert(0, _here)

import adsk.core
import adsk.fusion

from core.tab import TabManager
from core.panel import ButtonSpec, FusionkitPanel
from core.registry import registry

# --------------------------------------------
#       MODULE STATE
# --------------------------------------------

_ui = None
_tab_manager = None

# --------------------------------------------
#       ADD-IN LIFECYCLE
# --------------------------------------------

def run(context) -> None:
    global _ui, _tab_manager

    app = adsk.core.Application.get()
    _ui = app.userInterface

    _tab_manager = TabManager(_ui)
    _tab_manager.setup()

    print(f"[FusionkitRibbonAPI] v{__version__} loaded.")


def stop(context) -> None:
    global _ui, _tab_manager

    for panel in registry.all(): panel.remove()
    registry.clear()

    if _tab_manager:
        _tab_manager.teardown()
        _tab_manager = None

    _ui = None

# --------------------------------------------
#       PUBLIC API
# --------------------------------------------

def register_panel(panel_id: str, panel_name: str) -> FusionkitPanel:
    """
    Register a new panel in the FusionKit tab.
 
    Idempotent - if a panel with this ID already exists it is
    returned as is so content add-ins can safely call this in
    every `run()` without duplicating panels.
 
    Args:
        panel_id: Unique identifier for this panel (e.g. "discord_rpc").
        panel_name: Display name shown in the ribbon (e.g. "Discord RPC").
 
    Returns:
        A FusionKitPanel instance. Call `.add_button()` on it.
 
    Raises:
        RuntimeError: If FusionKitRibbonAPI hasn't been loaded yet.
    """
    if _tab_manager is None or _tab_manager.tab is None:
        raise RuntimeError(
            "FusionkitRibbonAPI is not loaded. "
            "Make sure it is installed and set to run on startup."
        )
    
    # return existing panel if already registered
    existing = registry.get(panel_id)
    if existing: return existing

    # create the toolbar panel inside the fusionkit tab
    full_panel_id = f"fusionkit_{panel_id}_panel"
    toolbar_panel = _tab_manager.tab.toolbarPanels.itemById(full_panel_id)
    if not toolbar_panel: 
        toolbar_panel = _tab_manager.tab.toolbarPanels.add(full_panel_id, panel_name)

    panel = FusionkitPanel(panel_id, panel_name, _ui, toolbar_panel) # type: ignore
    registry.register(panel)
    return panel


def unregister_panel(panel_id: str) -> None:
    """
    Remove a panel and all its controls from the Fusionkit tab.
 
    The Fusionkit tab itself remains. Safe to call even if the
    panel was never registered.
 
    Args:
        panel_id: The same ID passed to `register_panel()`.
    """
    panel = registry.unregister(panel_id)
    if panel: panel.remove()