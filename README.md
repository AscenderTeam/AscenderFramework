<h1 align="center">Ascender Framework - The modern, powerful API framework</h1>


<p align="center">
<img src="https://github.com/AscenderTeam/AscenderFramework/blob/main/logo.png?raw=true" height="150px" />
<br>
<em>
Ascender Framework is a powerful, FastAPI-based framework designed to streamline the development of web applications. <br>
Inspired by NestJS and some parts of other DI frameworks, it combines the simplicity of Python with the robust architecture of modern web frameworks.</em>
</p>

<p align="center">
    <a href="https://ascender-framework.com">Official Website</a>
</p>


## Documentation

Get started! Learn the basics of framework and explore more advanced features and topics.

- [Getting Started](https://ascender-framework.com/introduction/installation)
- [Architecture](https://ascender-framework.com/introduction/overview)
- [Controllers](https://ascender-framework.com/controllers/overview)
- [Validators](https://ascender-framework.com/essentials/data-validation)
- [Dependency Injection](https://ascender-framework.com/di/overview)
- [CLI Engine](https://ascender-framework.com/cli/overview)
- [CLI Command Types](docs/cli/command-types)
- [Creating CLI Commands](https://ascender-framework.com/cli/creating-commands)
- [CLI Registration](https://ascender-framework.com/cli/registration)


## CLI Usage

- Global CLI (tooling):
  - ascender [command]
  - Examples:
    - ascender new --name <project-name> --orm-mode <tortoise|sqlalchemy>
    - ascender run serve

- Local project CLI wrapper:
  - ascender run [command]
  - Wraps project entrypoints and CLI scripts (shorter than invoking Python directly)
  - Examples:
    - ascender run serve
    - ascender run tests
    - ascender run tests init  # scaffolds basic tests and pytest.ini (planned)


## Getting Started

Install Ascender Framework (with its CLI) globally:
```
pip install ascender-framework
```
Initialize a project workspace:
```
ascender new --name <project-name> --orm-mode <tortoise|sqlalchemy>
```
Run the development server (global):
```
cd <project-name>
ascender run serve
```


## Project Structure

- src/bootstrap.py: Framework and server configuration
- src/controllers/: Your controllers (e.g., main controller)
- start.py: Initialization/bootstrap entrypoint for the application


## Testing

- Unit tests live under src/tests/
- Run tests via the local wrapper:
```
ascender run tests run
```
- Initialize a basic testing setup (to be implemented):
```
ascender run tests init
```
- src/tests basic tests and pytest.ini will be generated


## Contributing

Contributions are welcome! Please read through our contributing guidelines.

- [Guidelines](https://ascender-framework.com/meta/terms)


## Need help?

If you need any help, want to report a bug, improve documentation or contribute, please open an issue in this repository after reading the guidelines.


## License

This project is licensed under the [MIT License](LICENSE).

