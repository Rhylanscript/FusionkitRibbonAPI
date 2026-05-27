# core/

The internal implementation of the Fusionkit Ribbon API. Content add-ins should never import from this package directly - use the public API exposed by `FusionkitRibbonAPI.py` instead.

## Modules

### `tab.py` - `TabManager`

Owns the Fusionkit toolbar tab in the Design workspace. Creates it on `setup()` and deletes it (and everything inside) on `teardown()`. Only 1 instance exists, held by the main entrypoint.

### `panel.py` - `FusionkitPanel`

Represents a panel registered by a content add-in. Handles all Fusion event system boilerplate internally, `add_button()` accepts a plain python Callable and wires up the full `CommandCreated -> Execute` handler chain. Both handler objects are kept alive on `self` to prevent garbage collection between clicks.

### `registry.py` - `registry`

Module level singleton (`_Registry` instance) that maps panel IDs to `FusionkitPanel` objects. Perists for the lifetime of the API addin, outliving ang individual content add-in that registers or unregisters panels.

## Adding new Control Types

To add a new control type (e.g. a dropdown or checkbox alternative):

1. Add a new `SpecType` dataclass and `_create_*` method to `panel.py`
2. Add a corresponding `add_*` method to `FusionkitPanel`
3. Expose it through `FusionkitRibbonAPI.py` if required
4. Keep handler objs in `self._handlers` to prevent garbage collection
