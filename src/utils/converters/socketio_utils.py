import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, List, Union
from types import MappingProxyType
from bson import ObjectId
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SocketIOSerializer:
    """
    Utility class for serializing data for Socket.IO emission.
    Handles common serialization issues like datetime, ObjectId, Decimal, Enum, etc.
    """

    @staticmethod
    def serialize_value(value: Any) -> Any:
        """
        Serialize a single value for JSON compatibility.
        """
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        elif isinstance(value, set):
            return list(value)
        elif isinstance(value, MappingProxyType):
            return SocketIOSerializer.serialize_dict(dict(value))
        elif isinstance(value, Enum):
            return value.value
        elif hasattr(value, "dict"):
            return SocketIOSerializer.serialize_dict(value.dict())
        elif hasattr(value, "__dict__"):
            return SocketIOSerializer.serialize_dict(value.__dict__)
        else:
            return value

    @staticmethod
    def serialize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize a dictionary recursively.
        """
        if not isinstance(data, dict):
            return SocketIOSerializer.serialize_value(data)

        serialized = {}
        for key, value in data.items():
            if isinstance(value, dict):
                serialized[key] = SocketIOSerializer.serialize_dict(value)
            elif isinstance(value, list):
                serialized[key] = SocketIOSerializer.serialize_list(value)
            else:
                serialized[key] = SocketIOSerializer.serialize_value(value)

        return serialized

    @staticmethod
    def serialize_list(data: List[Any]) -> List[Any]:
        """
        Serialize a list recursively.
        """
        if not isinstance(data, list):
            return SocketIOSerializer.serialize_value(data)

        serialized = []
        for item in data:
            if isinstance(item, dict):
                serialized.append(SocketIOSerializer.serialize_dict(item))
            elif isinstance(item, list):
                serialized.append(SocketIOSerializer.serialize_list(item))
            else:
                serialized.append(SocketIOSerializer.serialize_value(item))

        return serialized

    @staticmethod
    def prepare_for_emission(data: Any) -> Any:
        """
        Main method to prepare any data structure for Socket.IO emission.
        """
        try:
            if isinstance(data, dict):
                return SocketIOSerializer.serialize_dict(data)
            elif isinstance(data, list):
                return SocketIOSerializer.serialize_list(data)
            else:
                return SocketIOSerializer.serialize_value(data)
        except Exception as e:
            logger.error(f"Failed to serialize data for Socket.IO: {e}")
            return {
                "error": True,
                "message": "Data serialization failed",
                "original_type": str(type(data).__name__),
                "timestamp": datetime.now().isoformat(),
            }

    @staticmethod
    def safe_emit_data(data: Any) -> Dict[str, Any]:
        """
        Create a safe, serializable version of data with metadata.
        """
        try:
            serialized_data = SocketIOSerializer.prepare_for_emission(data)
            return {
                "success": True,
                "data": serialized_data,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to create safe emit data: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }


def prepare_message_for_socket(message: Any) -> Any:
    """
    Prepare a message for Socket.IO emission.
    """
    return SocketIOSerializer.prepare_for_emission(message)


def safe_socket_emit(sio, event: str, data: Any, **kwargs) -> bool:
    """
    Safely emit data via Socket.IO with automatic serialization.
    """
    try:
        serialized_data = SocketIOSerializer.prepare_for_emission(data)
        sio.emit(event, serialized_data, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Failed to emit Socket.IO event '{event}': {e}")
        return False


async def async_safe_socket_emit(sio, event: str, data: Any, **kwargs) -> bool:
    """
    Safely emit data via Socket.IO with automatic serialization (async).
    """
    try:
        serialized_data = SocketIOSerializer.prepare_for_emission(data)
        await sio.emit(event, serialized_data, **kwargs)
        return True
    except Exception as e:
        logger.error(f"Failed to emit Socket.IO event '{event}': {e}")
        return False
