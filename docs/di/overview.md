# Dependency Injection Overview

Dependency Injection in the Ascender Framework was inspired by [Angular's DI principles](https://angular.dev/guide/di) and tailored for Python's syntax and ecosystem. It uses services, repositories, and other plain values (providers) as dependencies. The main purpose is to supply other parts of your application with the dependencies they need — business logic, configuration, or any other kind of value.

All these dependencies are managed by the framework's **injector**. It is responsible for resolving and storing dependencies while seamlessly managing their state.

Before application bootstrap, there is an application-wide injector called the **root injector**. It is created during application pre-initialization when you run `ascender` or `ascender run` in the CLI. It loads all modules — starting from CLI modules and finishing with the application itself, which contains FastAPI, the router graph, and other necessary parts of the framework.

## Learn more

<div class="grid cards" markdown>

-   :material-needle:{ .lg .middle } __Injectables Guide__

    ---

    Define services with `@Injectable` and let the framework scaffold them for you.

    [:octicons-arrow-right-24: Injectables](injectables.md)

-   :material-package-variant:{ .lg .middle } __Dependency Providers__

    ---

    Value, class, and factory providers — injection tokens beyond plain classes.

    [:octicons-arrow-right-24: Providers](dependency-providers.md)

-   :material-graph:{ .lg .middle } __Advanced DI Guide__

    ---

    Hierarchical injectors, scopes, and how resolution actually works.

    [:octicons-arrow-right-24: Deep dive](guide.md)

</div>
