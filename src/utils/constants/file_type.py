from enum import Enum


class FileType(Enum):
    PDF = "application/pdf"
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JPEG = "image/jpeg"
    PNG = "image/png"
    JSON = "application/json"
    CSV = "text/csv"


ALLOWED_FILE_TYPES = [filetype.value for filetype in FileType]
FILE_TYPE = {filetype.name: filetype.value for filetype in FileType}
