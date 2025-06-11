#!/usr/bin/env python3
"""
Unit Tests for Comment Generation Module

Tests all functionality of the src/integrations/openai/comment_gen.py module including:
- OpenAI API integration (mocked)
- Comment validation
- Comment variations
- Error handling and retry logic
"""

import os
# Add project root to path for imports
import sys
import unittest
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.integrations.openai.comment_gen import (
    generate_comment, generate_multiple_comments, validate_comment,
    get_comment_variations, test_comment_generation
)


class TestCommentGenModule(unittest.TestCase):
    """Test cases for the comment generation module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock environment variable for API key
        self.api_key_patcher = patch.dict(os.environ, {'OPENAI_API_KEY': 'test-api-key'})
        self.api_key_patcher.start()

    def tearDown(self):
        """Clean up after each test method."""
        self.api_key_patcher.stop()

    def test_validate_comment_valid_cases(self):
        """Test comment validation with valid comments."""
        valid_comments = [
            "Great workout! 💪",
            "Amazing session today",
            "Keep pushing forward! 🔥",
            "Nice progress dude",
            "Loving the dedication"
        ]

        for comment in valid_comments:
            with self.subTest(comment=comment):
                self.assertTrue(validate_comment(comment), f"Comment should be valid: {comment}")

    def test_validate_comment_invalid_cases(self):
        """Test comment validation with invalid comments."""
        invalid_comments = [
            "",  # Empty
            "x",  # Too short
            "spam",  # Banned word
            "advertisement here",  # Banned word
            "fake post",  # Banned word
            "A" * 200,  # Too long
            None,  # None value
            123,  # Not a string
        ]

        for comment in invalid_comments:
            with self.subTest(comment=comment):
                self.assertFalse(validate_comment(comment), f"Comment should be invalid: {comment}")

    def test_validate_comment_length_bounds(self):
        """Test comment validation length boundaries."""
        # Test exact boundaries
        self.assertTrue(validate_comment("A" * 5))  # Minimum length
        self.assertTrue(validate_comment("A" * 150))  # Maximum length
        self.assertFalse(validate_comment("A" * 4))  # Below minimum
        self.assertFalse(validate_comment("A" * 151))  # Above maximum

    def test_validate_comment_custom_lengths(self):
        """Test comment validation with custom length parameters."""
        # Custom length validation
        self.assertTrue(validate_comment("Short", max_length=10, min_length=3))
        self.assertFalse(validate_comment("Short", max_length=4, min_length=3))
        self.assertFalse(validate_comment("Hi", max_length=10, min_length=3))

    def test_get_comment_variations_default(self):
        """Test getting comment variations with default prompt."""
        variations = get_comment_variations()

        self.assertIsInstance(variations, list)
        self.assertGreater(len(variations), 0)
        self.assertIn("gym selfie", variations)
        self.assertIn("motivational gym selfie", variations)
        self.assertIn("fitness gym selfie", variations)

    def test_get_comment_variations_custom(self):
        """Test getting comment variations with custom prompt."""
        custom_prompt = "running photo"
        variations = get_comment_variations(custom_prompt)

        self.assertIsInstance(variations, list)
        self.assertIn(custom_prompt, variations)
        self.assertIn(f"motivational {custom_prompt}", variations)
        self.assertIn(f"inspiring {custom_prompt}", variations)

    @patch('src.integrations.openai.comment_gen.OpenAI')
    def test_generate_comment_success(self, mock_openai_class):
        """Test successful comment generation."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Great workout session! 💪"
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        result = generate_comment("gym selfie")

        # Verify
        self.assertEqual(result, "Great workout session! 💪")
        mock_client.chat.completions.create.assert_called_once()

        # Check call arguments
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args[1]['model'], 'gpt-4o-mini')
        self.assertEqual(len(call_args[1]['messages']), 2)
        self.assertEqual(call_args[1]['messages'][0]['role'], 'system')
        self.assertEqual(call_args[1]['messages'][1]['role'], 'user')

    @patch('src.integrations.openai.comment_gen.OpenAI')
    def test_generate_comment_with_quotes_cleanup(self, mock_openai_class):
        """Test comment generation with quote cleanup."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '"Great workout session! 💪"'  # With quotes
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        result = generate_comment("gym selfie")

        # Verify quotes are stripped
        self.assertEqual(result, "Great workout session! 💪")

    @patch('src.integrations.openai.comment_gen.OpenAI')
    def test_generate_comment_retry_logic(self, mock_openai_class):
        """Test comment generation retry logic on failure."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # First two calls fail, third succeeds
        mock_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            Mock(choices=[Mock(message=Mock(content="Success! 💪"))])
        ]

        # Test with patched sleep to speed up test
        with patch('time.sleep'):
            result = generate_comment("gym selfie", max_retries=3)

        # Verify
        self.assertEqual(result, "Success! 💪")
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)

    @patch('src.integrations.openai.comment_gen.OpenAI')
    def test_generate_comment_max_retries_exceeded(self, mock_openai_class):
        """Test comment generation when max retries are exceeded."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Persistent error")

        # Test
        with patch('time.sleep'):  # Speed up test
            with self.assertRaises(Exception) as cm:
                generate_comment("gym selfie", max_retries=2)

        # Verify error message includes retry information
        self.assertIn("Failed to generate comment after 2 attempts", str(cm.exception))

    @patch('src.integrations.openai.comment_gen.OpenAI')
    def test_generate_comment_empty_response(self, mock_openai_class):
        """Test comment generation with empty API response."""
        # Setup mock
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = []  # Empty choices
        mock_client.chat.completions.create.return_value = mock_response

        # Test
        with patch('time.sleep'):
            with self.assertRaises(Exception) as cm:
                generate_comment("gym selfie", max_retries=1)

        self.assertIn("Empty response from OpenAI API", str(cm.exception))

    def test_generate_comment_no_api_key(self):
        """Test comment generation without API key."""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment
            with self.assertRaises(ValueError) as cm:
                generate_comment("gym selfie")

            self.assertIn("OPENAI_API_KEY environment variable is not set", str(cm.exception))

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_generate_multiple_comments_success(self, mock_generate):
        """Test generating multiple unique comments."""
        # Setup mock to return different comments
        mock_generate.side_effect = [
            "Comment 1 💪",
            "Comment 2 🔥",
            "Comment 3 ⚡"
        ]

        # Test
        result = generate_multiple_comments("gym selfie", count=3)

        # Verify
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "Comment 1 💪")
        self.assertEqual(result[1], "Comment 2 🔥")
        self.assertEqual(result[2], "Comment 3 ⚡")
        self.assertEqual(mock_generate.call_count, 3)

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_generate_multiple_comments_with_duplicates(self, mock_generate):
        """Test generating multiple comments with duplicate handling."""
        # Setup mock to return duplicate then unique comments
        mock_generate.side_effect = [
            "Comment 1 💪",
            "Comment 1 💪",  # Duplicate
            "Comment 2 🔥",  # Unique
        ]

        # Test
        result = generate_multiple_comments("gym selfie", count=2, ensure_unique=True)

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Comment 1 💪")
        self.assertEqual(result[1], "Comment 2 🔥")
        self.assertEqual(mock_generate.call_count, 3)  # Called 3 times due to duplicate

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_generate_multiple_comments_allow_duplicates(self, mock_generate):
        """Test generating multiple comments allowing duplicates."""
        # Setup mock to return same comment
        mock_generate.return_value = "Same comment 💪"

        # Test
        result = generate_multiple_comments("gym selfie", count=2, ensure_unique=False)

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Same comment 💪")
        self.assertEqual(result[1], "Same comment 💪")
        self.assertEqual(mock_generate.call_count, 2)

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_generate_multiple_comments_with_failures(self, mock_generate):
        """Test generating multiple comments with some failures."""
        # Setup mock with failures
        mock_generate.side_effect = [
            Exception("API Error"),
            "Comment 1 💪",
            Exception("Another error"),
            "Comment 2 🔥"
        ]

        # Test
        result = generate_multiple_comments("gym selfie", count=2)

        # Verify
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], "Comment 1 💪")
        self.assertEqual(result[1], "Comment 2 🔥")

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_generate_multiple_comments_max_attempts(self, mock_generate):
        """Test generating multiple comments hitting max attempts."""
        # Setup mock to always fail
        mock_generate.side_effect = Exception("Persistent error")

        # Test
        result = generate_multiple_comments("gym selfie", count=3)

        # Verify we get empty result after max attempts
        self.assertEqual(len(result), 0)

    @patch('src.integrations.openai.comment_gen.generate_comment')
    @patch('src.integrations.openai.comment_gen.validate_comment')
    def test_test_comment_generation_function(self, mock_validate, mock_generate):
        """Test the test_comment_generation function."""
        # Setup mocks
        mock_generate.side_effect = [
            "Test comment 💪",  # Single comment
            "Multi comment 1 🔥",  # Multiple comments
            "Multi comment 2 ⚡"
        ]
        mock_validate.return_value = True

        # Test
        with patch('src.integrations.openai.comment_gen.generate_multiple_comments') as mock_multi:
            mock_multi.return_value = ["Comment 1", "Comment 2"]
            result = test_comment_generation()

        # Verify
        self.assertTrue(result)
        mock_generate.assert_called()
        mock_validate.assert_called()

    @patch('src.integrations.openai.comment_gen.generate_comment')
    def test_test_comment_generation_function_failure(self, mock_generate):
        """Test the test_comment_generation function with failure."""
        # Setup mock to fail
        mock_generate.side_effect = Exception("Test failure")

        # Test
        result = test_comment_generation()

        # Verify
        self.assertFalse(result)

    def test_unicode_handling_in_validation(self):
        """Test that validation handles Unicode characters properly."""
        unicode_comments = [
            "Great workout! 💪🔥",
            "Ça va bien! Nice session",
            "中文测试 workout",
            "Спорт это жизнь! 💪"
        ]

        for comment in unicode_comments:
            with self.subTest(comment=comment):
                # Should handle Unicode without errors
                result = validate_comment(comment)
                self.assertIsInstance(result, bool)

    def test_banned_words_case_insensitive(self):
        """Test that banned words detection is case insensitive."""
        banned_variations = [
            "This is SPAM content",
            "Fake news here",
            "BOT generated text",
            "Advertisement for sale"
        ]

        for comment in banned_variations:
            with self.subTest(comment=comment):
                self.assertFalse(validate_comment(comment))

    def test_validate_comment_whitespace_handling(self):
        """Test comment validation handles whitespace correctly."""
        # Whitespace should be stripped for length calculation
        self.assertTrue(validate_comment("  Valid comment  "))
        self.assertFalse(validate_comment("   x   "))  # Still too short after strip


def run_comment_gen_tests():
    """Run all comment generation tests and return results."""
    print("🧪 Running Comment Generation Module Tests...")
    print("=" * 50)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCommentGenModule)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Comment Generation Tests Summary:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(
        f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_comment_gen_tests()
