"""
`core/panel.py`

Panel and button abstractions for Fusionkit ribbon API.

Content add-ins never touch Fusion's event system directly,
instead `FusionkitPanel.addButton()` accepts a plain Python
callable and this module handles all CommandCreated ->
Execute handler wiring.
"""

from __future__ import annotations
from typing import Callable
from dataclasses import dataclass, field

import adsk.core


@dataclass
class ButtonSpec:
    """
    Data describing a button to be created on a panel.
    
    Attributes:
        id (str): Button ID
        name (str): Display name of button
        tooltip (str): Tooltip text (text shown on hover)
        icon_path (str): Path to the icon for the button

        on_execute (Callable[[], None]): The function to be executed on click
        promoted (bool): Boolean deciding whether the button is promoted to tab by default
    """
    id: str
    name: str
    tooltip: str
    icon_path: str
    on_execute: Callable[[], None]
    promoted: bool

class FusionkitPanel:
    """
    Represents a panel registered by a content add-in.

    Example:
        >>> panel = FusionkitPanel("discord_rpc", "Discord RPC", ui, toolbar_panel)

        >>> panel.add_button(id="toggle", name="...", ..., on_execute=my_function)
        >>> panel.remove()    # removes panel controls; tab stays 
    """

    def __init__(
        self,
        id: str,
        name: str,
        ui: adsk.core.UserInterface,
        toolbar_panel: adsk.core.ToolbarPanel
    ) -> None:
        """
        Represents a panel registered by a content add-in.

        Args:
            id (str): Unique identifier of panel
            name (str): Label shown on ribbon
            ui (adsk.core.UserInterface): The UI instance to refer to
            toolbar_panel (adsk.core.ToolbarPanel): The ToolBarPanel instance to refer to

        Example:
            >>> panel = FusionkitPanel("discord_rpc", "Discord RPC", ui, toolbar_panel)
            >>> panel.add_button(id="toggle", name="...", ..., on_execute=my_function)

            >>> panel.remove()    # removes panel controls but tab stays
        """
        
        self.id = id
        self.name = name

        self._ui = ui
        self._toolbar_panel = toolbar_panel

        self._button_specs: list[ButtonSpec] = []
        self._cmd_defs: list[adsk.core.CommandDefinition] = []
        self._handlers: list = []

    # -------------------------------------------
    #                PUBLIC API
    # -------------------------------------------

    def add_button(
        self,
        id: str,
        name: str,
        tooltip: str,
        icon_path: str,
        on_execute: Callable[[], None],
        promoted: bool = False,
    ) -> None:
        """
        Add a button to the panel.

        Args:
            id (str): Unique identifier (scope of panel)
            name (str): Label shown in the ribbon
            tooltip (str): Hover text
            icon_path (str): Absolute path to icon folder (containing 16x16.png etc.)

            on_execute (Callable[[], None]): Plain callable to be run when button is clicked
            promoted (bool): If true, shows the button outside the panel flyout
        """

        spec = ButtonSpec(
            id=f"fusionkit_{self.id}_{id}",
            name=name,
            tooltip=tooltip,
            icon_path=icon_path,
            on_execute=on_execute,
            promoted=promoted,
        )

        self._button_specs.append(spec)
        self._create_button(spec)

    def update_button(
        self, 
        id: str, 
        name: str | None = None,
        tooltip: str | None = None,
    ) -> None:
        """
        Update a buttons label or tooltip after creation by using
        it's `id` property.

        Args:
            id (str): The unique identifier of the button
            name (str): New label or None to keep the same
            tooltip (str): New tooltip text or None to keep the same
        """
        full_id = f"fusionkit_{self.id}_{id}"
        cmd_def = self._ui.commandDefinitions.itemById(full_id)
        if not cmd_def: return

        if name is not None: cmd_def.name = name
        if tooltip is not None: cmd_def.tooltip = tooltip

    def remove(self) -> None:
        """
        Remove all controls and command definitions for this panel.
        The toolbar panel itself is also deleted however the tab
        will remain.
        """
        self._handlers.clear()
        
        for cmd_def in self._cmd_defs:
            try:
                cmd_def.deleteMe()
            except Exception:...

        self._cmd_defs.clear()

        try:
            self._toolbar_panel.deleteMe()
        except Exception:...

    # -------------------------------------------
    #                  INTERNAL
    # -------------------------------------------

    def _create_button(self, spec: ButtonSpec) -> None:
        # clean any stale defs from prior runs
        existing = self._ui.commandDefinitions.itemById(spec.id)
        if existing:
            try:
                existing.deleteMe()
            except Exception:...

        cmd_def = self._ui.commandDefinitions.addButtonDefinition(
            spec.id,
            spec.name,
            spec.tooltip,
            spec.icon_path,
        )
        self._cmd_defs.append(cmd_def)

        # wire commandCreated
        created_handler = _ButtonCreatedHandler(spec.on_execute, self._handlers)
        cmd_def.commandCreated.add(created_handler)
        self._handlers.append(created_handler)

        control = self._toolbar_panel.controls.addCommand(cmd_def)
        if spec.promoted: control.isPromotedByDefault = True

# -------------------------------------------
#       INTERNAL FUSION EVENT HANDLERS
# -------------------------------------------

class _ButtonCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(
        self,
        on_execute: Callable[[], None],
        handler_store: list,
    ) -> None:
        super().__init__()

        self._on_execute = on_execute
        self._handler_store = handler_store

        self._execute_handler: adsk.core.CommandEventHandler | None = None

    def notify(self, args: adsk.core.CommandCreatedEventArgs) -> None:
        self._execute_handler = _ButtonExecuteHandler(self._on_execute)
        args.command.execute.add(self._execute_handler)
        self._handler_store.append(self._execute_handler)

class _ButtonExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self, on_execute: Callable[[], None]) -> None:
        super().__init__()
        self._on_execute = on_execute

    def notify(self, args: adsk.core.CommandEventArgs) -> None:
        try:
            self._on_execute()
        except Exception as e:
            print(f"[FusionkitRibbonAPI] button execute error: {str(e)}")