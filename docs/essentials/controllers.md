# Routing with Controllers

Controllers are the main architectural blocks of the Ascender Framework. They define the final HTTP endpoints—the tips of the router graph's branches. Controllers manage and process incoming requests, returning appropriate responses.

### Sections
1. **Defining a Controller**
2. **Defining Routes of a Controller**
3. **Combining and Composing Controllers with the Router Graph**

---

### Defining a Controller
Each controller in the Ascender Framework contains the following key components:

- A `@Controller` [decorator](https://peps.python.org/pep-0318/) to define the controller class.
- A Python class with endpoint functions that implement the controller's endpoint behavior.
- Methods wrapped with HTTP method decorators, which define the routes and their behavior.


```python title="user_controller.py" linenums="1"
from ascender.core import Controller

@Controller(
    standalone=False
)
class UserController:
    def __init__(self):
        # Initialization logic (e.g., inject services here)
        ...
```

---

### Defining Routes of a Controller
Routes are defined by creating methods inside the controller class and wrapping them with specific HTTP method decorators.


```python title="user_controller.py" hl_lines="10-19" linenums="1"
from ascender.core import Controller, Get

@Controller(
    standalone=False
)
class UserController:
    def __init__(self):
        ...

    @Get()
    async def get_all_users(self) -> list[dict]:
        """
        Defines the root endpoint of this controller (`/users`).
        """
        return [
            {"username": "user1", "email": "user1@example.com"},
            {"username": "user2", "email": "user2@example.com"}
        ]
```
In this example, the `get_all_users` method defines a route using the `@Get()` decorator, making it accessible as the root endpoint of the `UserController`.

---

### Combining and Composing Controllers with the Router Graph
The router graph in the Ascender Framework defines routes to controllers and their endpoints. It organizes the application's routing structure into a graph where specific "Route Nodes" are tied to controllers. These route nodes contain information about the controllers' base path, OpenAPI configurations, and child nodes.

``` mermaid
graph LR
  A[Router Graph] --> |controller| B(MainController);
  A -->|controller| C(UserController);
  C --> |GET: /| D[get_all_users];
```

```python title="routes.py" hl_lines="8-13" linenums="1"
routes: Sequence[RouterRoute] = [
    {
        "path": "/",
        "controller": MainController,
        "tags": ["Main"],
        "include_in_schema": True
    },
    {
        "path": "/users",
        "controller": UserController,
        "tags": ["Users"],
        "include_in_schema": True
    }
]

__all__ = ["routes"]
```

This example demonstrates how to define routes connecting base paths to controllers, with metadata for OpenAPI documentation and schema inclusion.

!!! tip
    Read more about router graph and Ascender Framework routes in [Controllers Overview](../controllers/overview.md)


!!! tip
    Want to know more about Ascender Framework's controllers? See the [Controllers Overview](../controllers/overview.md)


