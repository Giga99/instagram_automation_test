"""
Logger Module

Handles structured logging of comment posting activities in JSON or CSV format.
"""

import json
import csv
import os
import shutil
from typing import Optional, List, Dict, Any
from datetime import datetime

# Configuration constant for log format
LOG_FORMAT = "json"  # Change to "csv" for CSV format

# Global variable to track the current log file path
_current_log_path: Optional[str] = None


def init_logger(output_path: str) -> None:
    """
    Initializes the logger by creating the output file with appropriate headers.
    
    Args:
        output_path: Path to the output log file
    """
    global _current_log_path
    _current_log_path = output_path
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not os.path.exists(output_path):
        if LOG_FORMAT.lower() == "json":
            # Initialize with empty JSON array
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
            print(f"📝 Initialized JSON log file: {output_path}")
        elif LOG_FORMAT.lower() == "csv":
            # Initialize with CSV header
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['profile_id', 'timestamp', 'comment', 'error'])
            print(f"📝 Initialized CSV log file: {output_path}")
        else:
            raise ValueError(f"Unsupported log format: {LOG_FORMAT}")
    else:
        print(f"📁 Using existing log file: {output_path}")


def write_log_entry(profile_id: str, comment_text: str, timestamp: str, error: Optional[str] = None) -> None:
    """
    Writes a log entry to the output file using atomic operations.
    
    Args:
        profile_id: Profile identifier (e.g., 'profile1')
        comment_text: The posted comment text
        timestamp: ISO 8601 UTC timestamp with 'Z' suffix
        error: Optional error message if the operation failed
    """
    # Use configured log path or fallback to default
    log_path = _current_log_path or ("output/comments_log.json" if LOG_FORMAT.lower() == "json" else "output/comments_log.csv")
    
    if LOG_FORMAT.lower() == "json":
        _write_json_entry(log_path, profile_id, comment_text, timestamp, error)
    elif LOG_FORMAT.lower() == "csv":
        _write_csv_entry(log_path, profile_id, comment_text, timestamp, error)
    else:
        raise ValueError(f"Unsupported log format: {LOG_FORMAT}")


def _write_json_entry(log_path: str, profile_id: str, comment_text: str, timestamp: str, error: Optional[str]) -> None:
    """
    Writes a JSON log entry using atomic file operations.
    """
    try:
        # Read existing data
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Create new entry
        entry = {
            "profile_id": profile_id,
            "timestamp": timestamp,
            "comment": comment_text,
            "error": error
        }
        
        # Add new entry
        data.append(entry)
        
        # Write atomically using temporary file
        temp_path = log_path + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic move
        shutil.move(temp_path, log_path)
        
        status = "❌ ERROR" if error else "✅ SUCCESS"
        print(f"📝 Logged [{profile_id}] {status}: {comment_text[:50]}{'...' if len(comment_text) > 50 else ''}")
        
    except Exception as e:
        print(f"❌ Failed to write JSON log entry: {e}")
        # Ensure temp file is cleaned up
        temp_path = log_path + '.tmp'
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def _write_csv_entry(log_path: str, profile_id: str, comment_text: str, timestamp: str, error: Optional[str]) -> None:
    """
    Writes a CSV log entry by appending to the file.
    """
    try:
        # For CSV, we can simply append since it's naturally atomic for single writes
        with open(log_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([profile_id, timestamp, comment_text, error or ''])
        
        status = "❌ ERROR" if error else "✅ SUCCESS"
        print(f"📝 Logged [{profile_id}] {status}: {comment_text[:50]}{'...' if len(comment_text) > 50 else ''}")
        
    except Exception as e:
        print(f"❌ Failed to write CSV log entry: {e}")
        raise


def get_current_timestamp() -> str:
    """
    Returns current UTC timestamp in ISO 8601 format with 'Z' suffix.
    
    Returns:
        Timestamp string (e.g., '2025-06-07T12:34:56Z')
    """
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def read_log_entries(log_path: str) -> List[Dict[str, Any]]:
    """
    Reads and returns all log entries from the specified log file.
    
    Args:
        log_path: Path to the log file
        
    Returns:
        List of log entries as dictionaries
    """
    if not os.path.exists(log_path):
        return []
    
    try:
        if log_path.endswith('.json'):
            with open(log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif log_path.endswith('.csv'):
            entries = []
            with open(log_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert empty strings to None for error field
                    if row.get('error') == '':
                        row['error'] = None
                    entries.append(row)
            return entries
        else:
            raise ValueError(f"Unsupported file format: {log_path}")
    except Exception as e:
        print(f"❌ Failed to read log entries from {log_path}: {e}")
        return []


def get_log_summary(log_path: str) -> Dict[str, Any]:
    """
    Returns a summary of log entries including success/error counts.
    
    Args:
        log_path: Path to the log file
        
    Returns:
        Dictionary with summary statistics
    """
    entries = read_log_entries(log_path)
    
    total = len(entries)
    success_count = sum(1 for entry in entries if not entry.get('error'))
    error_count = total - success_count
    
    profiles = set(entry.get('profile_id', 'unknown') for entry in entries)
    
    return {
        "total_entries": total,
        "successful": success_count,
        "errors": error_count,
        "success_rate": f"{(success_count/total*100):.1f}%" if total > 0 else "0%",
        "profiles_processed": list(profiles),
        "latest_timestamp": entries[-1].get('timestamp') if entries else None
    }


def get_current_log_path() -> Optional[str]:
    """
    Returns the currently configured log file path.
    
    Returns:
        Current log file path or None if not set
    """
    return _current_log_path 