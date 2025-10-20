"""
Test script demonstrating the Ascender Framework CLI Engine with BasicCLI and GenericCLI.

This script shows how to set up and use the CLI engine with both command types.
"""

print("Starting imports...")

try:
    from ascender.core.cli_engine.engine import CLIEngine
    print("✓ CLIEngine imported successfully")
except Exception as e:
    print(f"✗ Failed to import CLIEngine: {e}")
    exit(1)

try:
    from examples.cli_commands import VersionCommand, GenerateCommand, BuildCommand, DatabaseCommand
    print("✓ Example commands imported successfully")
except Exception as e:
    print(f"✗ Failed to import example commands: {e}")
    exit(1)

print("All imports successful!")
print()


def main():
    """Demonstrate the CLI engine usage."""
    
    print("Starting CLI Engine Test...")
    print()
    
    # Create CLI engine
    cli_engine = CLIEngine(
        usage="ascender <command> [options]",
        description="Ascender Framework - Modern Python Web Framework"
    )
    print("CLI Engine created successfully!")
    
    # Register commands
    commands = [
        VersionCommand,      # BasicCLI
        GenerateCommand,     # GenericCLI  
        BuildCommand,        # BasicCLI
        DatabaseCommand,     # GenericCLI
    ]
    print(f"Found {len(commands)} command classes to register")
    
    # Process commands (this sets up the argument parser)
    cli_engine.process_commands(commands)
    print("Commands processed successfully!")
    print()
    
    # Print command information for demonstration
    print("Registered Commands:")
    print("=" * 50)
    
    for command_class in commands:
        command_info = getattr(command_class, "__asc_command__", {})
        name = command_info.get('name', 'Unknown')
        kind = command_info.get('kind', 'Unknown')
        description = command_info.get('description', 'No description')
        
        print(f"Command: {name}")
        print(f"  Type: {kind}")
        print(f"  Description: {description}")
        print(f"  Class: {command_class.__name__}")
        
        if kind == "generic":
            # List subcommands for GenericCLI
            methods = [method for method in dir(command_class) 
                      if not method.startswith('_') and callable(getattr(command_class, method))]
            # Filter out inherited methods that aren't command methods
            command_methods = [m for m in methods if m not in ['__command_info__']]
            if command_methods:
                print(f"  Subcommands: {', '.join(command_methods)}")
        print()
    
    # Example usage patterns
    print("Example Usage Patterns:")
    print("=" * 50)
    print("BasicCLI commands:")
    print("  ascender version")
    print("  ascender version --verbose")
    print("  ascender build --production --output dist")
    print()
    print("GenericCLI commands:")
    print("  ascender generate controller UserController --path src/controllers")
    print("  ascender generate service UserService --interface")
    print("  ascender database migrate")
    print("  ascender database seed --clear")
    print()
    
    # Note: Actual CLI parsing would be done with:
    # cli_engine.parse_and_execute()
    

if __name__ == "__main__":
    main()
