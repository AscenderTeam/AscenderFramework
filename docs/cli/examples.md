# CLI Examples

This section provides comprehensive examples of CLI commands for common use cases in web application development.

## BasicCLI Examples

### Version Command

A simple command to display version information:

```python
from typing import Any
from ascender.core.cli_engine import Command, BasicCLI, Parameter

@Command(name="version", description="Display framework version information")
class VersionCommand(BasicCLI):
    """Display version and build information."""
    
    verbose: bool = Parameter(
        False,
        description="Show detailed version information",
        names=["--verbose", "-v"]
    )
    
    json_format: bool = Parameter(
        False,
        description="Output in JSON format",
        names=["--json", "--json-format"]
    )
    
    def execute(self) -> None:
        """Display version information."""
        version_info = {
            "version": "1.0.0",
            "build": "2024.10.18",
            "python": "3.11+",
            "author": "Ascender Team"
        }
        
        if self.json_format:
            import json
            print(json.dumps(version_info, indent=2))
        elif self.verbose:
            print("Ascender Framework")
            print("-" * 20)
            for key, value in version_info.items():
                print(f"{key.capitalize()}: {value}")
        else:
            print(f"Ascender Framework v{version_info['version']}")
```

**Usage**:
```bash
ascender version
ascender version --verbose
ascender version --json-format
```

### Build Command

A build command with multiple options:

```python
from ascender.core.cli_engine import Command, BasicCLI, Parameter

@Command(name="build", description="Build the application for deployment")
class BuildCommand(BasicCLI):
    """Build and optimize the application."""
    
    production: bool = Parameter(
        False,
        description="Enable production optimizations",
        names=["--production", "--prod"]
    )
    
    output: str = Parameter(
        "dist",
        description="Output directory for built files",
        names=["--output", "-o"]
    )
    
    minify: bool = Parameter(
        True,
        description="Minify the output files",
        names=["--minify/--no-minify"]
    )
    
    source_maps: bool = Parameter(
        False,
        description="Generate source maps",
        names=["--source-maps", "--maps"]
    )
    
    watch: bool = Parameter(
        False,
        description="Watch for file changes and rebuild",
        names=["--watch", "-w"]
    )
    
    def execute(self) -> None:
        """Build the application."""
        print("Starting build process...")
        
        # Build configuration
        config = {
            "mode": "production" if self.production else "development",
            "output_dir": self.output,
            "minify": self.minify and self.production,
            "source_maps": self.source_maps,
            "watch": self.watch
        }
        
        print(f"Build mode: {config['mode']}")
        print(f"Output directory: {config['output_dir']}")
        
        if config["minify"]:
            print("Minification: enabled")
        
        if config["source_maps"]:
            print("Source maps: enabled")
        
        # Simulated build process
        import time
        print("Compiling TypeScript...")
        time.sleep(1)
        
        print("Bundling assets...")
        time.sleep(1)
        
        if config["minify"]:
            print("Minifying files...")
            time.sleep(0.5)
        
        if self.watch:
            print("Starting watch mode...")
            print("Press Ctrl+C to stop watching")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nWatch mode stopped")
        else:
            print("Build completed successfully!")
```

**Usage**:
```bash
ascender build
ascender build --production --output build
ascender build --watch --source-maps
```

## GenericCLI Examples

### Generate Command

A comprehensive code generation command group:

