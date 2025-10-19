class WrongORMException(Exception):
    def __init__(self, class_method: str) -> None:
        self.class_method = class_method

    def __str__(self) -> str:
        return f"Function `{self.class_method}` was only made for SQLAlchemy, use `settings.TORTOISE_ORM` for loading entities of Tortoise ORM"