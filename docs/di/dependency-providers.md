# Dependency Providers

In the previous chapter, we described how to inject and define class injectable dependencies using their instances and types, but that's far beyond from what Ascender Framework's DI can do. Aside from classes you can also inject and treat plain values (`str`, `int`, `bool`, `tuple`, `list` and other objects) as DI's dependencies

## Injection tokens

Each dependency in Ascender Framework's DI has it's own token. As we described how to define an `@Injectable` using services, type of those services were treated as injection token. The default and common behaviour of Ascender Framework's Injector in that case was to instantiate the class using it's `__init__` and creating instance of the class by also injecting all required tokens.

```py
...
    providers=[DataService]
```

In this scenario `DataService` type is the token associated with `DataService()` object. Everytime you specify `DataService` in type annotations of your injectables, those will be treated as an injection token.

However, you can configure framework's DI to associate your dependency with any other token you specify. For example you can associate `DataService` with `ExtendedFileManager` or you can associate `ExtendedFileManager` with any other interfaces or string you define.

```py title="Inside providers metadata parameter"
[{ "provide": DataService, "use_class": ExtendedFileManager }]
```

Now anytime you inject `DataService` you will get `ExtendedFileManager`, in fact that `DataService` name is more shorter and easier to remember then `ExtendedFileManager`.

The expended provider configuration defines the token and behaviour (how it will be injected).

There's a `Provider` dictionary configuration properties defined in `Provider` type:

- `provide` property contains token of provider which can be either any type or python string.
- Second property defines provider itself, and it's behaviour (the way how it will be injected):
    - `use_class` - used for classes, same as common behaviour and example provided in the upper section.
    - `use_factory` - lets you to define a factory function that returns dependency object. Used for manual construction of non injectable objects.
    - `value` - provides a static and plain value that can be injected as a dependency
- `deps` (optional) and used in some cases like `use_class` and `use_factory` you can manually define what dependencies to inject. These dependencies then will be injected into their constructers
- `multi` allows to associate multiple dependencies with one single token defined in `provide`

## Class injection using `use_class`

This is the default and most commonly used provider type. The DI system resolves the dependency by creating an instance of the specified class. All the dependencies required by the class (specified in its constructor) are also injected automatically.

```py title="Example of use_class"
providers = [
    { "provide": DataService, "use_class": ExtendedFileManager }
]
```

The token `DataService` is associated with the class `ExtendedFileManager`, whenever `DataService` is injected into another injectable or controller, an instance of `ExtendedFileManager` is provided.

## Factory Function based injection using `use_factory`

This provider type allows you to define a factory function that constructs and returns the dependency object manually. It is particularly useful when creating an object involves custom logic or when the object is not designed to be injectable.

```py title="Example of use_factory"
def custom_data_service_factory(config: Config):
    return CustomDataService(config.setting)

providers = [
    Config,
    { 
        "provide": DataService, 
        "use_factory": custom_data_service_factory, 
        "deps": [Config] 
    }
]
```

The factory function (`custom_data_service_factory`) is executed to create the dependency object and any dependencies required by the factory function (e.g., `Config`) can be manually specified in the `deps` property.

Ideal when dependencies require complex initialization logic, or when the object is not managed by the DI system, allowing you to view DI's or application's context.

## Static and Plain value injection using `value`

This provider type allows you to inject a static, predefined value. It is the simplest form of a provider and does not involve any instantiation or custom logic.

```py title="Example of value"
providers = [
    { "provide": "AppConfig", "value": { "debug": True, "version": __version__ } }
]
```

The token `AppConfig` is associated with the provided static value and whenever `AppConfig` is injected, the same value is returned.
Useful for injecting configuration objects, constants, or any plain value that does not require instantiation.

## How to inject string-based tokens?

As we described about static plain value injection using `value`, you might see that it uses string instead of type. In these cases Ascender Framework relies on specific `Inject()` class which provides metadata to annotation you use in `__init__` constructor method of service class. It uses python's [`typing.Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) type to write a **Metadata** reflection for annotation.

Here's the example of how to inject `"AppConfig"` into `ExampleService`:
```py title="src/examples/example_service.py"
from typing import Annotated
from ascender.core import Injectable, Inject


@Injectable()
class ExampleService:
    def __init__(self, app_config: Annotated[dict, Inject("AppConfig")])
        self.app_config = app_config # will have `dict` annotation type
    
    def get_app_config(self) -> dict:
        return self.app_config
```

<!-- TODO: Add InjectionToken object in future releases and describe in documentation here -->