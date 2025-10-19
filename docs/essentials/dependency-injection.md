# Modular Design with Dependency Injection (DI)

When you need to share logic between controllers, you can use the design pattern of dependency injection (DI). This allows you to create a “service”—a reusable piece of code—that can be injected into controllers, keeping your controller’s routes clean and separating your business logic into single sources of truth.

The Ascender Framework's DI pattern is similar to Angular and NestJS but tailored to Python's design and the simplicity of the framework.

---

## What are Services?

Services are reusable pieces of code that can be injected across your application. They allow you to:

- Define business logic in a centralized manner.
- Share logic seamlessly across controllers and other parts of your application.
- Keep your code organized by separating dependencies and concerns.

### Defining a Service

Similar to defining controllers, services follow a structured approach:

- Use the `@Injectable` decorator to mark the service as an injectable object. The `provided_in` parameter assigns the service to a specific injection scope (usually `"root"`).
- Define a Python class containing the behavior of the injectable object.
- Optionally, inherit from the `Service` class for compatibility with older Ascender Framework versions.

Here's the example of `AscenderService`.

```python title="ascender_service.py" linenums="1"
from ascender.common import Injectable
from ascender.core import Service
from fastapi import HTTPException

@Injectable(provided_in="root")
class AscenderService(Service):
    ascended: int  # Example field, avoid mutable shared state in real-world applications.

    def __init__(self):
        # Initialize dependencies or state here
        self.ascended = 0

    def ascend(self, amount: int):
        self.ascended += amount
        return self.ascended

    def descend(self, amount: int):
        if self.ascended == 0:
            raise HTTPException(422, "You can't descend further than 0. Try ascending first.")
        self.ascended -= amount
        return self.ascended
```

---

## How to Use a Service

To use a service in a controller, follow these steps:

1. **Import the Service**: Import the service into the controller module.
2. **Inject the Service**: Use the controller's `__init__` method to declare the service as a parameter. The Ascender Framework will automatically resolve the dependency.

Here’s how it might look like in `AscenderController`
```python title="ascender_controller.py" linenums="1"
from ascender.core import Controller
from ascender.decorators import Post
from .ascender_service import AscenderService
from fastapi import Body

@Controller(standalone=False)
class AscenderController:
    def __init__(self, ascender_service: AscenderService):
        self.ascender_service = ascender_service

    @Post()  # Root endpoint of this controller (`/ascend`)
    async def ascend_endpoint(self, amount: int = Body()) -> int:
        return self.ascender_service.ascend(amount=amount)

    @Post("descend")  # Endpoint to descend
    async def descend_endpoint(self, amount: int = Body()) -> int:
        return self.ascender_service.descend(amount=amount)
```

!!! tip
    Read more about Ascender Framework's dependency injection (DI) patterns and use-cases in [Advanced Dependency Injection Guide](/dependency-injection/overview)