from io import BytesIO
from typing import Any, Iterable

from fastapi import UploadFile
from pydantic import BaseModel

from ascender.common.http.types.file import FileData


class FormData:
    """A form data container for HTTP multipart/form-data requests.
    
    This class provides an interface similar to the JavaScript FormData API for building
    multipart form data. It supports string values and file uploads via FileData.
    
    Note:
        UploadFile values cannot be passed directly to the constructor. They must be added
        using the append() or set() methods, which handle the conversion to FileData internally.
    """
    
    def __init__(self, **entries: str | FileData) -> None:
        """Initialize FormData with key-value pairs.
        
        Args:
            **entries: Key-value pairs where values can be strings or FileData objects.
                Note: UploadFile values are not accepted here. Use append() or set() instead.
        """
        self.fields = entries
    
    def append_from_dto(self, data: BaseModel) -> None:
        self.fields.update(data.model_dump(mode="json"))
    
    def append(self, name: str, value: str | FileData | UploadFile) -> None:
        if isinstance(value, UploadFile):
            if not value.content_type or not value.filename:
                raise ValueError("UploadFile must have content_type and filename")

            file_content = value.file.read()
            file_data = FileData(
                filename=value.filename,
                content_type=value.content_type,
                content=BytesIO(file_content)
            )
            self.fields[name] = file_data
            return
        
        self.fields[name] = value
    
    def entries(self) -> Iterable[tuple[str, Any]]:
        return iter(self.fields.items())
    
    def get(self, name: str) -> str | FileData | None:
        return self.fields.get(name)
    
    def get_all(self) -> dict[str, str | FileData]:
        return self.fields.copy()
    
    def has(self, name: str) -> bool:
        return name in self.fields
    
    def keys(self) -> Iterable[str]:
        return self.fields.keys()
    
    def set(self, name: str, value: str | FileData | UploadFile) -> None:
        self.append(name, value)
    
    def values(self) -> Iterable[Any]:
        return self.fields.values()
    
    def delete(self, name: str) -> None:
        if name in self.fields:
            del self.fields[name]
    
    def _construct(self):
        files: dict[str, Any] = {}
        data: dict[str, Any] = {}
        
        for key, value in self.fields.items():
            if isinstance(value, FileData):
                files[key] = value.construct()
            else:
                data[key] = str(value)
        
        return {
            "data": data,
            "files": files
        }