```python
import os
from pathlib import Path
from typing import Any
from ascender.core.cli_engine import Command, Handler, GenericCLI, Parameter

@Command(name="generate", description="Generate application components")
class GenerateCommand(GenericCLI):
    """Code generation utilities for rapid development."""
    
    @Handler("controller", description="Generate a new controller")
    def controller(self,
                  name: str,
                  path: str = "src/controllers",
                  crud: bool = False,
                  api: bool = False,
                  **kwargs: Any) -> None:
        """
        Generate a new controller.
        
        Args:
            name: Controller name (without 'Controller' suffix)
            path: Output path for the controller file
            crud: Generate CRUD operations
            api: Generate API endpoints
        """
        controller_name = f"{name}Controller"
        file_path = Path(path) / f"{name.lower()}_controller.py"
        
        print(f"Generating controller: {controller_name}")
        print(f"Location: {file_path}")
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate controller content
        content = self._generate_controller_content(
            controller_name, crud, api
        )
        
        # Write file
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Created {file_path}")
        
        if crud:
            print("✓ Added CRUD operations")
        if api:
            print("✓ Added API endpoints")
    
    @Handler("service", description="Generate a new service class")
    def service(self,
               name: str,
               path: str = "src/services", 
               interface: bool = False,
               async_methods: bool = False,
               **kwargs: Any) -> None:
        """
        Generate a new service class.
        
        Args:
            name: Service name (without 'Service' suffix)
            path: Output path for the service file
            interface: Generate interface/protocol
            async_methods: Use async methods
        """
        service_name = f"{name}Service"
        file_path = Path(path) / f"{name.lower()}_service.py"
        
        print(f"Generating service: {service_name}")
        print(f"Location: {file_path}")
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = self._generate_service_content(
            service_name, interface, async_methods
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Created {file_path}")
        
        if interface:
            interface_path = Path(path) / f"{name.lower()}_interface.py"
            interface_content = self._generate_interface_content(service_name)
            with open(interface_path, 'w') as f:
                f.write(interface_content)
            print(f"✓ Created interface {interface_path}")
    
    @Handler("model", description="Generate a new model class")
    def model(self,
             name: str,
             path: str = "src/models",
             database: str = "default",
             fields: str = Parameter(
                 None,
                 description="Comma-separated list of fields (name:type)",
                 names=["--fields", "-f"],
                 metavar="FIELDS"
             ),
             **kwargs: Any) -> None:
        """
        Generate a new model class.
        
        Args:
            name: Model name
            path: Output path for the model file
            database: Database connection name
            fields: Comma-separated list of fields (name:type)
        """
        model_name = f"{name}"
        file_path = Path(path) / f"{name.lower()}.py"
        
        print(f"Generating model: {model_name}")
        print(f"Database: {database}")
        
        # Parse fields if provided
        parsed_fields = []
        if fields:
            for field in fields.split(','):
                if ':' in field:
                    field_name, field_type = field.strip().split(':')
                    parsed_fields.append((field_name.strip(), field_type.strip()))
                else:
                    parsed_fields.append((field.strip(), 'str'))
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        content = self._generate_model_content(
            model_name, database, parsed_fields
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✓ Created {file_path}")
        if parsed_fields:
            print(f"✓ Added {len(parsed_fields)} fields")
    
    @Handler("module", description="Generate a new application module")
    def module(self,
              name: str,
              path: str = "src/modules",
              **kwargs: Any) -> None:
        """
        Generate a new application module.
        
        Args:
            name: Module name
            path: Output path for the module
        """
        module_name = f"{name}Module"
        module_path = Path(path) / name.lower()
        
        print(f"Generating module: {module_name}")
        print(f"Location: {module_path}")
        
        # Create module structure
        module_path.mkdir(parents=True, exist_ok=True)
        
        files = {
            "__init__.py": self._generate_module_init(module_name),
            f"{name.lower()}_module.py": self._generate_module_content(module_name),
            "controllers/__init__.py": "",
            "services/__init__.py": "",
            "models/__init__.py": "",
        }
        
        for file_name, content in files.items():
            file_path = module_path / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✓ Created {file_path}")
    
    # Helper methods for content generation
    def _generate_controller_content(self, name: str, crud: bool, api: bool) -> str:
        """Generate controller class content."""
        imports = [
            "from typing import Any",
            "from ascender.common.http import HttpRequest, HttpResponse",
            "from ascender.core.decorators import Controller, Route"
        ]
        
        if api:
            imports.append("from ascender.common.serializer import JsonResponse")
        
        content = "\n".join(imports) + "\n\n"
        
        content += f"@Controller()\n"
        content += f"class {name}:\n"
        content += f'    """{name.replace("Controller", "")} controller."""\n\n'
        
        if crud:
            crud_methods = [
                ("index", "GET", "/", "List all items"),
                ("show", "GET", "/<int:id>", "Show specific item"),
                ("create", "POST", "/", "Create new item"),
                ("update", "PUT", "/<int:id>", "Update existing item"),
                ("delete", "DELETE", "/<int:id>", "Delete item"),
            ]
            
            for method, http_method, route, description in crud_methods:
                content += f'    @Route("{route}", methods=["{http_method}"])\n'
                content += f"    def {method}(self, request: HttpRequest) -> HttpResponse:\n"
                content += f'        """{description}."""\n'
                if api:
                    content += f'        return JsonResponse({{"message": "{description}"}}) \n'
                else:
                    content += f'        return HttpResponse("{description}")\n'
                content += "\n"
        else:
            content += f'    @Route("/")\n'
            content += f"    def index(self, request: HttpRequest) -> HttpResponse:\n"
            content += f'        """Handle index route."""\n'
            content += f'        return HttpResponse("Hello from {name}!")\n'
        
        return content
    
    def _generate_service_content(self, name: str, interface: bool, async_methods: bool) -> str:
        """Generate service class content."""
        imports = ["from typing import Any, Optional"]
        
        if async_methods:
            imports.append("import asyncio")
        
        if interface:
            imports.append(f"from .{name.lower().replace('service', '')}_interface import I{name}")
        
        content = "\n".join(imports) + "\n\n"
        
        if interface:
            content += f"class {name}(I{name}):\n"
        else:
            content += f"class {name}:\n"
        
        content += f'    """{name.replace("Service", "")} service implementation."""\n\n'
        content += f"    def __init__(self):\n"
        content += f'        """Initialize the service."""\n'
        content += f"        pass\n\n"
        
        # Add sample methods
        method_prefix = "async " if async_methods else ""
        
        content += f"    {method_prefix}def get_all(self) -> list[dict]:\n"
        content += f'        """Get all items."""\n'
        if async_methods:
            content += f"        await asyncio.sleep(0)  # Simulate async operation\n"
        content += f"        return []\n\n"
        
        content += f"    {method_prefix}def get_by_id(self, item_id: int) -> Optional[dict]:\n"
        content += f'        """Get item by ID."""\n'
        if async_methods:
            content += f"        await asyncio.sleep(0)  # Simulate async operation\n"
        content += f"        return None\n"
        
        return content
    
    def _generate_interface_content(self, service_name: str) -> str:
        """Generate interface/protocol content."""
        interface_name = f"I{service_name}"
        content = f"""from typing import Protocol, Optional

class {interface_name}(Protocol):
    \"""Protocol for {service_name}.\"""
    
    def get_all(self) -> list[dict]:
        \"""Get all items.\"""
        ...
    
    def get_by_id(self, item_id: int) -> Optional[dict]:
        \"""Get item by ID.\"""
        ...
"""
        return content
    
    def _generate_model_content(self, name: str, database: str, fields: list) -> str:
        """Generate model class content."""
        content = f"""from typing import Optional
from ascender.core.database import Model

class {name}(Model):
    \"""{name} model.\"""
    
    __tablename__ = '{name.lower()}s'
    __database__ = '{database}'
    
"""
        
        # Add fields
        if fields:
            for field_name, field_type in fields:
                content += f"    {field_name}: {field_type}\n"
        else:
            content += "    # Add your model fields here\n"
            content += "    # Example: name: str\n"
            content += "    # Example: email: Optional[str] = None\n"
        
        content += f"""
    def __str__(self) -> str:
        return f"<{name}(id={{self.id}})>"
"""
        
        return content
    
    def _generate_module_init(self, module_name: str) -> str:
        """Generate module __init__.py content."""
        return f'""""{module_name} - Auto-generated module."""\n'
    
    def _generate_module_content(self, module_name: str) -> str:
        """Generate main module file content."""
        return f"""from ascender.core.modules import Module

class {module_name}(Module):
    \"""{module_name.replace("Module", "")} module.\"""
    
    def configure(self):
        \"""Configure the module.\"""
        # Add your module configuration here
        pass
"""
```

