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
git clone https://github.com/AscenderTeam/AscenderFramework.git
cd AscenderFramework
poetry install
```

We recommend using [Poetry](https://python-poetry.org/) for dependency management. 
However pip is also can be used for installing dependencies.

```bash
pip install -r requirements.txt
```

## Getting Started

1. **Initialize the Application**:
   Use `python3 start.py serve` to start your application.

2. **Database Initialization**:
   Utilize the `use_database()` function for initializing the database.

3. **Creating Controllers**:
   Controllers include `endpoints.py`, `service.py`, and `repository.py`. Optionally, you can add `models.py` for Pydantic models and `serializer.py` for serialization.

## CLI Commands

- **Create a New Controller**:
  ```bash
  python3 start.py new controller --name ControllerName
  ```

- **Add Optional Files to a Controller**:
  ```bash
  python3 start.py add optionals --name ControllerName
  ```

- **Initialize Database Migration**:
  ```bash
  python3 start.py migration init
  ```

- **Create a Database Migration**:
  ```bash
  python3 start.py migration migrate --name MigrationName
  ```

## Project Structure

- `bootstrap.py`: For server configuration and controller registration.
- `controllers/`: Contains the controllers with their respective `endpoints.py`, `service.py`, and `repository.py`.
- `models/`: (Optional) Pydantic models for data structure definition.
- `serializers/`: (Optional) For converting Tortoise models to Pydantic models.

## Contributing

Contributions are welcome! Please adhere to the project's coding standards and commit guidelines.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).