"""Small fail-closed JSON-schema subset used before optional full validators."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .models import ContractError


_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def validate(value: Any, schema: Mapping[str, Any], path: str = "$") -> None:
    expected = schema.get("type")
    if expected is not None:
        py_type = _TYPES.get(expected)
        if py_type is None:
            raise ContractError(f"{path}: unsupported schema type {expected!r}")
        if not isinstance(value, py_type) or expected in {"integer", "number"} and isinstance(value, bool):
            raise ContractError(f"{path}: expected {expected}")
    if "enum" in schema and value not in schema["enum"]:
        raise ContractError(f"{path}: value is not in enum")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            raise ContractError(f"{path}: string is too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            raise ContractError(f"{path}: string is too long")
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            raise ContractError(f"{path}: string does not match pattern")
    if isinstance(value, dict):
        required = schema.get("required", ())
        missing = [name for name in required if name not in value]
        if missing:
            raise ContractError(f"{path}: missing required fields {missing}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(value) - set(properties)
            if unknown:
                raise ContractError(f"{path}: unknown fields {sorted(unknown)}")
        for name, child in value.items():
            if name in properties:
                validate(child, properties[name], f"{path}.{name}")
    if isinstance(value, list) and "items" in schema:
        for index, child in enumerate(value):
            validate(child, schema["items"], f"{path}[{index}]")

