#!/usr/bin/env python3
"""Test script to check the CLI commands"""

from ascender.core.cli_engine.engine import CLIEngine
from examples.cli_commands import VersionCommand, BuildCommand, GenerateCommand, DatabaseCommand

# Create engine with all commands
engine = CLIEngine(commands=[
    VersionCommand(),
    BuildCommand(),
    GenerateCommand(),
    DatabaseCommand()
])

print("=" * 60)
print("Test 1: ascender generate")
print("=" * 60)
try:
    result = engine.parse_and_execute(["generate"])
    print(f"Result: {result}")
except SystemExit as e:
    print(f"Exited with code: {e.code}")

print("\n" + "=" * 60)
print("Test 2: ascender generate controller MyController")
print("=" * 60)
try:
    result = engine.parse_and_execute(["generate", "controller", "MyController"])
    print(f"Result: {result}")
except SystemExit as e:
    print(f"Exited with code: {e.code}")
