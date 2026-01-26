"""Common helpers for function signature validation.

These helpers are used by the Wizelit MCP wrappers to enforce that tool
functions declare explicit type hints and that incoming arguments match the
expected signature at runtime.
"""

from __future__ import annotations

import inspect
from typing import Any, Dict, Iterable, Mapping, Sequence, get_type_hints

from typeguard import check_type


class SignatureValidationError(TypeError):
    """Raised when a function signature or call arguments are invalid."""


def _clean_excluded(exclude: Iterable[str] | None) -> set[str]:
    return {name for name in (exclude or [])}


def ensure_type_hints(
    func: Any, *, exclude_params: Iterable[str] | None = None
) -> Dict[str, Any]:
    """Ensure a function has type hints for all non-excluded parameters.

    Args:
        func: The target function.
        exclude_params: Parameter names to ignore (e.g., dependency-injected params).

    Returns:
        The resolved type hints for the function.

    Raises:
        SignatureValidationError: If any non-excluded parameter lacks a type hint.
    """

    exclude = _clean_excluded(exclude_params)
    hints = get_type_hints(func, include_extras=True)
    missing = [
        name
        for name, param in inspect.signature(func).parameters.items()
        if name not in exclude and param.kind != inspect.Parameter.VAR_KEYWORD
        and param.kind != inspect.Parameter.VAR_POSITIONAL
        and name not in hints
    ]

    if missing:
        raise SignatureValidationError(
            f"Function {func.__name__} is missing type hints for: {', '.join(missing)}"
        )
    return hints


def bind_and_validate_arguments(
    func: Any,
    args: Sequence[Any],
    kwargs: Mapping[str, Any],
    *,
    exclude_params: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Bind args/kwargs to a function signature and validate types.

    This ensures required parameters are present and values match the annotated
    types. Excluded parameters are ignored for both binding and validation.

    Args:
        func: The target function.
        args: Positional arguments.
        kwargs: Keyword arguments.
        exclude_params: Parameter names to ignore during validation.

    Returns:
        A dictionary of bound arguments suitable for calling ``func``.

    Raises:
        SignatureValidationError: If required parameters are missing or types mismatch.
    """

    exclude = _clean_excluded(exclude_params)
    sig = inspect.signature(func)

    # Drop excluded parameters from the signature for binding
    filtered_params = [
        param
        for name, param in sig.parameters.items()
        if name not in exclude
    ]
    filtered_sig = sig.replace(parameters=filtered_params)

    try:
        bound = filtered_sig.bind(*args, **kwargs)
        bound.apply_defaults()
    except TypeError as exc:
        raise SignatureValidationError(
            f"Invalid arguments for {func.__name__}: {exc}"
        ) from exc

    hints = get_type_hints(func, include_extras=True)
    for name, value in bound.arguments.items():
        if name in exclude:
            continue
        expected = hints.get(name)
        if expected is None:
            continue
        try:
            check_type(name, value, expected)
        except TypeError as exc:
            raise SignatureValidationError(
                f"Argument '{name}' to {func.__name__} must be {expected}, got {type(value)}"
            ) from exc

    return bound.arguments
