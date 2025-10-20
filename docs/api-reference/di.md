# Dependency Injection API

The Dependency Injection API provides decorators, functions, and utilities for managing dependencies in your application.

## Core Decorators

### Injectable

::: ascender.common.Injectable
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Injection Functions

### inject()

::: ascender.core.inject
    options:
      show_root_heading: true
      show_source: false

### Inject

::: ascender.core.Inject
    options:
      show_root_heading: true
      show_source: false

## Provider Types

::: ascender.core.Provider
    options:
      show_root_heading: true
      show_source: false

## Injector

::: ascender.core.Injector
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Basic Injectable Service

```python
from ascender.common import Injectable, inject

@Injectable()
class UserService:
    """Service for managing users."""
    
    def __init__(self, db_engine=inject()):
        self.db = db_engine
    
    async def find_by_id(self, user_id: str):
        return await self.db.query("SELECT * FROM users WHERE id = ?", user_id)
```

### Using Different Provider Types

```python
from ascender.core import AscModule, ClassProvider, ValueProvider, FactoryProvider

def create_config():
    return {"api_key": "secret", "timeout": 30}

@AscModule(
    providers=[
        # Class provider
        ClassProvider(provide=UserService, useClass=UserService),
        
        # Value provider
        ValueProvider(provide="API_KEY", useValue="my-api-key"),
        
        # Factory provider
        FactoryProvider(provide="Config", useFactory=create_config),
    ]
)
class AppModule:
    pass
```

### Circular Dependencies

```python
from ascender.common import Injectable, inject
from ascender.core.di import DependencyForwardRef

@Injectable()
class ServiceA:
    def __init__(self, service_b=inject()):
        # Use forward reference to resolve circular dependency
        self.service_b = DependencyForwardRef(lambda: service_b)

@Injectable()
class ServiceB:
    def __init__(self, service_a=inject()):
        self.service_a = service_a
```

## See Also

- [Dependency Injection Guide](../di/guide.md) - Comprehensive DI guide
- [Providers Documentation](../di/dependency-providers.md) - Provider types and usage
- [Injectables](../di/injectables.md) - Creating injectable services
