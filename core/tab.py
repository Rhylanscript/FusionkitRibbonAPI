"""
`core/tab.py`

Owns the Fusionkit toolbar tab.

Creates the tab on `setup()`, removes it on `teardown()`. All 
panels registered through the API live inside this tab.
"""

import adsk.core

FUSIONKIT_TAB_ID    = "fusionkit_tab"
FUSIONKIT_TAB_NAME  = "FusionKit"
DESIGN_WORKSPACE    = "FusionSolidEnvironment"


class TabManager:
    """Creates and destroys the Fusionkit tab in the design workspace."""

    def __init__(self, ui: adsk.core.UserInterface) -> None:
        """
        Creates and destroys the Fusionkit tab in the design workspace.
        
        Args:
            ui (adsk.core.UserInterface): The UI instance to refer to
        """
        self._ui = ui
        self._tab: adsk.core.ToolbarTab | None = None

    def setup(self) -> adsk.core.ToolbarTab | None:
        """
        Creates the Fusionkit tab if it doesn't already exist.

        Returns:
            adsk.core.ToolbarTab | None: The tab or None if the design workspace wasn't found
        """
        workspace = self._ui.workspaces.itemById(DESIGN_WORKSPACE)
        if not workspace: 
            print("[FusionkitRibbonAPI] Design workspace not found - tab not created.")
            return None
        
        tab = workspace.toolbarTabs.itemById(FUSIONKIT_TAB_ID)
        if not tab: tab = workspace.toolbarTabs.add(FUSIONKIT_TAB_ID, FUSIONKIT_TAB_NAME)

        self._tab = tab
        return tab
    
    def teardown(self) -> None:
        """Remove the Fusionkit tab and everything in it."""
        if self._tab:
            try:
                self._tab.deleteMe()
            except Exception:...

            self._tab = None

    @property
    def tab(self) -> adsk.core.ToolbarTab | None: 
        """The `adsk.core.ToolbarTab` instance of the Fusionkit API."""
        return self._tab