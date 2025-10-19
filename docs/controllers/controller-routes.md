# Defining Controller Routes

Each controller works as a container which contains HTTP Endpoints. They group endpoints that are related to specific task providing modular approach of defining routes and HTTP API endpoints.

Each HTTP endpoint requires:
- A python [decorator](https://peps.python.org/pep-0318/) describing HTTP method: `@Get()`, `@Post()`, `@Put()`, `@Patch()` and `@Delete()`
- Controller's method function defining behaviour of the HTTP method. Each time request will be sent to that route, this method will be executed and it's output will be returned as a HTTP response.

```py title="todo_controller.py"
from .dtos.item import ItemDTO

@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service
    
    @Post("items") # POST: /todo/items
    async def add_todo_item(self, data: ItemDTO):
        return await self.todo_service.add_item(data)

    @Get("items/{item_id}") # GET: /todo/items/{item_id}
    async def get_todo_item(self, item_id: int):
        return await self.todo_service.get_item(item_id)
    
    @Get("items") # GET: /todo/items
    async def get_todo_item(self):
        return await self.todo_service.get_items()
    
    @Delete("items/{item_id}") # DELETE: /todo/items/{item_id}
    async def remove_todo_item(self, item_id: int):
        return await self.todo_service.delete_item(item_id)
```

## HTTP GET Method with `@Get()` decorator

The HTTP GET method is used to request data from a specified resource. It is one of the most common and widely used HTTP methods.

The GET method is for **read-only** operations only, the GET method retrieves data without cause any side effects on server or modifying it's state (e.g., it doesn't update or delete data).

Ascender Framework follows FastAPI's principles in terms of declaring HTTP endpoints (their paths, queries and request bodies).

Usually in GET method you don't declare request body, because it made for **read-only** operations. In GET method we mostly use `query` and `path` parameters.
```py hl_lines="12-14 16-18"
from .dtos.item import ItemDTO

@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service
    
    ...

    @Get("items") # GET: /todo/items
    async def get_todo_item(self):
        return await self.todo_service.get_items()
    
    @Get("items/{item_id}") # GET: /todo/items/{item_id}
    async def get_todo_item(self, item_id: int):
        return await self.todo_service.get_item(item_id)
```

As in provided example, there we use path parameters in `get_todo_item`. Let's define query params in `get_todo_item`, usually they are optional and serve same as flag-like behaviour

```py hl_lines="12-14"
from .dtos.item import ItemDTO

@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service
    
    ...

    @Get("items") # GET: /todo/items
    async def get_todo_item(self, page: int = 1, max_items: int = 10):
        return await self.todo_service.get_items_paginated(page, max_items)
```

In this example you mark `page` and `max_items` as query parameters of `/todo/items` route. They also have default values which will be used if none of these query params wer e passed.

Example of endpoint: `/todo/items?page=1&max_items=20` will set `page` parameter of method and `max_items` to specified values and also will validate them for `int` type



## HTTP POST Method with `@Post()` Decorator

The HTTP POST method is used to send data to the server to **create a new resource**. Unlike GET, POST includes a **request body** that typically contains the data for creating or processing a resource.

In the Ascender Framework, data sent in a POST request is validated using DTOs (Data Transfer Objects). DTOs ensure that the input data is properly structured and validated before reaching the endpoint logic.

What are DTOs? DTOs are objects that define the shape and structure of data sent or received in an HTTP request/response. They:
- Validate and parse incoming data.
- Prevent invalid data from reaching the business logic layer.
- Improve security by ensuring type safety and structure adherence.

In the Ascender Framework, DTOs can be defined using [Pydantic](https://docs.pydantic.dev), which provides powerful data validation and parsing capabilities
```py hl_lines="12-14"
from .dtos.item import ItemDTO

@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service

    ...

    @Post("items") # POST: /todo/items
    async def add_todo_item(self, data: ItemDTO):
        return await self.todo_service.add_item(data)
```

In this example, `ItemDTO` defines the structure and validation rules for the request body and `add_todo_item` processes the incoming data and creates a new to-do item.

```py title="dtos/item.py"
from ascender.common import BaseDTO

class ItemDTO(BaseDTO):
    title: str
    description: str = ""
    completed: bool = False
```

!!! tip
    For more on Pydantic and Request Body definition guides, refer to the [Pydantic documentation](https://docs.pydantic.dev) or [FastAPI request body documentation](https://fastapi.tiangolo.com/tutorial/body/).


## HTTP PUT and PATCH Methods with `@Put()` and `@Patch()` Decorators

The HTTP PUT and PATCH methods are used for **updating existing resources**.

**PUT**
- Replaces the entire resource with the provided data.
- The request body typically includes all fields.

**PATCH**
- Updates specific fields of a resource.
- The request body contains only the fields to update.

```py hl_lines="10-12 14-16"
from .dtos.item import ItemDTO, UpdateItemDTO

@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service

    @Put("items/{item_id}") # PUT: /todo/items/{item_id}
    async def update_todo_item(self, item_id: int, data: ItemDTO):
        return await self.todo_service.update_item(item_id, data)

    @Patch("items/{item_id}") # PATCH: /todo/items/{item_id}
    async def partially_update_todo_item(self, item_id: int, data: UpdateItemDTO):
        return await self.todo_service.partially_update_item(item_id, data)
```

- `ItemDTO` defines the full structure for replacing an item (PUT).
- `UpdateItemDTO` allows partial updates (PATCH).

```py title="dtos/item.py"
from ascender.common import BaseDTO

class UpdateItemDTO(BaseDTO):
    """
    Which field is specified and is not None, that field will be updated
    """
    title: str | None = None
    description: str | None = None
    completed: bool | None = None
```

Example Endpoint Usage for PUT:
```http
PUT /todo/items/1
Content-Type: application/json

{
    "title": "Buy groceries and cook dinner",
    "completed": true
}
```

Example Endpoint Usage for PATCH:

```http
PATCH /todo/items/1
Content-Type: application/json

{
    "completed": true
}
```


## HTTP DELETE Method with `@Delete()` Decorator

The HTTP DELETE method is used to remove resources from the server. It is idempotent, meaning multiple DELETE requests for the same resource should produce the same outcome.

```py hl_lines="8-10"
@Controller(
    standalone=True
)
class TodoController:
    def __init__(self, todo_service: TodoService):
        self.todo_service = todo_service

    @Delete("items/{item_id}") # DELETE: /todo/items/{item_id}
    async def remove_todo_item(self, item_id: int):
        return await self.todo_service.delete_item(item_id)
```

- The `item_id` is passed as a path parameter to specify which resource to delete.
- The `todo_service` handles the deletion logic and returns an appropriate response.

Example Endpoint Usage:
```http
DELETE /todo/items/1
```