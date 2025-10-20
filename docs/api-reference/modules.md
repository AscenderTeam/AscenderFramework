# Modules API

The Modules API provides decorators and utilities for organizing your application into modular components.

## Module Decorator

::: ascender.core.struct.module.AscModule
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Basic Module

```python
from ascender.core import AscModule
from ascender.common import Injectable

@Injectable()
class UserService:
    pass

@Injectable()
class UserRepository:
    pass

@AscModule(
    providers=[UserService, UserRepository],
    Declarations=[],
    imports=[],
    exports=[UserService]
)
class UserModule:
    """User management module."""
    pass
```

### Module with Imports

```python
from ascender.core import AscModule
from .database_module import DatabaseModule
from .auth_module import AuthModule

@AscModule(
    imports=[
        DatabaseModule,  # Import database functionality
        AuthModule,      # Import authentication
    ],
    providers=[UserService],
    Declarations=[UserController],
    exports=[UserService]  # Export for other modules to use
)
class UserModule:
    """User module with dependencies."""
    pass
```

### Root Application Module

```python
from ascender.core import AscModule
from .user.user_module import UserModule
from .product.product_module import ProductModule
from .auth.auth_module import AuthModule

@AscModule(
    imports=[
        AuthModule,
        UserModule,
        ProductModule,
    ],
    providers=[],
    Declarations=[],
)
class AppModule:
    """Root application module."""
    pass
```

### Module with Custom Providers

```python
from ascender.core import AscModule

def create_cache_client():
    from redis import Redis
    return Redis(host='localhost', port=6379)

@AscModule(
    providers=[
        # Class provider
        {
            "provide": UserService,
            "use_class": UserService
        },

        # Factory provider
        {
            "provide": 'CacheClient',
            "use_factory": create_cache_client
        },

        # Value provider
        {
            "provide": 'API_VERSION',
            "value": 'v1'
        },
    ],
    Declarations=[UserController],
)
class UserModule:
    """User module with custom providers."""
    pass
```

### Dynamic Module Configuration

```python
from ascender.core import AscModule

class ConfigModule:
    """Dynamic configuration module."""
    
    @staticmethod
    def forRoot(config: dict):
        """Create module with configuration."""
        return AscModule(
            providers=[
                ValueProvider(provide='Config', useValue=config),
            ],
            exports=['Config']
        )(ConfigModule)

# Usage
@AscModule(
    imports=[
        ConfigModule.forRoot({
            'database_url': 'postgresql://localhost/mydb',
            'api_key': 'secret-key'
        })
    ]
)
class AppModule:
    pass
```

## Module Features

### Providers
Define services and dependencies that should be instantiated within the module.

### Declarations
List of Declarations (Controllers or Guards) that belong to this module and handle HTTP requests or any other hooks if defined.

### Imports
Other modules whose exported providers should be available in this module.

### Exports
Providers that should be available to modules that import this module.

## See Also

- [Module Documentation](../modules/overview.md) - Comprehensive module guide
- [Dependency Injection](di.md) - DI system used by modules
- [Application](application.md) - Creating applications from modules
