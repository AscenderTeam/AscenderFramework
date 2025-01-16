# Understanding Dependency Injection

Dependency Injection (DI) is a fundamental concept within the Ascender Framework. It enables seamless management of dependencies across various components, ensuring modularity, scalability, and testability. DI is deeply integrated into the framework, allowing classes such as controllers, services, and modules to define and consume dependencies effortlessly.


## Providing a dependency

```py
class DogService:
    ...
```

Let's imagine we have `DogService` that has some sort of useful functions that are required in the controller.

Now first what we have to do is to add `@Injectable` decorator to mark this class as an injectable object and can be used by injector as a dependency.

```py hl_lines="1 3"
from ascender.core import Injectable

@Injectable()
class DogService:
    ...
```


## Providing at The Root level by using decorator with `provided_in`

You can provide a service at the root level of application by using `provided_in` parameter set to `"root"` in `@Injectable` decorator.

This makes your service available everywhere inside of your application's scope.

```py hl_lines="4"
from ascender.core import Injectable

@Injectable(
    provided_in="root"
)
class DogService:
    ...
```

When you provide the service at the root level, `DogService` becomes a single and shared instance (singletone) and can be accessed and injected into any class in scope of your Ascender Framework application which asks for it.


## Providing at the AscModule level

You can provide services at `@AscModule` level by using `providers` parameter field of the `@AscModule` decorator. In this case, `DogService` will be added to the scope of the `@AscModule` and will be available to all dependencies of the `@AscModule`, it's declarations (controllers and guards) and all of it's imported subjects (dependencies of imported modules or controllers).

```py
@AscModule(
    imports=[],
    declarations=[DogController], # will be available in `DogController`
    providers=[DogService],
    exports=[]
)
class DogModule: ...
```

Same thing can be applied to [`standalone` controllers](/controllers/controller-types/#standalone-controllers)
```py
@Controller(
    standalone=True,
    providers=[DogService]
)
class DogController: ...
```

!!! note
    Declaring a service like this causes `DogService` to always be included in your application. Even if you don't use it anywhere.


## Providing at The Root level in `IBootstrap`

You can also use `providers` field of the variable which follows `IBootstrap` type and is being passed to the `createApplication` function to provide a service or any `@Injectable` at the root level of application.

```py title="src/bootstrap.py"
appBootstrap: IBootstrap = {
    "providers": [
        DogService,
    ]
}
```

```py title="src/main.py"
from ascender.core.applications.create_application import createApplication
from bootstrap import appBootstrap

app = createApplication(config=appBootstrap)


if __name__ == "__main__":
    app.launch()
```
In this example, the `DogService` becomes root-level dependency and becomes available to all controllers and other injectables.

!!! note
    Declaring a service like this causes `DogService` to always be included in your application. Even if you don't use it anywhere.


## Using / Injecting a dependency

There's few ways to inject a dependency, most popular and simple way is to declare it in the `__init__` method of the class. When Ascender Framework creates an instance of the controller, it determines all services or dependencies that class needs by it's `__init__` method and starts chains of injections. 

For example, if `DogController` requires the `DogService`, `__init__` method would look like this:
```py
@Controller(...)
class DogController:
    def __init__(self, service: DogService):
        self.service = service
```

Another option is to use the `inject` method:
```py
@Controller(...)
class DogController:
    service = inject(DogService)
```

Dependency injection follows factory & caching pattern. It first checks if the injector has already initialized and existing instance of that service, if it doesn't, then the injector creates one using the registered provider by invoking it and injecting it's dependencies to initialize it, before returning the service.

When all requested services have been resolved and returned with issues, then Ascender Injector will initialize controller by invoking it's `__init__` method and passing all those services it requires as keyword arguments.

!!! warning
    Always keep in mind, that in `__init__` method of all controllers and other dependencies using `@Injectable` decorator you can't use parameters without annotations.
    If you will, then it may lead to error or an unexpected behaviour. Use `__init__` method only for dependency injection in these types of objects!

``` mermaid
graph TD
  subgraph Ascender Injector 
    B(Service A)
    C(DogService)
    D(Service C)
    E(Service D)
  end
  C --> H(DogController)
```