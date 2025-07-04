from enum import Enum


class FileType(Enum):
    PDF = "application/pdf"
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    PPTX = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    JPEG = "image/jpeg"
    PNG = "image/png"
    JSON = "application/json"
    CSV = ("text/csv",)
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    TXT = "text/plain"
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    PY = "application/octet-stream"
    JS = "application/javascript"
    TS = "application/typescript"
    JAVA = "text/x-java-source"
    CPP = "text/x-c++src"
    C = "text/x-csrc"
    GO = "text/x-go"
    RB = "application/x-ruby"
    PHP = "application/x-httpd-php"
    SWIFT = "text/swift"
    KOTLIN = "text/x-kotlin"
    SH = "application/x-sh"
    SQL = "application/sql"
    XML = "application/xml"
    YAML = "application/x-yaml"


ALLOWED_FILE_TYPES = [filetype.value for filetype in FileType]
FILE_TYPE = {filetype.name: filetype.value for filetype in FileType}
