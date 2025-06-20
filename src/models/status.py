from enum import Enum


class Status(str, Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"

    def __str__(self):
        return self.value

    @classmethod
    def list(cls):
        return [status.value for status in cls]
