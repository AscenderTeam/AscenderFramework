# Controllers API

The Controllers API provides decorators and utilities for building HTTP endpoints and handling requests.

## Controller Decorator

::: ascender.core.Controller
    options:
      show_root_heading: true
      show_source: false
      members:
        - __init__

## HTTP Method Decorators

::: ascender.core.Get
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.Post
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.Put
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.Patch
    options:
      show_root_heading: true
      show_source: false

::: ascender.core.Delete
    options:
      show_root_heading: true
      show_source: false


::: ascender.core.struct.routes.create_route_decorator
    options:
      show_root_heading: true
      show_source: false

## Example Usage

```python
from ascender.core import Controller, Get, Post, inject
from ascender.common.fastapi_interop import Body

from .services.user_service import UserService

@Controller(standalone=True)
class UserController:
    """User management endpoints."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    @Get("{id}")
    async def get_user(self, id: str):
        """Get a user by ID."""
        return await self.user_service.find_by_id(id)

    @Get("/")
    async def list_users(self, page: int = 1, limit: int = 10):
        """List users with pagination."""
        return await self.user_service.list(page, limit)

    @Post("/")
    async def create_user(self, data: dict = Body(...)):
        """Create a new user."""
        return await self.user_service.create(data)
```

## See Also

- [Controllers Guide](../controllers/overview.md) - Comprehensive guide to using controllers
- [Dependency Injection](di.md) - Using DI in controllers
- [Validation](validation.md) - Request/response validation
