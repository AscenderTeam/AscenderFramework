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

- Getting Started: docs/introduction/installation.md
- Architecture: docs/introduction/overview.md
- Controllers: docs/controllers/overview.md
- Validators: docs/essentials/data-validation.md
- Dependency Injection: docs/di/overview.md
- CLI Engine: docs/cli/overview.md
- CLI Command Types: docs/cli/command-types.md
- Creating CLI Commands: docs/cli/creating-commands.md
- CLI Registration: docs/cli/registration.md


## CLI Usage

- Global CLI (tooling):
  - ascender [command]
  - Examples:
    - ascender new --name <project-name> --orm-mode <tortoise|sqlalchemy>
    - ascender serve

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
ascender serve
```
Or via local wrapper:
```
ascender run serve
```


## Project Structure

- src/bootstrap.py: Framework and server configuration
- src/controllers/: Your controllers (e.g., main controller)
- start.py: Initialization/bootstrap entrypoint for the application


## Testing

- Unit tests live under src/tests/
- Run tests via the local wrapper:
  - ascender run tests
- Initialize a basic testing setup (to be implemented):
  - ascender run tests init
    - Generates src/tests basic tests and pytest.ini


## Contributing

Contributions are welcome! Please read through our contributing guidelines.

- Guidelines: docs/introduction/next-steps.md


## Need help?

If you need any help, want to report a bug, improve documentation or contribute, please open an issue in this repository after reading the guidelines.


## License

This project is licensed under the MIT License (LICENSE).

