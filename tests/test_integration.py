#!/usr/bin/env python3
"""
Integration Tests for Instagram Automation Project

Tests how all modules work together in realistic scenarios.
"""

import os
import shutil
# Add project root to path for imports
import sys
import tempfile
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.logger import init_logger, write_log_entry, get_current_timestamp, get_log_summary
from modules.comment_gen import generate_comment, validate_comment
from modules.notifier import send_completion_notification


class TestIntegration(unittest.TestCase):
    """Integration test cases for the Instagram automation system."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.test_dir, "integration_test.json")
        self.test_bot_token = "test-bot-token"
        self.test_chat_id = "test-chat-id"

        # Reset global logger state
        import modules.logger
        modules.logger._current_log_path = None

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        import modules.logger
        modules.logger._current_log_path = None

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'})
    @patch('modules.comment_gen.OpenAI')
    @patch('modules.logger.LOG_FORMAT', 'json')
    def test_comment_generation_with_logging(self, mock_openai_class):
        """Test comment generation integrated with logging."""
        # Setup OpenAI mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Great workout! 💪 Keep it up!"
        mock_client.chat.completions.create.return_value = mock_response

        # Initialize logger and generate comment
        init_logger(self.log_path)
        comment = generate_comment("gym selfie")

        # Validate and log
        self.assertTrue(validate_comment(comment))
        timestamp = get_current_timestamp()
        write_log_entry("profile1", comment, timestamp)

        # Verify integration worked
        summary = get_log_summary(self.log_path)
        self.assertEqual(summary['total_entries'], 1)
        self.assertEqual(summary['successful'], 1)
        self.assertIn("profile1", summary['profiles_processed'])

    @patch('modules.logger.LOG_FORMAT', 'json')
    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('modules.notifier.TelegramNotifier._send_message')
    def test_logging_with_notification_workflow(self, mock_send_message):
        """Test complete logging to notification workflow."""
        # Initialize logger and simulate operations
        init_logger(self.log_path)
        timestamp = get_current_timestamp()

        write_log_entry("profile1", "Amazing workout! 💪", timestamp)
        write_log_entry("profile2", "Failed comment", timestamp, "Network timeout")
        write_log_entry("profile3", "Great progress! 🔥", timestamp)

        # Send notification
        summary = get_log_summary(self.log_path)
        send_completion_notification(summary)

        # Verify notification contains correct data
        mock_send_message.assert_called_once()
        call_args = mock_send_message.call_args[0]
        message = call_args[0]

        self.assertIn("Total Operations: 3", message)
        self.assertIn("Successful: 2", message)
        self.assertIn("Errors: 1", message)
        self.assertIn("Success Rate: 66.7%", message)

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key', 'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('modules.comment_gen.OpenAI')
    @patch('modules.logger.LOG_FORMAT', 'json')
    @patch('modules.notifier.TelegramNotifier._send_message')
    def test_full_workflow_simulation(self, mock_send_message, mock_openai_class):
        """Test complete workflow simulation with all modules."""
        # Setup OpenAI mock for multiple comments
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_responses = [
            Mock(choices=[Mock(message=Mock(content="Great session! 💪"))]),
            Exception("API Error"),  # Simulate failure
            Mock(choices=[Mock(message=Mock(content="Amazing work! ⚡"))])
        ]
        mock_client.chat.completions.create.side_effect = mock_responses

        # Initialize logger
        init_logger(self.log_path)

        # Simulate workflow for 3 profiles
        profiles = ["profile1", "profile2", "profile3"]
        for profile in profiles:
            try:
                with patch('time.sleep'):  # Speed up retries
                    comment = generate_comment("gym selfie", max_retries=1)

                if not validate_comment(comment):
                    raise ValueError("Invalid comment")

                timestamp = get_current_timestamp()
                write_log_entry(profile, comment, timestamp)

            except Exception as e:
                timestamp = get_current_timestamp()
                write_log_entry(profile, "", timestamp, str(e))

        # Send completion notification
        summary = get_log_summary(self.log_path)
        send_completion_notification(summary)

        # Verify results
        self.assertEqual(summary['total_entries'], 3)
        self.assertEqual(summary['successful'], 2)  # profile1 and profile3
        self.assertEqual(summary['errors'], 1)  # profile2
        mock_send_message.assert_called_once()


def run_integration_tests():
    """Run all integration tests and return results."""
    print("🧪 Running Integration Tests...")
    print("=" * 50)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 50)
    print(f"📊 Integration Tests Summary:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(
        f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_integration_tests()
