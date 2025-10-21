from json import JSONDecodeError
from typing import Any, Self

from pydantic import ValidationError


class RPCException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 500,
        details: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """
        Ascender RPC Exception for Microservices.
        
        Args:
            message (str): Error message.
            code (int, optional): Error code. Defaults to 500.
            details (str | None, optional): Additional error details. Defaults to None.
            metadata (dict[str, Any], optional): Additional metadata. Defaults to None.
        """
        self.message = message
        self.code = code
        self.details = details
        self.metadata = metadata or {}

        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize exception into a dictionary for logging or transport."""
        return {
            "error": self.message,
            "code": self.code,
            "details": self.details,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, _dict: dict) -> Self:
        """Serialize RPCException from dict"""
        return cls(
            message=_dict["error"],
            code=_dict["code"],
            details=_dict["details"],
            metadata=_dict["metadata"]
        )

    @staticmethod
    def is_exception(_dict: dict):
        required_keys = {"error", "code", "details", "metadata"}

        if required_keys.issubset(_dict):
            return True
        
        return False

    @classmethod
    def from_validation_err(cls, err: ValidationError) -> Self:
        return cls(
            message=f"Validation Error | {err.title}",
            code=422,
            details=err.json(),
            metadata={
                "err_count": err.error_count()
            }
        )
    
    @classmethod
    def from_json_err(cls, err: JSONDecodeError) -> Self:
        return cls(
            message="Internal Validation Error",
            code=500,
            details=err.msg,
            metadata={
                "colno": err.colno,
                "lineno": err.lineno,
                "doc": err.doc
            }
        )
    
    def __str__(self):
        return f"\n{self.message}\n\n{self.details or ''}"