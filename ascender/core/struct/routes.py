from enum import Enum
from typing import Any, Literal

from fastapi.datastructures import Default


def create_route_decorator(
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"]
):
    """
    Factory function to create route decorators for different HTTP methods.

    Args:
        method (Literal[&quot;GET&quot;, &quot;POST&quot;, &quot;PUT&quot;, &quot;PATCH&quot;, &quot;DELETE&quot;]): The HTTP method for the route.
    """
    def decorator(
        path: str = "/",
        response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] | None = None,
        **kwargs
    ):
        path = "" if path == "/" else f"/{path.lstrip('/')}"

        def wrapper(func):
            metadata = {
                "methods": [method],
                "path": path,
                "response_model": response_model,
                "status_code": status_code,
                "tags": tags,
                **kwargs
            }
            if not (getattr(func, "__cmetadata__", None)):
                func.__cmetadata__ = metadata
                return func

            func.__cmetadata__ = {
                **func.__cmetadata__,
                **metadata,
            }

            return func

        return wrapper

    return decorator


Get = create_route_decorator("GET")
Post = create_route_decorator("POST")
Put = create_route_decorator("PUT")
Patch = create_route_decorator("PATCH")
Delete = create_route_decorator("DELETE")

__all__ = ["Get", "Post", "Put", "Patch", "Delete"]
