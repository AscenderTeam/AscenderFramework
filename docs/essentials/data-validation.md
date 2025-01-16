# Request Body & Responses with Type Validation

Request bodies and responses are essential for defining the structure and validation of the data exchanged in your API. The Ascender Framework leverages Pydantic models to provide type safety, validation, and seamless integration with FastAPI's request and response handling.

---

## What Are DTOs and Responses?

- **DTOs (Data Transfer Objects):** These models define the structure of incoming request bodies, ensuring that the data sent by clients is validated and adheres to the expected schema.
- **Responses:** These models define the structure of outgoing data, ensuring consistent responses across your API.

Ascender Framework simplifies their usage with base classes:

- **`BaseDTO`**: The base class for request body models.
- **`BaseResponse`**: The base class for response models, optional but useful for nesting data or complex response structures.

Naming conventions are recommended but not strictly required:

- **DTOs**: `[Name]DTO`
- **Responses**: `[Name]Response`

---

## Defining DTOs
DTOs inherit from `BaseDTO` and specify the expected structure of the request body. Validation is automatically handled by Pydantic.

Here's how it might look like in example with `CreateUserDTO`:
```python linenums="1"
from ascender.common import BaseDTO

class CreateUserDTO(BaseDTO):
    name: str
    email: str
```
In this example, `CreateUserDTO` ensures that any incoming request to create a user includes `name` and `email` fields as strings.

---

## Defining Responses
Responses inherit from `BaseResponse` and define the structure of the API's responses. This is particularly useful for ensuring consistent output and handling nested or complex data.

```python linenums="1"
from ascender.common import BaseResponse

class UserResponse(BaseResponse):
    id: int
    name: str
    email: str
```
In this example, `UserResponse` ensures that the API consistently returns user data with `id`, `name`, and `email` fields.

---

## Using DTOs and Responses in Controllers
DTOs and responses are integrated directly into your controllers to handle request validation and response serialization.

```python linenums="1"
from ascender.core import Controller, Post
from .dto import CreateUserDTO
from .responses import UserResponse

@Controller(standalone=False)
class UserController:
    @Post()
    async def create_user(self, body: CreateUserDTO) -> UserResponse:
        return UserResponse(
            id=1,  # Example ID
            name=body.name,
            email=body.email
        )
```
In this example, the `create_user` endpoint:

1. Validates the incoming request body using `CreateUserDTO`.
2. Returns a structured response using `UserResponse`.
---

## When to Use BaseResponse
While `BaseResponse` is optional, it is highly recommended for complex APIs requiring:

- Nested data structures.
- Consistent response formats.

For example:
```python linenums="1"
from typing import Generic, TypeVar
from ascender.common import BaseResponse

T = TypeVar("T")

class PaginatedResponse(BaseResponse, Generic[T]):
    data: list[T]
    total: int
```

---

### Summary
- Use **DTOs** (`BaseDTO`) for request bodies to validate incoming data.
- Use **Responses** (`BaseResponse`) for structured and consistent API responses.
- Follow naming conventions (`[Name]DTO`, `[Name]Response`) to maintain clarity and separation of concerns.

