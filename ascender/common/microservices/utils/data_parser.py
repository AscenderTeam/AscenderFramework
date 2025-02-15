import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel, ValidationError, TypeAdapter

T = TypeVar("T")

def validate_json(json_data: str, expected_type: Type[T]) -> T:
    """
    Validate and parse a JSON string into the specified type.

    This utility works for both Pydantic models and ordinary types
    (such as int, str, list, dict, tuple, etc.) by first decoding the
    JSON string and then validating/converting it to the expected type
    using Pydantic's `parse_obj_as` function.

    Parameters:
        json_data (str): The JSON string to validate.
        expected_type (Type[T]): The type into which to parse the data. This
            can be a Pydantic model class or any valid Python type (including
            complex types like List[int], Dict[str, Any], etc.).

    Returns:
        T: An instance of the expected type, validated and parsed from the JSON.

    Raises:
        ValueError: If the JSON is malformed or if the data fails validation.
    """
    if issubclass(expected_type, BaseModel):
        result = expected_type.model_validate_json(json_data)
        
        return result
    
    # Validate and convert the data to the expected type
    result = TypeAdapter(expected_type).validate_json(json_data)

    return result


def validate_python(obj: Any, expected_type: Type[T]) -> T:
    """
    Validate and parse a Python object into the specified type.

    This utility works for both Pydantic models and ordinary types
    (such as int, str, list, dict, tuple, etc.) by first handling python object
    and then validating/converting it to the expected type
    using Pydantic's `parse_obj_as` function.

    Parameters:
        obj (Any): Serializable python object (e.g. dict, list, int, str, and etc).
        expected_type (Type[T]): The type into which to parse the data. This
            can be a Pydantic model class or any valid Python type (including
            complex types like List[int], Dict[str, Any], etc.).

    Returns:
        T: An instance of the expected type, validated and parsed from the JSON.

    Raises:
        ValueError: If the JSON is malformed or if the data fails validation.
    """
    if issubclass(expected_type, BaseModel):
        result = expected_type.model_validate(obj)
        
        return result
    
    # Validate and convert the data to the expected type
    result = TypeAdapter(expected_type).validate_python(obj)

    return result


def parse_data(data: BaseModel | Any) -> str:
    """
    Parses data to json serializable value, it expects any plain value & pydantic

    Args:
        data (Any): Data either pydantic model or plain value

    Returns:
        str: JSON object
    """
    if isinstance(data, BaseModel):
        return data.model_dump_json()
    
    return json.dumps(data)


def decode_message(response: bytes | str | dict | None) -> Any:
    """
    Decode a message that may be provided as bytes, a JSON string, or already as a dict.
    
    Args:
        response: The raw response.
        
    Returns:
        A JSON-decoded object if possible; otherwise, the original response.
    """
    if response is None:
        return None
    if isinstance(response, dict):
        # Already decoded
        return response
    if isinstance(response, bytes):
        try:
            response = response.decode("utf-8")
        except Exception as e:
            # Log or handle the decode error as needed.
            return response
    try:
        return json.loads(response)
    except (json.JSONDecodeError, TypeError):
        # If it’s not valid JSON, return as is.
        return response