"""
`core/registry.py`

Central registry of all panels registered by content add-ins.

The registry is a module level singleton so it persists for the
lifetime of the FusionkitRibbonAPI add-in, outliving any
individual content add-in that registers or unregisters panels.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING: from core.panel import FusionkitPanel


class _Registry:
    """Singleton registry mapping panel IDs to FusionkitPanel instances"""
    def __init__(self) -> None:
        self._panels: dict[str, FusionkitPanel] = {}

    def register(self, panel: FusionkitPanel) -> None:
        self._panels[panel.id] = panel

    def unregister(self, panel_id: str) -> FusionkitPanel | None:
        return self._panels.pop(panel_id, None)
    
    def get(self, panel_id: str) -> FusionkitPanel | None:
        return self._panels.get(panel_id)
    
    def all(self) -> list[FusionkitPanel]:
        return list(self._panels.values())
    
    def clear(self) -> None:
        self._panels.clear()


# MODULE LEVEL SINGLETON
registry: _Registry = _Registry()
"""
Module-level singleton registry that contains a map of panel
IDs to FusionkitPanel instances.

### Examples:
    **Registering a panel**:
        >>> registry.register(my_panel)

    **Unregistering a panel**:
        Will return None if no panel in registry has the provided ID.

        >>> unregistered: FusionkitPanel | None = registry.unregister(my_panel.id)

    **Get a specific panel in the registry by ID**:
        >>> my_panel: FusionkitPanel = registry.get(panelID)

    **Get all panels in registry**:
        >>> list_of_panels: list[FusionkitPanel] = registry.all()

    **Clear the registry**:
        >>> registry.clear()
"""