#!/usr/bin/env python3
"""
Unit Tests for Poster Module

Tests all functionality of the modules/poster.py module including:
- Comment posting functionality (mocked)
- Simulation mode testing
- DOM interaction and input detection
- Success verification and error handling
- Rate limiting and restriction detection
"""

import unittest
import os
import re
from unittest.mock import patch, Mock, MagicMock

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.poster import (
    post_comment, simulate_post, find_and_focus_comment_input,
    submit_comment, verify_comment_posted, check_comment_restrictions,
    get_post_info, wait_for_rate_limit_reset, POST_COMMENT
)


class TestPosterModule(unittest.TestCase):
    """Test cases for the Poster module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_comment = "Great workout! 💪 Keep it up!"
        self.test_post_url = "https://www.instagram.com/p/TEST123/"
        self.test_profile_id = "test_profile"
        
        # Mock context and page
        self.mock_context = Mock()
        self.mock_page = Mock()
        self.mock_context.new_page.return_value = self.mock_page
    
    @patch('modules.poster.POST_COMMENT', False)
    def test_post_comment_simulation_mode(self):
        """Test comment posting in simulation mode."""
        result = post_comment(self.mock_context, self.test_comment, self.test_post_url)
        
        self.assertTrue(result)
        # Should not create any pages in simulation mode
        self.mock_context.new_page.assert_not_called()
    
    @patch('modules.poster.POST_COMMENT', True)
    @patch('modules.poster.submit_comment')
    @patch('modules.poster.find_and_focus_comment_input')
    @patch('modules.poster.time.sleep')
    def test_post_comment_real_mode_success(self, mock_sleep, mock_find_input, mock_submit):
        """Test successful comment posting in real mode."""
        # Setup
        mock_find_input.return_value = True
        mock_submit.return_value = True
        
        # Test
        result = post_comment(self.mock_context, self.test_comment, self.test_post_url)
        
        # Verify
        self.assertTrue(result)
        self.mock_context.new_page.assert_called_once()
        self.mock_page.goto.assert_called_once_with(self.test_post_url, timeout=15000)
        self.mock_page.wait_for_selector.assert_called_once_with('article', timeout=10000)
        mock_find_input.assert_called_once_with(self.mock_page)
        self.mock_page.keyboard.type.assert_called_once_with(self.test_comment, delay=50)
        mock_submit.assert_called_once_with(self.mock_page)
        self.mock_page.close.assert_called_once()
    
    @patch('modules.poster.POST_COMMENT', True)
    def test_post_comment_empty_text(self):
        """Test posting with empty comment text."""
        result = post_comment(self.mock_context, "", self.test_post_url)
        
        self.assertFalse(result)
        self.mock_context.new_page.assert_not_called()
    
    @patch('modules.poster.POST_COMMENT', True)
    @patch('modules.poster.find_and_focus_comment_input')
    def test_post_comment_input_not_found(self, mock_find_input):
        """Test posting when comment input cannot be found."""
        mock_find_input.return_value = False
        
        result = post_comment(self.mock_context, self.test_comment, self.test_post_url)
        
        self.assertFalse(result)
        self.assertEqual(self.mock_page.close.call_count, 3)
    
    @patch('modules.poster.POST_COMMENT', True)
    @patch('modules.poster.time.sleep')
    @patch('modules.poster.submit_comment')
    @patch('modules.poster.find_and_focus_comment_input')
    def test_post_comment_retry_logic(self, mock_find_input, mock_submit, mock_sleep):
        """Test retry logic on failures."""
        # Setup: fail first attempt, succeed second
        mock_find_input.side_effect = [False, True]
        mock_submit.return_value = True
        
        # Test
        result = post_comment(self.mock_context, self.test_comment, max_retries=2)
        
        # Verify
        self.assertTrue(result)
        self.assertEqual(self.mock_context.new_page.call_count, 2)
        mock_sleep.assert_called_once_with(1)  # Exponential backoff: 2^0 = 1
    
    @patch('modules.poster.POST_COMMENT', True)
    @patch('modules.poster.find_and_focus_comment_input')
    def test_post_comment_all_retries_fail(self, mock_find_input):
        """Test when all retry attempts fail."""
        mock_find_input.return_value = False
        
        result = post_comment(self.mock_context, self.test_comment, max_retries=2)
        
        self.assertFalse(result)
        self.assertEqual(self.mock_context.new_page.call_count, 2)
    
    @patch('modules.poster.time.sleep')
    def test_simulate_post_success(self, mock_sleep):
        """Test simulation posting."""
        result = simulate_post(self.test_profile_id, self.test_comment, self.test_post_url)
        
        self.assertTrue(result)
        mock_sleep.assert_called_once_with(0.5)
    
    def test_simulate_post_without_url(self):
        """Test simulation posting without URL."""
        result = simulate_post(self.test_profile_id, self.test_comment)
        
        self.assertTrue(result)
    
    def test_find_and_focus_comment_input_success(self):
        """Test successful comment input detection."""
        mock_page = Mock()
        mock_element = Mock()
        mock_element.is_visible.return_value = True
        mock_page.wait_for_selector.return_value = mock_element
        
        result = find_and_focus_comment_input(mock_page)
        
        self.assertTrue(result)
        mock_element.click.assert_called_once()
    
    def test_find_and_focus_comment_input_not_found(self):
        """Test when comment input is not found."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Not found")
        
        result = find_and_focus_comment_input(mock_page)
        
        self.assertFalse(result)
    
    @patch('modules.poster.time.sleep')
    def test_find_and_focus_comment_input_click_area(self, mock_sleep):
        """Test finding input by clicking comment area."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        
        # First selector fails, second (comment area) succeeds, then input found
        mock_element = Mock()
        mock_element.is_visible.return_value = True
        
        def wait_for_selector_side_effect(selector, timeout=None):
            if 'textarea' in selector and timeout == 3000:
                raise PlaywrightTimeoutError("Not found")
            elif 'section:has(svg' in selector:
                return mock_element  # Comment area found
            elif 'textarea' in selector and timeout == 2000:
                return mock_element  # Input found after clicking
            raise PlaywrightTimeoutError("Not found")
        
        mock_page.wait_for_selector.side_effect = wait_for_selector_side_effect
        
        result = find_and_focus_comment_input(mock_page)
        
        self.assertTrue(result)
        mock_sleep.assert_called_once_with(1)
    
    @patch('modules.poster.verify_comment_posted')
    def test_submit_comment_button_success(self, mock_verify):
        """Test successful comment submission via button."""
        mock_page = Mock()
        mock_button = Mock()
        mock_button.is_visible.return_value = True
        mock_button.is_enabled.return_value = True
        mock_page.wait_for_selector.return_value = mock_button
        mock_verify.return_value = True
        
        result = submit_comment(mock_page)
        
        self.assertTrue(result)
        mock_button.click.assert_called_once()
        mock_verify.assert_called_once_with(mock_page)
    
    @patch('modules.poster.verify_comment_posted')
    def test_submit_comment_enter_key(self, mock_verify):
        """Test comment submission via Enter key."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Button not found")
        mock_verify.return_value = True
        
        result = submit_comment(mock_page)
        
        self.assertTrue(result)
        mock_page.keyboard.press.assert_called_once_with("Enter")
        mock_verify.assert_called_once_with(mock_page)
    
    def test_submit_comment_error(self):
        """Test comment submission with error."""
        mock_page = Mock()
        mock_page.wait_for_selector.side_effect = Exception("General error")
        
        result = submit_comment(mock_page)
        
        self.assertFalse(result)
    
    def test_verify_comment_posted_input_cleared(self):
        """Test comment verification by input clearing."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_first_input = Mock()
        mock_first_input.input_value.return_value = ""  # Input cleared
        mock_locator.count.return_value = 1
        mock_locator.first = mock_first_input
        mock_page.locator.return_value = mock_locator
        
        result = verify_comment_posted(mock_page)
        
        self.assertTrue(result)
    
    def test_verify_comment_posted_confirmation(self):
        """Test comment verification by confirmation message."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 0  # No inputs found
        mock_page.locator.return_value = mock_locator
        
        # Mock finding confirmation message
        mock_page.wait_for_selector.return_value = Mock()
        
        result = verify_comment_posted(mock_page)
        
        self.assertTrue(result)
    
    def test_verify_comment_posted_assume_success(self):
        """Test comment verification assuming success when no confirmation found."""
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.count.return_value = 0
        mock_page.locator.return_value = mock_locator
        
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Not found")
        
        result = verify_comment_posted(mock_page)
        
        self.assertTrue(result)  # Assumes success if no error indicators
    
    def test_check_comment_restrictions_restricted(self):
        """Test detecting comment restrictions."""
        mock_page = Mock()
        mock_page.wait_for_selector.return_value = Mock()  # Found restriction
        
        result = check_comment_restrictions(mock_page)
        
        self.assertTrue(result["restricted"])
        self.assertIn("message", result)
    
    def test_check_comment_restrictions_not_restricted(self):
        """Test when no restrictions are detected."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Not found")
        
        result = check_comment_restrictions(mock_page)
        
        self.assertFalse(result["restricted"])
    
    def test_check_comment_restrictions_error(self):
        """Test restriction checking with error."""
        mock_page = Mock()
        mock_page.wait_for_selector.side_effect = Exception("General error")
        
        result = check_comment_restrictions(mock_page)
        
        self.assertFalse(result["restricted"])
        self.assertIn("Error checking restrictions", result["message"])
    
    @patch('re.findall')
    def test_get_post_info_success(self, mock_findall):
        """Test successful post info extraction."""
        mock_page = Mock()
        mock_page.url = self.test_post_url
        
        # Mock comments section found
        mock_page.wait_for_selector.return_value = Mock()
        
        # Mock comment count element
        mock_locator = Mock()
        mock_locator.is_visible.return_value = True
        mock_locator.text_content.return_value = "23 comments"
        mock_page.locator.return_value = mock_locator
        
        # Mock regex to return the expected number
        mock_findall.return_value = ['23']
        
        result = get_post_info(mock_page)
        
        self.assertEqual(result["url"], self.test_post_url)
        self.assertTrue(result["has_comments"])
        self.assertEqual(result["comment_count"], 23)
    
    def test_get_post_info_no_comments(self):
        """Test post info when no comments section found."""
        mock_page = Mock()
        mock_page.url = self.test_post_url
        
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Not found")
        
        # Mock no comment count element
        mock_locator = Mock()
        mock_locator.is_visible.return_value = False
        mock_page.locator.return_value = mock_locator
        
        result = get_post_info(mock_page)
        
        self.assertEqual(result["url"], self.test_post_url)
        self.assertFalse(result["has_comments"])
        self.assertEqual(result["comment_count"], 0)
    
    def test_get_post_info_error(self):
        """Test post info extraction with error."""
        mock_page = Mock()
        mock_page.url = self.test_post_url
        mock_page.wait_for_selector.side_effect = Exception("General error")
        
        result = get_post_info(mock_page)
        
        self.assertIn("error", result)
    
    @patch('modules.poster.time.sleep')
    def test_wait_for_rate_limit_reset(self, mock_sleep):
        """Test rate limit reset waiting."""
        wait_for_rate_limit_reset(30)
        
        mock_sleep.assert_called_once_with(30)
    
    @patch('modules.poster.time.sleep')
    def test_wait_for_rate_limit_reset_default(self, mock_sleep):
        """Test rate limit reset with default time."""
        wait_for_rate_limit_reset()
        
        mock_sleep.assert_called_once_with(60)


if __name__ == '__main__':
    unittest.main() 