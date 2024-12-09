class BaseUserException(Exception):
    def __init__(self, login: str) -> None:
        self.login = login


class UserNotFoundError(BaseUserException):
    def __str__(self) -> str:
        return f"User with login `{self.login}` not found in system"


class IncorrectPasswordError(BaseUserException):
    def __str__(self) -> str:
        return f"Incorrect password was entered for user with login {self.login}"


class AlreadyExistsError(BaseUserException):
    def __str__(self) -> str:
        return f"Cannot create user with login {self.login}. This user is already exists in system!"


class UninitializedAuthprovider(Exception):
    def __str__(self) -> str:
        return "Authentication Provider isn't initialized in `bootstrap.py`. Please add `app.use_authentication()` in `Bootstrap.server_boot_up()` method"