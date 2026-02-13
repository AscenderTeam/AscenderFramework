# Controller Hooks

Controller hooks are decorators with methods that handle specific logic inside the controller, as an example of hooks, take a look at built-in decorators: `@Get()`, `@Post()`, `@Put()`, `@Delete()` etc.:
```py
from ascender.core import Controller, Get, Post, Put, Delete

@Controller(standalone=True)
class MyController:

    @Get()
    def get_logic(self):
        return {"message": "Hello World"}

    @Post()
    def post_logic(self):
        return {"message": "Hello World"}

    @Put()
    def put_logic(self):
        return {"message": "Hello World"}

    @Delete()
    def delete_logic(self):
        return {"message": "Hello World"}
```

These decorators are built-in controller hooks and they are used to define HTTP methods for the controller's endpoints. Each decorator corresponds to a specific HTTP method, allowing you to handle requests appropriately within your controller.

## Defining Custom Controller Hook

You can also create your own controller hook decorator by defining a class that inherits from `ControllerDecoratorHook` from `ascender.core` and implementing the required methods. Here's an example of a custom controller hook that logs requests:

```py
from ascender.core import ControllerDecoratorHook, inject
from typing import Callable, Any

from .clients import DummyClient # Example client that has .add_event_handler() method


class WebsocketRequest(ControllerDecoratorHook):

    websocket_client: DummyClient = inject(DummyClient)
    
    def __init__(self, event: str):
        super().__init__()
        self.event = event

    def on_load(self, callable: Callable):
        self.websocket_client.add_event_handler(self.event, callable)
```

You can then use this custom hook in your controller like this:

```py
from ascender.core import Controller, Get
from .hooks import WebsocketRequest

@Controller(standalone=True)
class MyController:

    @WebsocketRequest("my_event")
    async def websocket_logic(self):
        return {"message": "Hello WebSocket"}
```

Now it will work when the Router Graph will load (hydrate) every controller defined there.

!!! note
    You should define your custom controller `MyController` in the Router Graph to make it work.
    See the [Combining and Composing Controllers with the Router Graph](../essentials/controllers.md#combining-and-composing-controllers-with-the-router-graph) for more details.


## Configuration and Metadata for Controller Hooks

### Accessing Route Configuration in Custom Controller Hook
You can get the configuration for a specified route of the controller where the ControllerDecoratorHook is used by accessing the `self.route_configuration` attribute inside your custom hook class. This attribute provides access to the route's configuration details, allowing you to tailor the behavior of your hook based on the specific route settings.
```py
from ascender.core import ControllerDecoratorHook, inject
from typing import Callable, Any

class CustomHook(ControllerDecoratorHook):

    def __init__(self, some_param: str):
        super().__init__()
        self.some_param = some_param

    def on_load(self, callable: Callable):
        route_config = self.route_configuration
        # You can now use route_config to customize behavior
        print(f"Route config for {route_config['path']}: {route_config}")
```

### Accessing Controller Metadata in Custom Controller Hook

You can also access the metadata of the controller or its reference (instance) where the ControllerDecoratorHook is used by accessing the `self.controller` attribute inside your custom hook class. This attribute provides access to the controller's metadata, allowing you to utilize additional information about the controller within your hook's logic.

```py
from ascender.core import ControllerDecoratorHook, inject
from typing import Callable, Any

class CustomHook(ControllerDecoratorHook):

    def __init__(self, some_param: str):
        super().__init__()
        self.some_param = some_param

    def on_load(self, callable: Callable):
        controller_instance = self.controller
        # You can now use controller_instance to access metadata
        print(f"Controller instance: {controller_instance}")
```

You also can access controller's injection scope only if the controller is standalone (has that `standalone=True` in its decorator), by using `inject(...)` function inside the `on_load` method of your custom hook:

```py
from ascender.core import ControllerDecoratorHook, inject
from typing import Callable, Any

class CustomHook(ControllerDecoratorHook):

    def __init__(self, some_param: str):
        super().__init__()
        self.some_param = some_param

    def on_load(self, callable: Callable):
        # Access the controller's injection scope
        some_service = inject(SomeService, scope=self.controller)
        # You can now use some_service within your hook logic
        print(f"Using service: {some_service}")
```

By this you have also access to dependencies that were provided specifically for that standalone controller.