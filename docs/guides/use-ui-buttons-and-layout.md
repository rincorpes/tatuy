# Use UI Buttons and Layout

Tatuy UI uses ECS components plus scene resources for resolved layout and pointer interaction.

## Required UI state

A UI-enabled scene uses:

- `UiNode` for hierarchy, size, anchoring, visibility, and enabled state
- `Panel` for panel geometry/presentation
- `Text` from `tatuy.features.visual` for UI text
- `Button` and `ButtonState` for interaction
- `UIFrame` for resolved layout
- `UIInteraction` for pointer capture/activation state
- `UiIntent` for pointer input

Import UI concepts from the public facade:

```python
from tatuy.ui import (
    Button,
    ButtonState,
    Panel,
    UIFrame,
    UIInteraction,
    UiIntent,
    UiNode,
)
```

## Layout

A node with no parent is anchored against the viewport. Child nodes are anchored against the resolved parent box.

```python
UiNode(
    size=Size(180, 56),
    parent=container,
    anchor=(0.5, 0.5),
    offset=Vec2(0, 40),
    z=1,
)
```

Parent visibility/enabled state propagates to children.

## Buttons

A clickable entity combines `UiNode`, `Panel`, `Button`, and `ButtonState`.

`Button.commands` can push fixed engine commands on activation. `UIInteraction.activated` is also available when gameplay needs custom behavior beyond a fixed command binding.

`UiPointerSystem` requires an intent derived from `UiIntent`; using a plain `Intent` is a contract error.

## Rendering

`UiRenderSystem` is separate from world `RenderSystem`. UI reuses the same semantic `RenderQueue`, but UI layout/interaction/rendering remain owned by the UI subsystem.

Examples:

- `examples/fundamentals/020_ui/001_panel_layout/app.py`
- `examples/fundamentals/020_ui/002_text/app.py`
- `examples/fundamentals/020_ui/003_button/app.py`

See also [UI](../learn/ui.md).

---