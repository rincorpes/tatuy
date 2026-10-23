# UI

Tatuy UI is a separate authoring subsystem built on ECS state, resolved layout resources, pointer interaction, and semantic rendering.

## Public UI contract

Use the public facade:

```python
from tatuy.ui import (
    Button,
    ButtonAppearance,
    ButtonState,
    Panel,
    PanelShape,
    UIFrame,
    UIInteraction,
    UiIntent,
    UiNode,
)
```

UI text intentionally reuses `tatuy.features.visual.Text`.

## Layout

`UiNode` describes hierarchy, size, anchor, offset, visibility, enabled state, and z-order.

`UiLayoutSystem` resolves those declarations into `UIFrame`. Child layout derives from the resolved parent box, and parent visibility/enabled state propagates to descendants.

## Pointer interaction

Interactive UI uses an intent derived from `UiIntent`. `UiPointerSystem` reads pointer state and updates `UIInteraction` plus per-button `ButtonState`.

The interaction model tracks concepts such as:

- hovered entity
- pressed/captured entity
- activation on release

A plain `Intent` is not sufficient for pointer UI because it does not provide the UI pointer contract.

## Buttons

A button entity typically combines:

```text
UiNode
Panel
Button
ButtonState
optional Text
```

`ButtonAppearance` can override foreground/background/content for interaction states. Fixed engine commands may be attached to `Button.commands`; custom gameplay may also inspect `UIInteraction.activated`.

## Rendering

`UiRenderSystem` renders resolved UI independently from world `RenderSystem`.

```text
UI components + UIFrame
        ↓
UiRenderSystem
        ↓
RenderQueue(layer="ui")
```

The visual feature does not know UI exists. Both systems merely produce semantic render operations that later share the same render pipeline.

## What is implementation detail?

Normal game code should not depend on UI renderer internals, layout helper implementations, pointer hit-test implementation details, or backend renderer objects.

## Native preservation contract

A native implementation must preserve:

- hierarchy/anchor/offset layout meaning
- inherited visibility and enabled state
- deterministic z-order
- pointer hover/press/capture/activation semantics
- `ButtonAppearance` behavior
- UI render output ordering relative to other render layers

## Examples

- `examples/fundamentals/020_ui/001_panel_layout/app.py`
- `examples/fundamentals/020_ui/002_text/app.py`
- `examples/fundamentals/020_ui/003_button/app.py`

See [Use UI buttons and layout](../guides/use-ui-buttons-and-layout.md).

---