"""
ascender.core.cli_engine package initializer

Expose convenient top-level imports for the CLI engine so documentation and
external imports can use `from ascender.core.cli_engine import ...` and the
package is a proper Python package (contains a real __init__.py).
"""
from __future__ import annotations

# Core engine
from ascender.core.cli_engine.engine import CLIEngine

# CLI protos
from ascender.core.cli_engine.protos.basic_cli import BasicCLI
from ascender.core.cli_engine.protos.generic_cli import GenericCLI

# Decorators
from ascender.core.cli_engine.decorators.command import Command
from ascender.core.cli_engine.decorators.handler import Handler

# Provider
from ascender.core.cli_engine.provider import useCLI

# Common parameter types (convenience)
from ascender.core.cli_engine.parameters.parameter import Parameter
from ascender.core.cli_engine.parameters.boolean import BooleanParameter
from ascender.core.cli_engine.parameters.const import ConstantParameter

__all__ = [
    "CLIEngine",
    "BasicCLI",
    "GenericCLI",
    "Command",
    "Handler",
    "useCLI",
    "Parameter",
    "BooleanParameter",
    "ConstantParameter",
]
