# Welcome to Ascender Framework

Ascender Framework is a powerful, FastAPI-based framework designed to streamline the development of web applications. Inspired by NestJS and other dependency-injection frameworks, it brings a modern architecture to Python projects.

## Documentation

Get started quickly and explore more advanced features:

- [Getting Started](introduction/installation.md)
- [Architecture](introduction/overview.md)
- [Controllers](essentials/controllers.md)
- [Validators](essentials/data-validation.md)
- [Modular Design](essentials/dependency-injection.md)
- [HTTP Client](essentials/http-client.md)
- [Microservices](microservices/overview.md)

## Getting Started

Install Ascender Framework (with its CLI) globally:

```bash
pip install ascender-framework
```

Initialize a new project:

```bash
ascender new --name <project-name> --orm-mode <tortoise|sqlalchemy>
cd <project-name>
ascender serve
# or
ascender run serve
```

## Project Structure

- `bootstrap.py`: Framework and server configuration.
- `controllers/`: Controller classes defining endpoints.
- `start.py`: Application initialization entry point.