**Usage**:
```bash
# Generate controllers
ascender generate controller User --crud --api
ascender generate controller Product --path src/api/controllers

# Generate services  
ascender generate service User --interface --async-methods
ascender generate service Email --path src/services

# Generate models
ascender generate model User --fields "name:str,email:str,age:int"
ascender generate model Product --database inventory

# Generate modules
ascender generate module Auth --path src/modules
```

### Database Command

Database management command group:

```python
from ascender.core.cli_engine import Command, Handler, GenericCLI, Parameter

@Command(name="database", description="Database management operations")
class DatabaseCommand(GenericCLI):
    """Database utilities for schema and data management."""
    
    @Handler("migrate", description="Run database migrations")
    def migrate(self,
               rollback: bool = False,
               steps: int = Parameter(
                   None,
                   description="Number of migration steps",
                   names=["--steps", "-s"],
                   metavar="N"
               ),
               target: str = Parameter(
                   None,
                   description="Target migration version",
                   names=["--target", "-t"],
                   metavar="VERSION"
               ),
               dry_run: bool = Parameter(
                   False,
                   description="Show what would be done without executing",
                   names=["--dry-run", "--preview"]
               ),
               **kwargs: Any) -> None:
        """
        Run database migrations.
        
        Args:
            rollback: Rollback migrations instead of applying
            steps: Number of migration steps to apply/rollback
            target: Target migration version
            dry_run: Show what would be done without executing
        """
        if dry_run:
            print("DRY RUN MODE - No changes will be made")
        
        if rollback:
            if target:
                print(f"Rolling back to migration: {target}")
            elif steps:
                print(f"Rolling back {steps} migration(s)")
            else:
                print("Rolling back last migration")
            
            if not dry_run:
                # Rollback logic here
                print("✓ Rollback completed")
        else:
            print("Running pending migrations...")
            
            # Simulate migration discovery
            pending_migrations = [
                "001_create_users_table",
                "002_create_posts_table", 
                "003_add_user_roles"
            ]
            
            if steps:
                pending_migrations = pending_migrations[:steps]
            elif target:
                # Find migrations up to target
                try:
                    target_index = next(
                        i for i, m in enumerate(pending_migrations) 
                        if m.startswith(target)
                    )
                    pending_migrations = pending_migrations[:target_index + 1]
                except StopIteration:
                    print(f"Migration {target} not found")
                    return
            
            for migration in pending_migrations:
                print(f"Applying: {migration}")
                if not dry_run:
                    # Migration logic here
                    import time
                    time.sleep(0.5)
            
            if not dry_run:
                print(f"✓ Applied {len(pending_migrations)} migration(s)")
    
    @Handler("seed", description="Seed database with test data")
    def seed(self,
            clear: bool = False,
            file: str = Parameter(
                None,
                description="Specific seed file to run",
                names=["--file", "-f"],
                metavar="FILE"
            ),
            env: str = Parameter(
                "development",
                description="Environment-specific seed data",
                names=["--env", "-e"],
                choices=["development", "testing", "production"]
            ),
            **kwargs: Any) -> None:
        """
        Seed database with test data.
        
        Args:
            clear: Clear existing data before seeding
            file: Specific seed file to run
            env: Environment-specific seed data
        """
        print(f"Seeding database for environment: {env}")
        
        if clear:
            print("Clearing existing data...")
            # Clear logic here
            print("✓ Data cleared")
        
        if file:
            print(f"Running seed file: {file}")
            # File-specific seeding
        else:
            # Default seeding
            seed_files = [
                "users.py",
                "categories.py", 
                "products.py"
            ]
            
            for seed_file in seed_files:
                print(f"Seeding: {seed_file}")
                # Seeding logic here
                import time
                time.sleep(0.3)
        
        print("✓ Database seeded successfully")
    
    @Handler("status", description="Show current migration status")
    def status(self, **kwargs: Any) -> None:
        """Show current migration status."""
        print("Database Migration Status")
        print("=" * 40)
        
        migrations = [
            ("001_create_users_table", "Applied", "2024-10-15 10:30:00"),
            ("002_create_posts_table", "Applied", "2024-10-15 10:31:00"),
            ("003_add_user_roles", "Applied", "2024-10-16 09:15:00"), 
            ("004_add_indexes", "Pending", None),
            ("005_add_categories", "Pending", None),
        ]
        
        for migration, status, applied_at in migrations:
            status_icon = "✓" if status == "Applied" else "✗"
            status_text = f"{status_icon} {migration:<30} {status:<10}"
            if applied_at:
                status_text += f" ({applied_at})"
            print(status_text)
        
        applied_count = sum(1 for _, status, _ in migrations if status == "Applied")
        pending_count = len(migrations) - applied_count
        
        print()
        print(f"Applied: {applied_count}")
        print(f"Pending: {pending_count}")
    
    @Handler("reset", description="Reset database to initial state")
    def reset(self,
             confirm: bool = Parameter(
                 False,
                 description="Skip confirmation prompt",
                 names=["--confirm", "--yes", "-y"]
             ),
             **kwargs: Any) -> None:
        """
        Reset database to initial state.
        
        Args:
            confirm: Skip confirmation prompt
        """
        if not confirm:
            response = input("This will delete all data. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Database reset cancelled")
                return
        
        print("Resetting database...")
        print("1. Dropping all tables...")
        print("2. Running fresh migrations...")
        print("3. Seeding initial data...")
        
        # Reset logic here
        import time
        time.sleep(2)
        
        print("✓ Database reset completed")


## Async Command Examples

The CLI engine supports async command handlers for operations that require asynchronous processing:

```python
import asyncio
from typing import Any
from ascender.core.cli_engine import Command, Handler, GenericCLI, Parameter

