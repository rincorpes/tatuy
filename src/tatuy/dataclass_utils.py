from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import (
    Any,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

T = TypeVar("T")


def dataclass_from_dict(
    cls: type[T],
    data: Mapping[str, Any],
) -> T:
    return _decode(data, cls, cls.__name__)


def _decode(value: Any, annotation: Any, path: str) -> Any:
    if annotation is Any:
        return value

    origin = get_origin(annotation)
    args = get_args(annotation)

    # Handles Optional[T], T | None, and other unions.
    if origin in (Union, UnionType):
        for candidate in args:
            try:
                return _decode(value, candidate, path)
            except (TypeError, ValueError):
                pass

        raise ValueError(
            f"{path}: expected {annotation!r}, got {value!r}"
        )

    if annotation is type(None):
        if value is None:
            return None
        raise ValueError(f"{path}: expected None")

    if isinstance(annotation, type) and issubclass(annotation, Enum):
        try:
            return annotation(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"{path}: invalid {annotation.__name__}"
            ) from exc

    # Construct nested dataclasses using their declared field types.
    if isinstance(annotation, type) and is_dataclass(annotation):
        if isinstance(value, annotation):
            return value

        if not isinstance(value, Mapping):
            raise TypeError(f"{path}: expected a dictionary")

        init_fields = {
            field.name: field
            for field in fields(annotation)
            if field.init
        }

        unknown = value.keys() - init_fields.keys()

        if unknown:
            raise ValueError(
                f"{path}: unknown fields {unknown!r}"
            )

        # Resolves annotations declared with:
        # from __future__ import annotations
        hints = get_type_hints(annotation)

        kwargs = {
            name: _decode(
                item,
                hints[name],
                f"{path}.{name}",
            )
            for name, item in value.items()
        }

        # Omitted fields retain their defaults/default factories.
        return annotation(**kwargs)

    if origin in (list, tuple):
        if not isinstance(value, (list, tuple)):
            raise TypeError(f"{path}: expected a list or tuple")

        if origin is list:
            item_types = [args[0] if args else Any] * len(value)

        elif len(args) == 2 and args[1] is Ellipsis:
            # tuple[SomeType, ...]
            item_types = [args[0]] * len(value)

        elif not args:
            item_types = [Any] * len(value)

        else:
            # Fixed tuples such as tuple[str, int].
            if len(value) != len(args):
                raise ValueError(
                    f"{path}: expected {len(args)} items"
                )

            item_types = args

        items = [
            _decode(item, item_type, f"{path}[{index}]")
            for index, (item, item_type) in enumerate(
                zip(value, item_types)
            )
        ]

        return tuple(items) if origin is tuple else items

    if origin is dict:
        if not isinstance(value, Mapping):
            raise TypeError(f"{path}: expected a dictionary")

        key_type, item_type = args or (Any, Any)

        return {
            _decode(key, key_type, f"{path}.<key>"):
            _decode(item, item_type, f"{path}[{key!r}]")
            for key, item in value.items()
        }

    # Accept integer configuration values for float fields.
    if annotation is float and type(value) in (int, float):
        return float(value)

    if annotation in (str, int, bool, float):
        if type(value) is annotation:
            return value

        raise TypeError(
            f"{path}: expected {annotation.__name__}"
        )

    raise TypeError(
        f"{path}: unsupported annotation {annotation!r}"
    )