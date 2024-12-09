# Ascender Framework

## Introduction

Ascender Framework is a powerful, FastAPI-based framework designed to streamline the development of web applications. Inspired by NestJS and some parts of Laravel, it combines the simplicity of Python with the robust architecture of modern web frameworks.

## Features

- **FastAPI-based**: Leverages FastAPI's speed and ease of use.
- **CLI Support**: Powerful CLI tools for efficient project management.
- **Caching System**: Utilizes `.asc_cache` for efficient data handling.
- **Asynchronous Support**: Built-in async support with Tortoise ORM for database interactions.
- **Modular Structure**: Inspired by NestJS, offering a structured and modular architecture.

## Installation

```bash
pip install ascender
ascender projects new <project-name>
cd <project-name>
```

We recommend using [Poetry](https://python-poetry.org/) for dependency management. 
However pip is also can be used for installing dependencies.

Pip:
```bash
pip install -r requirements.txt
```

Poetry:
```bash
poetry install
```

## Getting Started

1. **Initialize the Application**:
   Use `ascender run serve` to start your application.

2. **Database Initialization**:
   Utilize the `use_database()` function for initializing the database.

3. **Creating Controllers**:
   Controllers include `endpoints.py`, `service.py`, and `repository.py`. Optionally, you can add `models.py` for Pydantic models and `serializer.py` for serialization.

## CLI Commands

- **Create a New Controller**:
  ```bash
  ascender run controllers new --name <controller-name>
  ```

- **Add Optional Files to a Controller**:
  ```bash
  ascender run controllers optionals --name <controller-name>
  ```

- **Initialize Database Migration**:
  ```bash
  ascender run migration init
  ```

- **Create a Database Migration**:
  ```bash
  ascender run migration migrate --name MigrationName
  ```

## Project Structure

- `bootstrap.py`: For server configuration and controller registration.
- `controllers/`: Contains the controllers with their respective `endpoints.py`, `service.py`, and `repository.py`.
- `{controller}/models/` or `models.py`: (Optional) Pydantic models for data structure definition.
- `{controller}/serializers/` or `serializers.py`: (Optional) For converting Tortoise models to Pydantic models.

## Contributing

Contributions are welcome! Please adhere to the project's coding standards and commit guidelines.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).