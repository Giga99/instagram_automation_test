#!/usr/bin/env python3
"""
Unit Tests for Logger Module

Tests all functionality of the src/utils/logger.py module including:
- JSON and CSV logging
- Atomic file operations
- Log reading and summarization
- Error handling and edge cases
"""

import csv
import json
import os
import shutil
# Add project root to path for imports
import sys
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logger import (
    init_logger, write_log_entry, get_current_timestamp,
    read_log_entries, get_log_summary, get_current_log_path
)


class TestLoggerModule(unittest.TestCase):
    """Test cases for the logger module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.json_log_path = os.path.join(self.test_dir, "test_log.json")
        self.csv_log_path = os.path.join(self.test_dir, "test_log.csv")

        # Reset global state
        import src.utils.logger
        src.utils.logger._current_log_path = None

    def tearDown(self):
        """Clean up after each test method."""
        # Remove the temporary directory and all contents
        shutil.rmtree(self.test_dir, ignore_errors=True)

        # Reset global state
        import src.utils.logger
        src.utils.logger._current_log_path = None

    def test_init_logger_json_new_file(self):
        """Test initializing a new JSON log file."""
        # Test with JSON format
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            # Check file was created
            self.assertTrue(os.path.exists(self.json_log_path))

            # Check file content is empty JSON array
            with open(self.json_log_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data, [])

            # Check global path was set
            self.assertEqual(get_current_log_path(), self.json_log_path)

    def test_init_logger_csv_new_file(self):
        """Test initializing a new CSV log file."""
        # Test with CSV format
        with patch('src.utils.logger.LOG_FORMAT', 'csv'):
            init_logger(self.csv_log_path)

            # Check file was created
            self.assertTrue(os.path.exists(self.csv_log_path))

            # Check CSV header
            with open(self.csv_log_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)
                self.assertEqual(header, ['profile_id', 'timestamp', 'comment', 'error'])

    def test_init_logger_existing_file(self):
        """Test initializing with an existing log file."""
        # Create existing file
        with open(self.json_log_path, 'w') as f:
            json.dump([{"test": "data"}], f)

        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            # Check file content wasn't overwritten
            with open(self.json_log_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(data, [{"test": "data"}])

    def test_write_log_entry_json_success(self):
        """Test writing a successful log entry in JSON format."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            timestamp = get_current_timestamp()
            write_log_entry("profile1", "Test comment 💪", timestamp)

            # Read and verify
            with open(self.json_log_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['profile_id'], "profile1")
                self.assertEqual(data[0]['comment'], "Test comment 💪")
                self.assertEqual(data[0]['timestamp'], timestamp)
                self.assertIsNone(data[0]['error'])

    def test_write_log_entry_json_error(self):
        """Test writing an error log entry in JSON format."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            timestamp = get_current_timestamp()
            error_msg = "Network timeout"
            write_log_entry("profile2", "Failed comment", timestamp, error_msg)

            # Read and verify
            with open(self.json_log_path, 'r') as f:
                data = json.load(f)
                self.assertEqual(len(data), 1)
                self.assertEqual(data[0]['profile_id'], "profile2")
                self.assertEqual(data[0]['error'], error_msg)

    def test_write_log_entry_csv_success(self):
        """Test writing a successful log entry in CSV format."""
        with patch('src.utils.logger.LOG_FORMAT', 'csv'):
            init_logger(self.csv_log_path)

            timestamp = get_current_timestamp()
            write_log_entry("profile1", "Test comment", timestamp)

            # Read and verify
            entries = read_log_entries(self.csv_log_path)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['profile_id'], "profile1")
            self.assertEqual(entries[0]['comment'], "Test comment")
            self.assertIsNone(entries[0]['error'])

    def test_write_multiple_entries(self):
        """Test writing multiple log entries."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            # Write multiple entries
            timestamp = get_current_timestamp()
            write_log_entry("profile1", "Comment 1", timestamp)
            write_log_entry("profile2", "Comment 2", timestamp, "Some error")
            write_log_entry("profile3", "Comment 3", timestamp)

            # Verify all entries
            entries = read_log_entries(self.json_log_path)
            self.assertEqual(len(entries), 3)
            self.assertEqual(entries[0]['profile_id'], "profile1")
            self.assertEqual(entries[1]['profile_id'], "profile2")
            self.assertEqual(entries[2]['profile_id'], "profile3")
            self.assertIsNone(entries[0]['error'])
            self.assertEqual(entries[1]['error'], "Some error")

    def test_read_log_entries_nonexistent_file(self):
        """Test reading from a non-existent log file."""
        entries = read_log_entries("nonexistent.json")
        self.assertEqual(entries, [])

    def test_read_log_entries_json(self):
        """Test reading JSON log entries."""
        # Create test data
        test_data = [
            {"profile_id": "profile1", "timestamp": "2025-01-01T00:00:00Z", "comment": "Test", "error": None},
            {"profile_id": "profile2", "timestamp": "2025-01-01T00:01:00Z", "comment": "Test2", "error": "Error"}
        ]

        with open(self.json_log_path, 'w') as f:
            json.dump(test_data, f)

        entries = read_log_entries(self.json_log_path)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['profile_id'], "profile1")
        self.assertEqual(entries[1]['error'], "Error")

    def test_read_log_entries_csv(self):
        """Test reading CSV log entries."""
        # Create test CSV
        with open(self.csv_log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['profile_id', 'timestamp', 'comment', 'error'])
            writer.writerow(['profile1', '2025-01-01T00:00:00Z', 'Test', ''])
            writer.writerow(['profile2', '2025-01-01T00:01:00Z', 'Test2', 'Error'])

        entries = read_log_entries(self.csv_log_path)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['profile_id'], "profile1")
        self.assertIsNone(entries[0]['error'])  # Empty string converted to None
        self.assertEqual(entries[1]['error'], "Error")

    def test_get_log_summary_empty(self):
        """Test getting summary for empty log."""
        summary = get_log_summary("nonexistent.json")
        self.assertEqual(summary['total_entries'], 0)
        self.assertEqual(summary['successful'], 0)
        self.assertEqual(summary['errors'], 0)
        self.assertEqual(summary['success_rate'], "0%")
        self.assertEqual(summary['profiles_processed'], [])
        self.assertIsNone(summary['latest_timestamp'])

    def test_get_log_summary_with_data(self):
        """Test getting summary with actual log data."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            timestamp1 = "2025-01-01T00:00:00Z"
            timestamp2 = "2025-01-01T00:01:00Z"
            timestamp3 = "2025-01-01T00:02:00Z"

            write_log_entry("profile1", "Success 1", timestamp1)
            write_log_entry("profile2", "Failed", timestamp2, "Error message")
            write_log_entry("profile1", "Success 2", timestamp3)

            summary = get_log_summary(self.json_log_path)
            self.assertEqual(summary['total_entries'], 3)
            self.assertEqual(summary['successful'], 2)
            self.assertEqual(summary['errors'], 1)
            self.assertEqual(summary['success_rate'], "66.7%")
            self.assertIn("profile1", summary['profiles_processed'])
            self.assertIn("profile2", summary['profiles_processed'])
            self.assertEqual(summary['latest_timestamp'], timestamp3)

    def test_get_current_timestamp_format(self):
        """Test timestamp format is correct."""
        timestamp = get_current_timestamp()

        # Check format: YYYY-MM-DDTHH:MM:SSZ
        self.assertRegex(timestamp, r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

        # Check it's a valid datetime
        datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')

    def test_unsupported_log_format(self):
        """Test handling of unsupported log format."""
        with patch('src.utils.logger.LOG_FORMAT', 'xml'):
            with self.assertRaises(ValueError):
                init_logger(self.json_log_path)

    def test_atomic_write_json_failure_cleanup(self):
        """Test that temporary files are cleaned up on write failure."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            # Mock json.dump to raise an exception
            with patch('json.dump', side_effect=Exception("Write failed")):
                with self.assertRaises(Exception):
                    write_log_entry("profile1", "Test", get_current_timestamp())

                # Check no temporary file exists
                temp_file = self.json_log_path + '.tmp'
                self.assertFalse(os.path.exists(temp_file))

    def test_directory_creation(self):
        """Test that logger creates necessary directories."""
        nested_path = os.path.join(self.test_dir, "nested", "deep", "log.json")

        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(nested_path)

            self.assertTrue(os.path.exists(nested_path))
            self.assertTrue(os.path.isdir(os.path.dirname(nested_path)))

    def test_unicode_support(self):
        """Test that logger handles Unicode characters correctly."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            unicode_comment = "Great workout! 💪🔥 Ça va bien! 中文测试"
            timestamp = get_current_timestamp()
            write_log_entry("profile1", unicode_comment, timestamp)

            # Read back and verify
            entries = read_log_entries(self.json_log_path)
            self.assertEqual(entries[0]['comment'], unicode_comment)

    def test_long_comment_truncation_in_log_message(self):
        """Test that long comments are truncated in console output."""
        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            init_logger(self.json_log_path)

            long_comment = "A" * 100  # 100 characters
            timestamp = get_current_timestamp()

            # Capture stdout to check truncation
            with patch('builtins.print') as mock_print:
                write_log_entry("profile1", long_comment, timestamp)

                # Check that print was called with truncated message
                call_args = str(mock_print.call_args)
                self.assertIn("...", call_args)  # Truncation indicator

    def test_fallback_log_path(self):
        """Test fallback to default log path when no path is set."""
        # Reset global path
        import src.utils.logger
        src.utils.logger._current_log_path = None

        with patch('src.utils.logger.LOG_FORMAT', 'json'):
            # Should use default path since no path is set
            timestamp = get_current_timestamp()

            # Create output directory for default path
            os.makedirs("output", exist_ok=True)

            write_log_entry("profile1", "Test comment", timestamp)

            # Check default file was created
            self.assertTrue(os.path.exists("output/comments_log.json"))


def run_logger_tests():
    """Run all logger tests and return results."""
    print("🧪 Running Logger Module Tests...")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLoggerModule)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Logger Tests Summary:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(
        f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_logger_tests()
