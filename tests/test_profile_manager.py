#!/usr/bin/env python3
"""
Unit Tests for Profile Manager Module

Tests all functionality of the modules/profile_manager.py module including:
- Browser context creation and management
- Instagram login automation (mocked)
- Login completion handling
- Error scenarios and recovery
- Session management and cleanup
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, Mock, MagicMock
from unittest.mock import call

# Add project root to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.profile_manager import (
    create_browser_context, login_profile, is_already_logged_in,
    wait_for_login_completion, navigate_to_post, close_context,
    get_profile_info
)


class TestProfileManagerModule(unittest.TestCase):
    """Test cases for the Profile Manager module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_profile_id = "test_profile"
        self.test_username = "test_user"
        self.test_password = "test_pass"
        self.test_post_url = "https://www.instagram.com/p/TEST123/"
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('modules.profile_manager.os.makedirs')
    def test_create_browser_context_success(self, mock_makedirs):
        """Test successful browser context creation."""
        # Setup
        mock_playwright = Mock()
        mock_browser = Mock()
        mock_context = Mock()
        
        mock_playwright.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        
        # Test
        result = create_browser_context(mock_playwright, self.test_profile_id, headless=True)
        
        # Verify
        self.assertEqual(result, mock_context)
        mock_makedirs.assert_called_once()
        mock_playwright.chromium.launch.assert_called_once()
        mock_browser.new_context.assert_called_once()
        
        # Check launch arguments include headless and security settings
        launch_args = mock_playwright.chromium.launch.call_args
        self.assertTrue(launch_args[1]['headless'])
        self.assertIn('--no-sandbox', launch_args[1]['args'])
    
    @patch('modules.profile_manager.create_browser_context')
    def test_login_profile_missing_credentials(self, mock_create_context):
        """Test login with missing credentials."""
        mock_playwright = Mock()
        
        # Test with missing username
        result = login_profile(mock_playwright, self.test_profile_id, "", self.test_password)
        self.assertIsNone(result)
        mock_create_context.assert_not_called()
        
        # Test with missing password
        result = login_profile(mock_playwright, self.test_profile_id, self.test_username, "")
        self.assertIsNone(result)
        mock_create_context.assert_not_called()
    
    @patch('modules.profile_manager.wait_for_login_completion')
    @patch('modules.profile_manager.is_already_logged_in')
    @patch('modules.profile_manager.create_browser_context')
    def test_login_profile_already_logged_in(self, mock_create_context, mock_is_logged_in, mock_wait_login):
        """Test login when user is already logged in."""
        # Setup
        mock_playwright = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_create_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_is_logged_in.return_value = True
        
        # Test
        result = login_profile(
            mock_playwright, self.test_profile_id, 
            self.test_username, self.test_password
        )
        
        # Verify
        self.assertEqual(result, mock_context)
        mock_page.goto.assert_called_once_with("https://www.instagram.com/accounts/login/", timeout=30000)
        mock_page.wait_for_selector.assert_called_once_with('input[name="username"]', timeout=10000)
        mock_is_logged_in.assert_called_once_with(mock_page)
        mock_wait_login.assert_not_called()  # Should not wait if already logged in
    
    @patch('modules.profile_manager.wait_for_login_completion')
    @patch('modules.profile_manager.is_already_logged_in')
    @patch('modules.profile_manager.create_browser_context')
    def test_login_profile_successful_login(self, mock_create_context, mock_is_logged_in, mock_wait_login):
        """Test successful login process."""
        # Setup
        mock_playwright = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_create_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_is_logged_in.return_value = False
        mock_wait_login.return_value = True
        
        # Test
        result = login_profile(
            mock_playwright, self.test_profile_id,
            self.test_username, self.test_password
        )
        
        # Verify
        self.assertEqual(result, mock_context)
        mock_page.fill.assert_any_call('input[name="username"]', self.test_username)
        mock_page.fill.assert_any_call('input[name="password"]', self.test_password)
        mock_page.click.assert_called_with('button[type="submit"]')
        mock_wait_login.assert_called_once_with(mock_page, self.test_profile_id)
    
    @patch('modules.profile_manager.wait_for_login_completion')
    @patch('modules.profile_manager.is_already_logged_in')
    @patch('modules.profile_manager.create_browser_context')
    def test_login_profile_login_failure(self, mock_create_context, mock_is_logged_in, mock_wait_login):
        """Test login failure and retry logic."""
        # Setup
        mock_playwright = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_create_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_is_logged_in.return_value = False
        mock_wait_login.return_value = False  # Login fails
        
        # Test with max_retries=1 to speed up test
        result = login_profile(
            mock_playwright, self.test_profile_id,
            self.test_username, self.test_password,
            max_retries=1
        )
        
        # Verify
        self.assertIsNone(result)
        mock_context.close.assert_called_once()
    
    @patch('modules.profile_manager.time.sleep')  # Mock sleep to speed up test
    @patch('modules.profile_manager.wait_for_login_completion')
    @patch('modules.profile_manager.is_already_logged_in')
    @patch('modules.profile_manager.create_browser_context')
    def test_login_profile_retry_with_success(self, mock_create_context, mock_is_logged_in, 
                                            mock_wait_login, mock_sleep):
        """Test retry logic with eventual success."""
        # Setup
        mock_playwright = Mock()
        mock_context = Mock()
        mock_page = Mock()
        
        mock_create_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_is_logged_in.return_value = False
        # Fail first attempt, succeed second
        mock_wait_login.side_effect = [False, True]
        
        # Test
        result = login_profile(
            mock_playwright, self.test_profile_id,
            self.test_username, self.test_password,
            max_retries=2
        )
        
        # Verify
        self.assertEqual(result, mock_context)
        self.assertEqual(mock_wait_login.call_count, 2)
        mock_sleep.assert_called_once_with(1)  # Exponential backoff: 2^0 = 1
    
    def test_is_already_logged_in_true(self):
        """Test detecting already logged in state."""
        mock_page = Mock()
        mock_page.wait_for_selector.return_value = Mock()  # Found home icon
        
        result = is_already_logged_in(mock_page)
        
        self.assertTrue(result)
        mock_page.wait_for_selector.assert_called_with('svg[aria-label="Home"]', timeout=3000)
    
    def test_is_already_logged_in_false(self):
        """Test detecting not logged in state."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.wait_for_selector.side_effect = PlaywrightTimeoutError("Not found")
        
        result = is_already_logged_in(mock_page)
        
        self.assertFalse(result)
    
    @patch('modules.profile_manager.time.time')
    @patch('modules.profile_manager.time.sleep')
    def test_wait_for_login_completion_success(self, mock_sleep, mock_time):
        """Test successful login completion detection."""
        # Setup time progression
        mock_time.side_effect = [0, 1, 2]  # Simulate time passing
        
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.is_visible.return_value = True
        mock_page.locator.return_value = mock_locator
        
        # Test
        result = wait_for_login_completion(mock_page, self.test_profile_id)
        
        # Verify
        self.assertTrue(result)
        mock_page.locator.assert_called_with('svg[aria-label="Home"]')
    
    @patch('modules.profile_manager.time.time')
    @patch('modules.profile_manager.time.sleep')
    def test_wait_for_login_completion_save_login_dialog(self, mock_sleep, mock_time):
        """Test handling 'Save Login Info' dialog."""
        # Setup time progression
        mock_time.side_effect = [0, 1, 2, 3]
        
        mock_page = Mock()
        mock_home_locator = Mock()
        mock_save_locator = Mock()
        
        # First check: save dialog visible, second check: home visible
        mock_home_locator.is_visible.side_effect = [False, True]
        mock_save_locator.is_visible.side_effect = [True, False]
        
        def locator_side_effect(selector):
            if 'Home' in selector:
                return mock_home_locator
            elif 'Save Your Login Info' in selector:
                return mock_save_locator
            return Mock()
        
        mock_page.locator.side_effect = locator_side_effect
        
        # Test
        result = wait_for_login_completion(mock_page, self.test_profile_id, timeout=5000)
        
        # Verify
        self.assertTrue(result)
        mock_page.click.assert_called_with('text="Not Now"')
    
    @patch('modules.profile_manager.time.time')
    def test_wait_for_login_completion_timeout(self, mock_time):
        """Test login completion timeout."""
        # Setup time progression to exceed timeout
        mock_time.side_effect = [0, 20]  # Simulate 20 seconds passing (timeout is 15)
        
        mock_page = Mock()
        mock_locator = Mock()
        mock_locator.is_visible.return_value = False
        mock_page.locator.return_value = mock_locator
        
        # Test
        result = wait_for_login_completion(mock_page, self.test_profile_id, timeout=15000)
        
        # Verify
        self.assertFalse(result)
    
    def test_navigate_to_post_success(self):
        """Test successful post navigation."""
        mock_page = Mock()
        
        result = navigate_to_post(mock_page, self.test_post_url)
        
        self.assertTrue(result)
        mock_page.goto.assert_called_once_with(self.test_post_url, timeout=15000)
        mock_page.wait_for_selector.assert_called_once_with('article', timeout=10000)
    
    def test_navigate_to_post_timeout(self):
        """Test post navigation timeout."""
        mock_page = Mock()
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")
        
        result = navigate_to_post(mock_page, self.test_post_url)
        
        self.assertFalse(result)
    
    def test_close_context_success(self):
        """Test successful context closure."""
        mock_context = Mock()
        
        # Should not raise exception
        close_context(mock_context)
        
        mock_context.close.assert_called_once()
    
    def test_close_context_none(self):
        """Test closing None context."""
        # Should not raise exception
        close_context(None)
    
    def test_close_context_error(self):
        """Test context closure with error."""
        mock_context = Mock()
        mock_context.close.side_effect = Exception("Close failed")
        
        # Should not raise exception
        close_context(mock_context)
        
        mock_context.close.assert_called_once()
    
    def test_get_profile_info_success(self):
        """Test successful profile info retrieval."""
        mock_context = Mock()
        mock_page = Mock()
        mock_context.new_page.return_value = mock_page
        
        result = get_profile_info(mock_context)
        
        self.assertEqual(result["status"], "logged_in")
        mock_page.goto.assert_called_once()
        mock_page.close.assert_called_once()
    
    def test_get_profile_info_error(self):
        """Test profile info retrieval with error."""
        mock_context = Mock()
        mock_context.new_page.side_effect = Exception("Page creation failed")
        
        result = get_profile_info(mock_context)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main() 