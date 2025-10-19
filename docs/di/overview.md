# Overview
---
## Dependency Injection Overview

Dependency Injection in Ascender Framewrok was inspired by [Angular's DI principles](https://angular.dev/guide/di) and tailored for python's syntax and ecosystem. It also uses services, repositories and other plain values (providers) as dependencies. The main purpose of this all is to supply other parts of your application with necessery dependencies which may contain: extra business logic, configuration or other types of values.

All these dependencies are managed by Ascender Framework's injector. It's responsible for resolving and storing dependencies while also managing their states seamlessly.
Before application bootstrap, there's an application injector called `root` injector. It's being created during application pre-initialization when you type `ascender` or `ascender run` command in CLI. It loads all modules starting from CLI modules and finishing with application itself which contains FastAPI, router graph and other necessery parts of framework.

## Learn more about Ascender Framework's dependency injection
