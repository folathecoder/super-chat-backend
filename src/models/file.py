from dataclasses import dataclass


@dataclass
class FileData:
    filename: str
    content: bytes
    content_type: str
