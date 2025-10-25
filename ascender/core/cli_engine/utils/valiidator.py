# 🧩 Step 1: unwrap Annotated to extract *real* type (ignoring Parameter)
import asyncio
from typing import Annotated, get_args, get_origin

from pydantic import TypeAdapter
from ascender.core.cli_engine.types.parameter import ParameterInfo

import inspect


def unwrap_annotation(annotation):
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        # first non-Parameter argument is your real type
        for arg in args:
            if not isinstance(arg, ParameterInfo):
                return arg
        return str  # fallback
    return annotation or str


# 🧩 Step 2: parse using Pydantic’s engine
def parse_value(value, annotation):
    base_type = unwrap_annotation(annotation)
    adapter = TypeAdapter(base_type)
    return adapter.validate_python(value)


# 🧩 Step 3: class-based attribute setter
def set_parsed_attr(command_instance, key: str, value):
    hints = getattr(command_instance.__class__, '__annotations__', {})
    annotation = hints.get(key, str)
    parsed_value = parse_value(value, annotation)
    setattr(command_instance, key, parsed_value)
    return parsed_value


# 🧩 Step 4: function-based parser (sync + async)
def call_parsed_method(method, subcommand_args: dict):
    sig = inspect.signature(method)
    parsed_kwargs = {}

    for key, param in sig.parameters.items():
        if key not in subcommand_args:
            continue

        value = subcommand_args[key]
        annotation = (
            param.annotation if param.annotation != inspect._empty else str
        )

        parsed_kwargs[key] = parse_value(value, annotation)

    if inspect.iscoroutinefunction(method):
        return asyncio.run(method(**parsed_kwargs))

    return method(**parsed_kwargs)