# What is the Ascender Framework?

The Ascender Framework is a modern Python API framework maintained by the Ascender Team for building scalable, maintainable, and efficient backend applications. It is built **on top of FastAPI** — so you keep FastAPI's performance, async support, and OpenAPI generation — and adds the structure that large applications need: dependency injection, modules, controllers, and guards, inspired by Angular and NestJS but tailored for Python.

## A taste of Ascender

```python title="src/users/users_controller.py"
from ascender.core import Controller, Get, Post
from .users_service import UsersService
from .users_dto import UserDTO


@Controller(standalone=True, providers=[UsersService], tags=["users"])
class UsersController:
    def __init__(self, users: UsersService):  # injected automatically
        self.users = users

    @Get()
    async def list_users(self):
        return await self.users.all()

    @Post(response_model=UserDTO, status_code=201)
    async def create_user(self, data: UserDTO):
        return await self.users.create(data)
```

One CLI command scaffolds it for you:

```bash
ascender g controller users/users
```

## Core principles

<div class="grid cards" markdown>

-   :material-view-module:{ .lg .middle } __Class-Based Architecture__

    ---

    Clear separation of modules, services, and controllers following the Single Responsibility Principle.

-   :material-graph:{ .lg .middle } __Dependency Injection__

    ---

    A hierarchical, Angular-style DI system built into the framework — clean, testable code with constructor injection.

-   :material-package-variant-closed:{ .lg .middle } __Modularity__

    ---

    Encapsulation through modules that export only what other parts of the app should see.

-   :material-rocket-launch:{ .lg .middle } __Performance-Oriented__

    ---

    Built on FastAPI and optimized for Python 3.11+ with modern language features and minimal runtime overhead.

-   :material-console:{ .lg .middle } __Batteries-Included CLI__

    ---

    Scaffold controllers, services, modules, and guards with `ascender g` — and ship your own commands with the CLI engine.

-   :material-shield-check:{ .lg .middle } __Guards & Validation__

    ---

    Declarative route protection and pydantic-powered DTO validation out of the box.

</div>

## How it relates to FastAPI

Every Ascender endpoint **is** a FastAPI path operation. Anything you know from FastAPI — `Body()`, `Query()`, `Header()`, pydantic models, `Request`, dependency semantics — works unchanged inside controller methods. Ascender adds the architectural layer on top: who provides what, where routes live, and how the pieces are wired together.

## Next steps

- [Install the framework and create your first project](installation.md)
- [Learn the essentials: controllers, DI, and validation](../essentials/controllers.md)
