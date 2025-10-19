import json
from typing import Any

from pydantic import BaseModel

from ascender.common.microservices.utils.data_parser import parse_data


def parse_redis_encodable(
    correlationId: str | None = None, 
    data: Any | BaseModel | None = None
) -> bytes:
    """
    Prepares and serializes data into the Ascender framework's Redis message format.
    
    The standardized message format is:
        {
            "key": <provided key>,
            "data": <serialized data>
        }
    
    If `data` is a Pydantic model, it is converted using its built-in JSON dump method.
    Otherwise, the raw data is included (if provided) or defaults to None.

    Args:
        key (Optional[str]): An optional key to include in the message payload.
        data (Union[Any, BaseModel, None]): The payload data, which may be a Pydantic model or any JSON-serializable value.

    Returns:
        bytes: The payload serialized as a JSON string and encoded into bytes.
    """
    # Serialize the data if it is a Pydantic model; otherwise use it directly.
    if isinstance(data, BaseModel):
        # In some cases you might prefer model_dump_json() instead,
        # but here we use model_dump with JSON mode for consistency.
        serialized_data = data.model_dump(mode="json")
    else:
        serialized_data = data if data is not None else None

    # Build the payload dictionary in the expected format.
    payload = {
        "correlationId": correlationId,
        "payload": serialized_data
    }

    # Serialize the payload to a JSON string and then encode it to bytes.
    json_str = parse_data(payload)
    return json_str.encode()


def decode_redis_data(data: bytes | str | int | float | None) -> dict[str, Any]:
    """
    Decodes data received from Redis pubsub and converts it into the Ascender framework's 
    standardized pubsub message format.

    The function accepts data in several formats:
      - If `data` is bytes or a string, it will attempt to decode and parse it as JSON.
      - If JSON parsing is successful and the resulting object is a dict that contains both 
        'key' and 'data', it is returned as is.
      - Otherwise, the data is wrapped in a dictionary with 'key' set to None.

    Args:
        data (Union[bytes, str, int, float, None]): Data received from Redis pubsub.

    Returns:
        Dict[str, Any]: A dictionary in the format {'key': <key_value>, 'data': <data_payload>}.
    """
    # Handle bytes or string: decode if needed and try to load as JSON.
    if isinstance(data, (bytes, str)):
        # Decode bytes to string if needed.
        data_str = data.decode() if isinstance(data, bytes) else data

        try:
            # Attempt to parse the string as JSON.
            parsed_data = json.loads(data_str)
        except json.JSONDecodeError:
            # If JSON parsing fails, fallback to returning the original string.
            return {"correlationId": None, "payload": data_str}

        # Use the parsed JSON data for further processing.
        data = parsed_data

    # If data is a dictionary and already contains the expected keys, return it as is.
    if isinstance(data, dict):
        if "correlationId" in data and "payload" in data:
            return data
        else:
            # Even if it's a dict, standardize the output format by wrapping it.
            return {"correlationId": None, "payload": data}

    # For any other type (e.g. int, float, None), wrap it in the default structure.
    return {"correlationId": None, "payload": data}