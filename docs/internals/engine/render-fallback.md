# Render Fallback Internals

Tatuy's normal render path is typed semantic data. Python callbacks are an explicit fallback path and must remain isolated from the native-safe data plane.

Canonical architecture: [Render Pipeline](../../architecture/render-pipeline.md).

## Primary source

```text
src/tatuy/graphics/render/
├── commands.py
├── fallback.py
├── queue.py
├── packets.py
└── executor.py

src/tatuy/engine/render/
```

## Typed operations

`DrawOperation` carries a typed `DrawCommand` payload. It must remain backend-agnostic and safe to snapshot/compile without embedding a Python backend object.

If new normal rendering can be represented as semantic data, add a typed command/operation rather than a Python callback.

## Python fallback operations

`PythonRenderOperation` carries `CustomCommand` fallback data.

Fallback callbacks receive `PythonRenderContext`, which intentionally exposes a narrow renderer capability instead of the entire backend/runtime.

The fallback operation still has layer, z, and sequence metadata and therefore participates in the same ordering stream as typed operations.

## Rules for contributors

Do not:

- add `Backend` to `DrawCommand`, `RenderQueue`, or typed packets
- make every new render feature a callback because it is convenient
- reorder fallback separately from typed work
- let fallback callbacks reach unrelated runtime services through the render context
- design a native ABI around per-command Python callbacks

Do:

- prefer typed semantic commands
- keep callback identity intact when compiling fallback work
- preserve mixed typed/fallback ordering
- make unsupported fallback behavior explicit in runtimes that cannot execute Python callbacks
- test packet compilation and executor routing independently

## Native implementations

A native executor should consume typed operations directly. If Python fallback is supported, routing may return to Python only for explicit fallback operations.

A runtime that cannot support Python fallback may reject those operations clearly while continuing to support the typed stream.

The presence of fallback must never force the normal render path to carry Python implementation objects.

---