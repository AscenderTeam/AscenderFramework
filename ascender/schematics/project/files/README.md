<h1 align="center">Ascender Framework - The modern, powerful API framework</h1>


<p align="center">
<img src="logo.png" height="150px" />
<br>
<em>
Ascender Framework is a powerful, FastAPI-based framework designed to streamline the development of web applications. <br>
Inspired by NestJS and some parts of other DI frameworks, it combines the simplicity of Python with the robust architecture of modern web frameworks.</em>
</p>

<p align="center">
    <a href="https://framework.ascender.space">Official Website</a>
</p>


## Documentation

Get started! Learn the basics of framework and explore more advanced features and topics.

- [Getting Started](https://framework.ascender.space/tutorials/quickstart)
- [Architecture](https://framework.ascender.space/tutorials/essentials)
- [Controllers](https://framework.ascender.space/tutorials/basics/controllers)
- [Validators](https://framework.ascender.space/tutorials/basics/pydantic)
- [Guards](https://framework.ascender.space/tutorials/basics/guards)

### Advanced level

- [Database](https://framework.ascender.space/tutorials/databases)
- [Abstract Providers](https://framework.ascender.space/tutorials/essentials/dependency-injection/abstracts)
- [CLI Factory](https://framework.ascender.space/tutorials/cli)
- [API](https://framework.ascender.space/api-references)


## Getting Started

Install Ascender Framework (with it's CLI) globally:
```
pip install ascender-framework
```
Initialize project workspace:
```
ascender new --name <project-name> --orm-mode <tortoise|sqlalchemy>
```
Run the first development server:
```
cd <project-name>
ascender serve
```
or use local CLI:
```
ascender run serve
```

## Project Structure

- `bootstrap.py`: For framework and server configuration.
- `controllers/`: Contains the controllers with main controller.
- `start.py`: Contains initialization and bootstrap entrypoint for entire application.

## Contributing

Contributions are welcome! Please read through our [contributing guidelines](https://framework.ascender.space/guidelines/contributions).

## Need a help?

If you need any help, report bug, improve documentation or contribute, please read our guidelines for [contributing](CONTRIBUTING.md) and then head out into issues of this repository.

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).

