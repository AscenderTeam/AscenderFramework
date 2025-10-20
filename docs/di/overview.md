# Overview
---
## Dependency Injection Overview

Dependency Injection in Ascender Framework was inspired by [Angular's DI principles](https://angular.dev/guide/di) and tailored for Python's syntax and ecosystem. It uses services, repositories, and other plain values (providers) as dependencies. The main purpose is to supply other parts of your application with necessary dependencies which may contain extra business logic, configuration, or other types of values.

All these dependencies are managed by Ascender Framework's injector. It's responsible for resolving and storing dependencies while also managing their states seamlessly.

Before application bootstrap, there's an application injector called `root` injector. It's created during application pre-initialization when you type `ascender` or `ascender run` command in CLI. It loads all modules starting from CLI modules and finishing with the application itself, which contains FastAPI, router graph, and other necessary parts of the framework.

## Learn more about Ascender Framework's dependency injection

- [Injectables Guide](injectables.md)
- [Dependency Providers](dependency-providers.md)
- [DI Advanced Guide](guide.md)
