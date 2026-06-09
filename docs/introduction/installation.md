# Installation

Get up and running with the Ascender Framework in a few minutes.

## Prerequisites

- **Python 3.11 or higher** — the framework leverages modern Python features and optimizations.
- **Poetry** — Ascender manages project dependencies through [Poetry](https://python-poetry.org/).

!!! tip "Poetry virtual environments"
    Make sure Poetry is configured to create a virtual environment for each project:

    ```bash
    poetry config virtualenvs.create true
    ```

## Install the framework

1. **Install Poetry** (if not already installed):

    ```bash
    pip install poetry
    ```

2. **Install the Ascender Framework CLI:**

    ```bash
    pip install ascender-framework
    ```

3. **Verify the installation:**

    ```bash
    ascender -h
    ```

    This should display the available CLI commands.

## Create your first project

Scaffold a new project with the `new` command:

```bash
ascender new --name my-app
cd my-app
```

By default the project is set up with the SQLAlchemy ORM. Prefer Tortoise?

```bash
ascender new --name my-app --orm tortoise
```

The generated project looks like this:

```
my-app/
├── ascender.json          # framework configuration
├── pyproject.toml         # dependencies, managed by Poetry
└── src/
    ├── main.py            # application entry point
    ├── bootstrap.py       # providers: router, database, docs
    ├── routes.py          # route table
    └── settings.py        # project settings
```

## Run the development server

```bash
ascender run serve
```

Your API is now live at `http://127.0.0.1:8000` — with interactive OpenAPI docs at [`/docs`](http://127.0.0.1:8000/docs). The server hot-reloads on code changes.

Need a different host or port?

```bash
ascender run serve -H 0.0.0.0 -p 8080
```

## Next steps

- [Learn what makes Ascender different](overview.md)
- [Build your first controller](../essentials/controllers.md)
- [Understand dependency injection](../essentials/dependency-injection.md)
