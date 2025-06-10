"""
Utility Functions

Common utility functions used across the Instagram automation project.
"""

import logging
from datetime import datetime
from typing import Optional, Any

logger = logging.getLogger(__name__)


def parse_timestamp(timestamp: Optional[Any]) -> Optional[datetime]:
    """
    Parse timestamp from various sources to datetime object.
    
    Handles multiple timestamp formats commonly used in APIs:
    - Unix timestamps (int/float seconds since epoch)
    - String representations of Unix timestamps
    - ISO format datetime strings
    
    Args:
        timestamp: Timestamp value (can be int, str, float, or None)
        
    Returns:
        datetime object or None if parsing fails
        
    Examples:
        >>> parse_timestamp(1642262400)  # Unix timestamp
        datetime.datetime(2022, 1, 15, 16, 0)
        
        >>> parse_timestamp("1642262400")  # Unix timestamp as string
        datetime.datetime(2022, 1, 15, 16, 0)
        
        >>> parse_timestamp("2022-01-15T16:00:00Z")  # ISO format
        datetime.datetime(2022, 1, 15, 16, 0)
        
        >>> parse_timestamp(None)  # None input
        None
    """
    if not timestamp:
        return None
    
    try:
        # Handle Unix timestamp (seconds since epoch)
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp)
        
        # Handle string timestamp
        if isinstance(timestamp, str):
            # Try to convert to int first (Unix timestamp as string)
            try:
                return datetime.fromtimestamp(int(timestamp))
            except ValueError:
                # Try ISO format parsing
                try:
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Could not parse timestamp: {timestamp}")
                    return None
        
        logger.warning(f"Unknown timestamp format: {timestamp} (type: {type(timestamp)})")
        return None
        
    except Exception as e:
        logger.warning(f"Failed to parse timestamp {timestamp}: {str(e)}")
        return None


def format_datetime_for_display(dt: Optional[datetime], default: str = "Unknown") -> str:
    """
    Format datetime object for user-friendly display.
    
    Args:
        dt: datetime object to format
        default: Default string to return if dt is None
        
    Returns:
        Formatted datetime string or default value
        
    Examples:
        >>> dt = datetime(2022, 1, 15, 16, 30, 45)
        >>> format_datetime_for_display(dt)
        "2022-01-15 16:30:45"
        
        >>> format_datetime_for_display(None)
        "Unknown"
        
        >>> format_datetime_for_display(None, "Never")
        "Never"
    """
    if dt is None:
        return default
    
    try:
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logger.warning(f"Failed to format datetime {dt}: {str(e)}")
        return default


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with optional default.
    
    Args:
        dictionary: Dictionary to get value from
        key: Key to lookup
        default: Default value if key not found or value is None
        
    Returns:
        Value from dictionary or default
        
    Examples:
        >>> data = {"name": "profile1", "count": 0, "empty": None}
        >>> safe_get(data, "name")
        "profile1"
        
        >>> safe_get(data, "missing", "default")
        "default"
        
        >>> safe_get(data, "empty", "fallback")
        "fallback"
    """
    try:
        value = dictionary.get(key, default)
        return value if value is not None else default
    except Exception as e:
        logger.warning(f"Failed to get key '{key}' from dictionary: {str(e)}")
        return default 