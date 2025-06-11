#!/usr/bin/env python3
"""
Unit Tests for Notifier Module

Tests all functionality of the src/integrations/telegram/notifier.py module including:
- Telegram API integration (mocked)
- Message formatting
- Retry logic and error handling
- Different notification types
"""

import os
# Add project root to path for imports
import sys
import unittest
from unittest.mock import patch, Mock

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.telegram.notifier import (
    TelegramNotifier, send_telegram, send_completion_notification, send_error_notification,
    send_progress_notification, validate_telegram_credentials, test_telegram_notification
)


class TestNotifierModule(unittest.TestCase):
    """Test cases for the notifier module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_bot_token = "test-bot-token"
        self.test_chat_id = "test-chat-id"
        self.test_message = "Test message"

    def tearDown(self):
        """Clean up after each test method."""
        pass

    @patch('requests.post')
    def test_send_telegram_success(self, mock_post):
        """Test successful Telegram message sending."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {"message_id": 123}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test
        send_telegram(self.test_bot_token, self.test_chat_id, self.test_message)

        # Verify
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        expected_url = f"https://api.telegram.org/bot{self.test_bot_token}/sendMessage"
        self.assertEqual(call_args[0][0], expected_url)

        # Check payload
        payload = call_args[1]['json']
        self.assertEqual(payload['chat_id'], self.test_chat_id)
        self.assertEqual(payload['text'], self.test_message)
        self.assertEqual(payload['parse_mode'], 'HTML')

    @patch('requests.post')
    def test_send_telegram_api_error(self, mock_post):
        """Test Telegram API error response."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Bad Request: chat not found"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test
        with patch('time.sleep'):  # Speed up test
            with self.assertRaises(Exception) as cm:
                send_telegram(self.test_bot_token, self.test_chat_id, self.test_message, max_retries=1)

        # Check that the final error message is about failed attempts
        self.assertIn("Failed to send Telegram notification after 1 attempts", str(cm.exception))

    @patch('requests.post')
    def test_send_telegram_network_error(self, mock_post):
        """Test network error handling."""
        # Setup mock to raise network error
        mock_post.side_effect = requests.exceptions.RequestException("Network error")

        # Test
        with patch('time.sleep'):  # Speed up test
            with self.assertRaises(Exception) as cm:
                send_telegram(self.test_bot_token, self.test_chat_id, self.test_message, max_retries=1)

        self.assertIn("Failed to send Telegram notification after 1 attempts", str(cm.exception))

    @patch('requests.post')
    def test_send_telegram_retry_logic(self, mock_post):
        """Test retry logic on failures."""
        # Setup mock to fail twice then succeed
        mock_responses = [
            requests.exceptions.RequestException("Error 1"),
            requests.exceptions.RequestException("Error 2"),
            Mock(json=lambda: {"ok": True, "result": {"message_id": 123}}, raise_for_status=lambda: None)
        ]
        mock_post.side_effect = mock_responses

        # Test
        with patch('time.sleep'):  # Speed up test
            send_telegram(self.test_bot_token, self.test_chat_id, self.test_message, max_retries=3)

        # Verify retry count
        self.assertEqual(mock_post.call_count, 3)

    def test_send_telegram_missing_credentials(self):
        """Test sending telegram with missing credentials."""
        # Test missing bot token - can fail in two ways:
        # 1. Early validation: "Telegram credentials required"
        # 2. After retries: "Failed to send Telegram notification after"
        with self.assertRaises(Exception) as cm:
            send_telegram("", self.test_chat_id, self.test_message)

        exception_msg = str(cm.exception)
        self.assertTrue(
            "Failed to send Telegram notification after" in exception_msg or
            "Telegram credentials required" in exception_msg,
            f"Unexpected error message: {exception_msg}"
        )

        # Test missing chat ID - can fail in two ways:
        # 1. Early validation: "Telegram credentials required"  
        # 2. After retries: "Failed to send Telegram notification after"
        with self.assertRaises(Exception) as cm:
            send_telegram(self.test_bot_token, "", self.test_message)

        exception_msg = str(cm.exception)
        self.assertTrue(
            "Failed to send Telegram notification after" in exception_msg or
            "Telegram credentials required" in exception_msg,
            f"Unexpected error message: {exception_msg}"
        )

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_completion')
    def test_send_completion_notification(self, mock_send):
        """Test sending completion notification with summary."""
        # Test data
        summary = {
            "total_entries": 5,
            "successful": 3,
            "errors": 2,
            "success_rate": "60.0%",
            "profiles_processed": ["profile1", "profile2", "profile3"],
            "latest_timestamp": "2025-06-06T12:00:00Z"
        }

        # Test
        send_completion_notification(summary)

        # Verify
        mock_send.assert_called_once_with(summary)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_send_completion_notification_fallback(self, mock_send):
        """Test completion notification fallback on failure."""
        # Setup mock to fail first, succeed on fallback
        mock_send.side_effect = [
            Exception("Primary send failed"),
            None  # Fallback succeeds
        ]

        summary = {"total_entries": 0, "successful": 0, "errors": 0, "success_rate": "0%", "profiles_processed": [],
                   "latest_timestamp": None}

        # Test
        send_completion_notification(summary)

        # Verify fallback was called
        self.assertEqual(mock_send.call_count, 2)

        # Check fallback message
        fallback_call = mock_send.call_args_list[1]
        fallback_message = fallback_call[0][0]
        self.assertIn("Instagram automation completed", fallback_message)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_send_completion_notification_double_failure(self, mock_send):
        """Test completion notification when both primary and fallback fail."""
        # Setup mock to always fail
        mock_send.side_effect = Exception("Always fails")

        summary = {"total_entries": 0, "successful": 0, "errors": 0, "success_rate": "0%", "profiles_processed": [],
                   "latest_timestamp": None}

        # Test - should raise exception after fallback fails
        with self.assertRaises(Exception):
            send_completion_notification(summary)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_error')
    def test_send_error_notification(self, mock_send):
        """Test sending error notification."""
        error_message = "Login failed for user"
        profile_id = "profile1"

        # Test with profile ID
        send_error_notification(error_message, profile_id)

        # Verify
        mock_send.assert_called_once_with(error_message, profile_id)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_error')
    def test_send_error_notification_no_profile(self, mock_send):
        """Test sending error notification without profile ID."""
        error_message = "General error occurred"

        # Test without profile ID
        send_error_notification(error_message)

        # Verify
        mock_send.assert_called_once_with(error_message, None)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_progress')
    def test_send_progress_notification(self, mock_send):
        """Test sending progress notification."""
        profile_id = "profile1"
        status = "Login successful"
        comment = "Great workout session! 💪"

        # Test with comment
        send_progress_notification(profile_id, status, comment)

        # Verify
        mock_send.assert_called_once_with(profile_id, status, comment)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_progress')
    def test_send_progress_notification_no_comment(self, mock_send):
        """Test sending progress notification without comment."""
        profile_id = "profile2"
        status = "Login failed"

        # Test without comment
        send_progress_notification(profile_id, status)

        # Verify
        mock_send.assert_called_once_with(profile_id, status, None)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_send_progress_notification_long_comment(self, mock_send):
        """Test progress notification with long comment truncation."""
        profile_id = "profile1"
        status = "Comment posted"
        long_comment = "A" * 150  # Long comment

        # Test
        send_progress_notification(profile_id, status, long_comment)

        # Verify comment is truncated
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        message = call_args[0]

        self.assertIn("Comment:", message)
        self.assertIn("...", message)  # Truncation indicator

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.validate_credentials')
    def test_validate_telegram_credentials_success(self, mock_validate):
        """Test successful credential validation."""
        mock_validate.return_value = True

        # Test
        result = validate_telegram_credentials()

        # Verify
        self.assertTrue(result)
        mock_validate.assert_called_once()

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier.validate_credentials')
    def test_validate_telegram_credentials_failure(self, mock_validate):
        """Test credential validation failure."""
        mock_validate.return_value = False

        # Test
        result = validate_telegram_credentials()

        # Verify
        self.assertFalse(result)

    @patch('requests.get')
    def test_get_bot_info_success(self, mock_get):
        """Test successful bot info retrieval."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": True,
            "result": {
                "first_name": "TestBot",
                "username": "test_bot"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create notifier with explicit credentials
        notifier = TelegramNotifier(bot_token=self.test_bot_token, chat_id=self.test_chat_id)

        # Test
        result = notifier.get_bot_info()

        # Verify
        self.assertIsNotNone(result)
        self.assertEqual(result["first_name"], "TestBot")
        self.assertEqual(result["username"], "test_bot")

        # Check API call
        expected_url = f"https://api.telegram.org/bot{self.test_bot_token}/getMe"
        mock_get.assert_called_once_with(expected_url, timeout=10)

    @patch('requests.get')
    def test_get_bot_info_api_error(self, mock_get):
        """Test bot info retrieval with API error."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "ok": False,
            "description": "Unauthorized"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Create notifier with explicit credentials
        notifier = TelegramNotifier(bot_token=self.test_bot_token, chat_id=self.test_chat_id)

        # Test
        result = notifier.get_bot_info()

        # Verify
        self.assertIsNone(result)

    @patch('requests.get')
    def test_get_bot_info_network_error(self, mock_get):
        """Test bot info retrieval with network error."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        # Create notifier with explicit credentials
        notifier = TelegramNotifier(bot_token=self.test_bot_token, chat_id=self.test_chat_id)

        # Test
        result = notifier.get_bot_info()

        # Verify
        self.assertIsNone(result)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    @patch('src.integrations.telegram.notifier.TelegramNotifier.send_completion')
    def test_test_telegram_notification_success(self, mock_completion, mock_send):
        """Test the test_telegram_notification function success case."""
        # Setup mocks
        mock_send.return_value = None
        mock_completion.return_value = None

        # Test
        result = test_telegram_notification()

        # Verify
        self.assertTrue(result)
        mock_send.assert_called_once()
        mock_completion.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    def test_test_telegram_notification_no_credentials(self):
        """Test the test_telegram_notification function without credentials."""
        # Test
        result = test_telegram_notification()

        # Verify
        self.assertFalse(result)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_test_telegram_notification_failure(self, mock_send):
        """Test the test_telegram_notification function with failure."""
        # Setup mock to fail
        mock_send.side_effect = Exception("Send failed")

        # Test
        result = test_telegram_notification()

        # Verify
        self.assertFalse(result)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_completion_notification_empty_profiles(self, mock_send):
        """Test completion notification with empty profiles list."""
        summary = {
            "total_entries": 0,
            "successful": 0,
            "errors": 0,
            "success_rate": "0%",
            "profiles_processed": [],
            "latest_timestamp": None
        }

        send_completion_notification(summary)

        # Check message content
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        message = call_args[0]
        self.assertIn("No profiles processed", message)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_html_formatting_in_messages(self, mock_send):
        """Test that messages use proper HTML formatting."""
        # Test error notification
        send_error_notification("Test error", "profile1")

        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        message = call_args[0]

        # Check HTML tags
        self.assertIn("<b>", message)
        self.assertIn("</b>", message)

    @patch.dict(os.environ, {'TG_BOT_TOKEN': 'test-token', 'TG_CHAT_ID': 'test-chat'})
    @patch('src.integrations.telegram.notifier.TelegramNotifier._send_message')
    def test_notification_error_handling(self, mock_send):
        """Test error handling in notification functions."""
        # Test that exceptions in send_telegram are caught and logged
        mock_send.side_effect = Exception("Send failed")

        # These should not raise exceptions
        send_error_notification("Error")
        send_progress_notification("profile1", "Status")

        # Verify send_telegram was called despite failures
        self.assertEqual(mock_send.call_count, 2)


def run_notifier_tests():
    """Run all notifier tests and return results."""
    print("🧪 Running Notifier Module Tests...")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNotifierModule)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Notifier Tests Summary:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(
        f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_notifier_tests()