@Command(name="deploy", description="Deployment operations")
class DeployCommand(GenericCLI):
    """Async deployment command examples."""
    
    @Handler("upload", description="Upload files to server", is_coroutine=True)
    async def upload(self,
                    source: str,
                    destination: str = Parameter(
                        None,
                        description="Remote destination path",
                        names=["--dest", "-d"],
                        metavar="PATH"
                    ),
                    parallel: int = Parameter(
                        4,
                        description="Number of parallel uploads",
                        names=["--parallel", "-p"],
                        metavar="N"
                    ),
                    **kwargs: Any) -> None:
        """Async file upload with parallel processing."""
        print(f"Uploading {source} to {destination}")
        print(f"Using {parallel} parallel connections")
        
        # Simulate async upload
        tasks = []
        for i in range(parallel):
            task = asyncio.create_task(self._upload_chunk(i))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        print("✓ Upload completed")
    
    @Handler("backup", description="Create remote backup", is_coroutine=True)
    async def backup(self,
                    database: str = "main",
                    compress: bool = True,
                    **kwargs: Any) -> None:
        """Async database backup."""
        print(f"Creating backup of {database} database")
        
        if compress:
            print("Compression enabled")
        
        # Simulate async backup process
        await self._create_backup(database, compress)
        print("✓ Backup created successfully")
    
    async def _upload_chunk(self, chunk_id: int) -> None:
        """Helper method for async upload simulation."""
        await asyncio.sleep(0.5)  # Simulate upload time
        print(f"  Chunk {chunk_id} uploaded")
    
    async def _create_backup(self, database: str, compress: bool) -> None:
        """Helper method for async backup simulation."""
        print("  Connecting to database...")
        await asyncio.sleep(0.3)
        
        print("  Dumping data...")
        await asyncio.sleep(1.0)
        
        if compress:
            print("  Compressing backup...")
            await asyncio.sleep(0.5)
```

**Usage**:
```bash
# Async commands work just like regular commands
ascender deploy upload ./dist --dest /var/www/app --parallel 8
ascender deploy backup --database production --compress
```
