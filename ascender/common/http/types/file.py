from io import BytesIO


class FileData:
    def __init__(self, filename: str, content: bytes | BytesIO, content_type: str) -> None:
        self.filename = filename
        self.content = content
        self.content_type = content_type
    
    def seek(self, position: int) -> None:
        if isinstance(self.content, BytesIO):
            self.content.seek(position)
    
    def construct(self) -> tuple[str, bytes | BytesIO, str]:
        return (self.filename, self.content, self.content_type)