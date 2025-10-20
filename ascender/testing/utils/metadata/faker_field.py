from typing import Any


try:
    from faker import Faker
    _faker = Faker()
except ImportError:
    _faker = None


class FakerField:
    """
    Marks a field for faker-based data generation.
    
    Example:
    ```python
    Annotated[str, FakerField("name")]
    ```
    """
    def __init__(self, method: str, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def generate(self) -> Any:
        if not _faker:
            raise RuntimeError("Faker is not installed. Run `pip install faker`.")
        if not hasattr(_faker, self.method):
            raise AttributeError(f"Faker has no method '{self.method}'")
        return getattr(_faker, self.method)(*self.args, **self.kwargs)
