# Types API

Type definitions and interfaces used throughout the Ascender Framework.

## Provider Types

### Base Provider

```python
from typing import TypedDict, Any, Callable

class Provider(TypedDict, total=False):
    """Base provider type."""
    provide: Any
    multi: bool
```

### Class Provider

```python
class ClassProvider(Provider):
    """Class-based provider."""
    useClass: type
```

### Value Provider

```python
class ValueProvider(Provider):
    """Value-based provider."""
    useValue: Any
```

### Factory Provider

```python
class FactoryProvider(Provider):
    """Factory function provider."""
    useFactory: Callable[..., Any]
    inject: list[Any] | None
```

### Existing Provider

```python
class ExistingProvider(Provider):
    """Alias to existing provider."""
    useExisting: Any
```

## Route Types

### Route Configuration

```python
class RouteConfig(TypedDict):
    """Route configuration."""
    path: str
    method: str
    handler: Callable
    response_model: type | None
    status_code: int
    tags: list[str]
    summary: str | None
    description: str | None
    deprecated: bool
```

### Route Parameter

```python
class RouteParam(TypedDict):
    """Route parameter configuration."""
    name: str
    type: type
    default: Any
    required: bool
    description: str | None
```

## Module Types

### Module Configuration

```python
class ModuleConfig(TypedDict, total=False):
    """Module configuration."""
    providers: list[Provider | type]
    controllers: list[type]
    imports: list[type]
    exports: list[str | type]
```

### Module Metadata

```python
class ModuleMetadata(TypedDict):
    """Module metadata."""
    token: str
    providers: list[Provider]
    controllers: list[type]
    imports: list[str]
    exports: list[str]
```

## Dependency Injection Types

### Injection Token

```python
InjectionToken = str | type
```

### Provider Record

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Callable

T = TypeVar('T')

@dataclass
class ProviderRecord(Generic[T]):
    """Provider record in DI container."""
    value: T
    factory: Callable[[], T] | None
    multi: bool
```

### Forward Reference

```python
class DependencyForwardRef(Generic[T]):
    """Forward reference for circular dependencies."""
    
    def __init__(self, resolver: Callable[[], T]):
        self._resolver = resolver
        self._resolved = False
        self._value: T | None = None
    
    def resolve(self) -> T:
        """Resolve the forward reference."""
        if not self._resolved:
            self._value = self._resolver()
            self._resolved = True
        return self._value
```

## HTTP Types

### HTTP Method

```python
from typing import Literal

HttpMethod = Literal[
    "GET", "POST", "PUT", "PATCH", "DELETE",
    "OPTIONS", "HEAD", "TRACE"
]
```

### Request Context

```python
from starlette.requests import Request
from starlette.responses import Response

HttpRequest = Request
HttpResponse = Response
```

## Middleware Types

### Middleware Function

```python
from typing import Awaitable, Callable
from starlette.requests import Request

Middleware = Callable[[Request, Callable], Awaitable[Response]]
```

### Middleware Configuration

```python
class MiddlewareConfig(TypedDict):
    """Middleware configuration."""
    middleware: type
    options: dict[str, Any]
```

## CLI Types

### Command Configuration

```python
class CommandConfig(TypedDict):
    """CLI command configuration."""
    name: str
    description: str | None
    help: str | None
```

### Handler Configuration

```python
class HandlerConfig(TypedDict):
    """CLI handler configuration."""
    name: str
    description: str | None
    is_coroutine: bool
```

### Parameter Configuration

```python
class ParameterConfig(TypedDict, total=False):
    """CLI parameter configuration."""
    default: Any
    required: bool
    description: str | None
    type: type
    choices: list[Any]
```

## Database Types

### Database Configuration

```python
class DatabaseConfig(TypedDict, total=False):
    """Database configuration."""
    url: str
    echo: bool
    pool_size: int
    max_overflow: int
    pool_timeout: float
    pool_recycle: int
```

## Validation Types

### Field Info

```python
from pydantic.fields import FieldInfo

# Field validation types
StringConstraints = dict[str, Any]  # min_length, max_length, pattern
NumberConstraints = dict[str, Any]  # gt, ge, lt, le, multiple_of
```

## Generic Types

### Success Response

```python
from typing import Generic, TypeVar

T = TypeVar('T')

class SuccessResponse(Generic[T]):
    """Generic success response."""
    success: bool = True
    data: T
    message: str | None = None
```

### Error Response

```python
class ErrorResponse:
    """Error response."""
    success: bool = False
    error: str
    details: dict[str, Any] | None = None
```

### Paginated Response

```python
class PaginatedResponse(Generic[T]):
    """Paginated response."""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int
```

## Example Usage

### Using Provider Types

```python
from ascender.core import AscModule, ClassProvider, ValueProvider, FactoryProvider

def create_config():
    return {"key": "value"}

@AscModule(
    providers=[
        ClassProvider(provide=MyService, useClass=MyService),
        ValueProvider(provide="API_KEY", useValue="secret"),
        FactoryProvider(provide="Config", useFactory=create_config),
    ]
)
class MyModule:
    pass
```

### Using Generic Response Types

```python
from ascender.common import Controller, GET, BaseResponse
from typing import Generic, TypeVar

T = TypeVar('T')

class ApiResponse(BaseResponse, Generic[T]):
    """Generic API response."""
    success: bool
    data: T
    message: str | None = None

@Controller("/api")
class ApiController:
    @GET("/users/:id")
    async def get_user(self, id: str) -> ApiResponse[dict]:
        """Return typed response."""
        user = await self.find_user(id)
        return ApiResponse(
            success=True,
            data=user,
            message="User found"
        )
```

### Type Hints for Injection

```python
from ascender.common import Injectable, inject
from typing import Protocol

class UserRepository(Protocol):
    """User repository interface."""
    async def find_by_id(self, id: str) -> dict: ...
    async def create(self, data: dict) -> dict: ...

@Injectable()
class UserService:
    """User service with typed dependencies."""
    
    def __init__(self, user_repo: UserRepository = inject()):
        self.user_repo = user_repo
```

## See Also

- [Dependency Injection](di.md) - DI system and provider types
- [Controllers](controllers.md) - Route and HTTP types
- [Modules](modules.md) - Module configuration types
- [Python Type Hints](https://docs.python.org/3/library/typing.html) - Official typing documentation
