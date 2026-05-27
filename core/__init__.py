"""
`core/`

Module of the Fusion 360 add-in FusionkitRibbonAPI, which
allows easy addition and management to a custom ribbon in
the workspace.

The `core/` module contains the registry singleton containing
tabs for the ribbon, classes for creation and management of
buttons and panels.
"""

from registry import registry

from panel import ButtonSpec, FusionkitPanel
from tab import TabManager