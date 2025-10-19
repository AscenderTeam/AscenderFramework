# Controller Types
There are two types of controllers `standalone` and `non-standalone` controllers.
The main difference between both of them that `standalone` controller is an independendent controller and does not require an [AscModule](/asc-module/overview) to work and host HTTP endpoints.

## Standalone Controllers
Standalone controllers don't require an [AscModule](/asc-module/overview) to access dependency injection scope. You can directly import modules or define and use providers right in the controller itself by managing them in the `@Controller` decorator itself

Here's the example with `SupplierController`:
```py title="supplier_controller.py" linenums="1"
from ascender.core import Controller, Post, Get

from shared.auth.auth_service import AuthService
from shared.auth.user_service import UserService
from shared.dtos import IUserDataDTO

@Controller(
    standalone=True,
    imports=[],
    providers=[AuthService, UserService],
    exports=[]
)
class SupplierController:
    def __init__(self, auth_service: AuthService, user_service: UserService):
        self.auth_service = auth_service
        self.user_service = user_service
    
    @Post("auth")
    async def supply_auth(self, user_data: IUserDataDTO):
        return await self.auth_service.supply_auth(user_data)
    
    @Get("user/{user_id}")
    async def supply_user(self, user_id: int):
        return await self.user_service.supply_user(user_id)
```

As same as [AscModule](/asc-module/overview) has parameters that manage it's dependency injection, a `standalone` controller has it too.

- `imports` can contain other modules or controllers to import to, their `exports` will be imported and exposed to current controller's scope
- `providers` defines providers that will be available only for this controller's dependency injection scope unless you won't explicitly export them by including them in `exports`
- `exports` allows to export providers or imported providers, declarations to other module/controller that will import this controller

!!! tip
    Read more about Dependency Injection in AscModules at the [AscModule Guide Page](/asc-module/overview)


## Non-Standalone Controllers
This type of controllers require a parent [AscModule](/asc-module/overview) to define them as their declaration. As a non-standalone controller will be defined in `declarations` of an [`AscModule`](/asc-module/overview) it becomes the controller of that module which declared it in their `declarations`. It also becomes consumer of the module as it can access it's dependency injection scope and import available dependencies to that module

Here's the example with non-standalone `SupplierController`:
```py title="supplier_controller.py" linenums="1" hl_lines="8"
from ascender.core import Controller, Post, Get

from shared.auth.auth_service import AuthService
from shared.auth.user_service import UserService
from shared.dtos import IUserDataDTO

@Controller(
    standalone=False,
)
class SupplierController:
    def __init__(self, auth_service: AuthService, user_service: UserService):
        self.auth_service = auth_service
        self.user_service = user_service
    
    @Post("auth")
    async def supply_auth(self, user_data: IUserDataDTO):
        return await self.auth_service.supply_auth(user_data)
    
    @Get("user/{user_id}")
    async def supply_user(self, user_id: int):
        return await self.user_service.supply_user(user_id)
```

```py title="supplier_module.py" linenums="1"
from ascender.core import AscModule

from shared.auth.auth_service import AuthService
from shared.auth.user_service import UserService

from .supplier_controller import SupplierController

@AscModule(
    imports=[],
    declarations=[SupplierController],
    providers=[AuthService, UserService],
    exports=[]
)
class SupplierModule: ...
```

Now, `SupplierController` is controller and subject of an [AscModule](/asc-module/overview) `SupplierModule`. `SupplierController` can access DI scope of `SupplierModule` and use it's defined and imported providers

- `imports` can contain other modules or controllers to import to, their `exports` will be imported and exposed to current controller's scope
- `providers` defines providers that will be available only for this controller's dependency injection scope unless you won't export them by including them in `exports`
- `exports` allows to export providers or imported providers, declarations to other module/controller that will import this controller

!!! tip
    Read more about Dependency Injection in AscModules at the [AscModule Guide Page](/asc-module/overview)

