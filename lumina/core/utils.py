"""
lumina/core/utils.py
--------------------
Shared maths helpers used across simulation modules.

All functions here must be pure (no Qt imports, no side effects).
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# RNG seeding — deterministic seeds for reproducible tests
# ---------------------------------------------------------------------------

def seeded_rng(seed: int = 42) -> np.random.Generator:
    """Return a NumPy random generator with a fixed seed.

    Args:
        seed: Integer seed for reproducibility.

    Returns:
        A numpy Generator instance.
    """
    return np.random.default_rng(seed)


# ---------------------------------------------------------------------------
# Array helpers
# ---------------------------------------------------------------------------

def normalise(arr: NDArray[np.float64]) -> NDArray[np.float64]:
    """Normalise an array to the range [0, 1].

    Args:
        arr: Input array.

    Returns:
        Normalised array. Returns zeros if max == min.
    """
    lo, hi = arr.min(), arr.max()
    if hi == lo:
        return np.zeros_like(arr)
    return (arr - lo) / (hi - lo)


def clamp(
    value: float, low: float, high: float
) -> float:
    """Clamp a scalar value to [low, high].

    Args:
        value: The value to clamp.
        low: Lower bound.
        high: Upper bound.

    Returns:
        Clamped value.
    """
    return max(low, min(high, value))


# ---------------------------------------------------------------------------
# Safe expression evaluator
# ---------------------------------------------------------------------------

# Allowed names in user-entered expressions (Level 2 editable equations).
# This is deliberately restrictive — no builtins, no imports.
_SAFE_NAMES: dict[str, object] = {
    "pi": math.pi,
    "e": math.e,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "tanh": np.tanh,
    "cosh": np.cosh,
    "sinh": np.sinh,
    "arctan": np.arctan,
    "arcsin": np.arcsin,
    "arccos": np.arccos,
}

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class ExpressionError(Exception):
    """Raised when a user-entered expression is invalid or unsafe."""


def _eval_node(
    node: ast.AST,
    variables: dict[str, object],
) -> object:
    """Recursively evaluate an AST node with restricted operations.

    Args:
        node: An AST node from ast.parse.
        variables: Mapping of variable names to their current values.

    Returns:
        The evaluated result (float or ndarray).

    Raises:
        ExpressionError: If the expression contains disallowed constructs.
    """
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, variables)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ExpressionError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Name):
        name = node.id
        if name in variables:
            return variables[name]
        if name in _SAFE_NAMES:
            return _SAFE_NAMES[name]
        raise ExpressionError(f"Unknown variable or function: '{name}'")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ExpressionError(f"Unsupported operator: {op_type.__name__}")
        left = _eval_node(node.left, variables)
        right = _eval_node(node.right, variables)
        return _SAFE_OPS[op_type](left, right)

    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _SAFE_OPS:
            raise ExpressionError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand, variables)
        return _SAFE_OPS[op_type](operand)

    if isinstance(node, ast.Call):
        func = _eval_node(node.func, variables)
        if not callable(func):
            raise ExpressionError(f"'{func}' is not callable")
        args = [_eval_node(arg, variables) for arg in node.args]
        if node.keywords:
            raise ExpressionError("Keyword arguments are not allowed")
        return func(*args)

    raise ExpressionError(f"Unsupported expression node: {type(node).__name__}")


def safe_eval(
    expression: str,
    variables: dict[str, object] | None = None,
) -> object:
    """Safely evaluate a mathematical expression string.

    Supports arithmetic operators (+, -, *, /, **), standard math functions
    (sin, cos, exp, log, sqrt, etc.), and named variables.

    Args:
        expression: The expression string (e.g. "sigma * (y - x)").
        variables: Mapping of variable names to values.

    Returns:
        The evaluated result.

    Raises:
        ExpressionError: If the expression is invalid or contains
            disallowed constructs (imports, attribute access, etc.).
    """
    if variables is None:
        variables = {}
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Invalid syntax: {exc}") from exc
    return _eval_node(tree, variables)


def make_callable(
    expression: str,
    var_names: list[str],
) -> Callable[..., object]:
    """Compile an expression string into a callable function.

    This is used for Level 2 editable equations — the user types an
    expression, and we return a function that accepts the named variables
    as positional arguments.

    Args:
        expression: The expression string (e.g. "sigma * (y - x)").
        var_names: Ordered list of variable names (e.g. ["x", "y", "sigma"]).

    Returns:
        A callable f(*args) that evaluates the expression.

    Raises:
        ExpressionError: If the expression is invalid.

    Example:
        >>> f = make_callable("sigma * (y - x)", ["x", "y", "sigma"])
        >>> f(1.0, 2.0, 10.0)
        10.0
    """
    # Validate by parsing once
    try:
        ast.parse(expression.strip(), mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"Invalid syntax: {exc}") from exc

    def _func(*args: object) -> object:
        if len(args) != len(var_names):
            raise ExpressionError(
                f"Expected {len(var_names)} arguments ({var_names}), got {len(args)}"
            )
        variables = dict(zip(var_names, args))
        return safe_eval(expression, variables)

    return _func
