#!/usr/bin/env python3
"""
AdsPower Profile Manager Module Tests

Tests for the AdsPower profile manager functionality including:
- Profile login and session management
- Browser context creation and cleanup
- Instagram authentication workflows
- Credential fallback mechanisms
- Basic functionality testing
"""

import unittest
from unittest.mock import Mock, patch

from src.integrations.adspower.client import AdsPowerProfile
# Import the modules to test
from src.integrations.adspower.profile_manager import AdsPowerProfileManager


class TestAdsPowerProfileManager(unittest.TestCase):
    """Test cases for AdsPowerProfileManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = AdsPowerProfileManager()
        self.test_profile_id = "test_profile_123"
        self.test_username = "test_user"
        self.test_password = "test_pass"

        # Mock Playwright objects
        self.mock_playwright = Mock()
        self.mock_browser = Mock()
        self.mock_context = Mock()
        self.mock_page = Mock()

        # Set up mock relationships
        self.mock_browser.contexts = [self.mock_context]
        self.mock_context.pages = [self.mock_page]
        self.mock_context.new_page.return_value = self.mock_page
        self.mock_playwright.chromium.connect_over_cdp.return_value = self.mock_browser

    def test_init_default_params(self):
        """Test manager initialization with default parameters."""
        manager = AdsPowerProfileManager()
        self.assertEqual(manager.adspower_client.base_url, "http://localhost:50325")
        self.assertIsNone(manager.adspower_client.api_key)
        self.assertTrue(manager.allow_credential_fallback)
        self.assertEqual(manager.credential_fallback_timeout, 60)

    def test_init_custom_params(self):
        """Test manager initialization with custom parameters."""
        manager = AdsPowerProfileManager(
            adspower_base_url="http://localhost:8080",
            adspower_api_key="test_key",
            allow_credential_fallback=False,
            credential_fallback_timeout=30
        )
        self.assertEqual(manager.adspower_client.base_url, "http://localhost:8080")
        self.assertEqual(manager.adspower_client.api_key, "test_key")
        self.assertFalse(manager.allow_credential_fallback)
        self.assertEqual(manager.credential_fallback_timeout, 30)

    @patch('src.integrations.adspower.profile_manager.AdsPowerClient')
    def test_check_adspower_connection_success(self, mock_client_class):
        """Test successful AdsPower connection check."""
        mock_client = Mock()
        mock_client.check_connection.return_value = True
        mock_client_class.return_value = mock_client

        manager = AdsPowerProfileManager()
        result = manager.check_adspower_connection()
        self.assertTrue(result)

    @patch('src.integrations.adspower.profile_manager.AdsPowerClient')
    def test_check_adspower_connection_failure(self, mock_client_class):
        """Test failed AdsPower connection check."""
        mock_client = Mock()
        mock_client.check_connection.return_value = False
        mock_client_class.return_value = mock_client

        manager = AdsPowerProfileManager()
        result = manager.check_adspower_connection()
        self.assertFalse(result)

    @patch('src.integrations.adspower.profile_manager.AdsPowerClient')
    def test_get_available_profiles(self, mock_client_class):
        """Test getting available profiles."""
        sample_profiles = [
            AdsPowerProfile(
                profile_id="profile_001",
                name="Test Profile 1",
                username="user1",
                password="pass1"
            ),
            AdsPowerProfile(
                profile_id="profile_002",
                name="Test Profile 2",
                username="user2",
                password="pass2"
            )
        ]

        mock_client = Mock()
        mock_client.get_profiles.return_value = sample_profiles
        mock_client_class.return_value = mock_client

        manager = AdsPowerProfileManager()
        profiles = manager.get_available_profiles()

        self.assertEqual(len(profiles), 2)
        self.assertEqual(profiles[0].profile_id, "profile_001")
        self.assertEqual(profiles[1].profile_id, "profile_002")

    def test_login_profile_adspower_start_failed(self):
        """Test login when AdsPower profile start fails."""
        with patch.object(self.manager, 'check_adspower_connection', return_value=True):
            with patch.object(self.manager.adspower_client, 'start_profile', return_value=None):
                result = self.manager.login_profile(
                    self.mock_playwright, self.test_profile_id,
                    self.test_username, self.test_password
                )
                self.assertIsNone(result)

    def test_login_profile_browser_connection_failed(self):
        """Test login when browser connection fails."""
        browser_data = {"ws": {"puppeteer": "ws://localhost:9222"}}

        with patch.object(self.manager, 'check_adspower_connection', return_value=True):
            with patch.object(self.manager.adspower_client, 'start_profile', return_value=browser_data):
                with patch.object(self.manager, '_connect_playwright_to_adspower', return_value=None):
                    result = self.manager.login_profile(
                        self.mock_playwright, self.test_profile_id,
                        self.test_username, self.test_password
                    )
                    self.assertIsNone(result)

    def test_close_context_success(self):
        """Test successful context closure."""
        # Add a context to active contexts
        self.manager.active_contexts[self.test_profile_id] = self.mock_context

        with patch.object(self.manager.adspower_client, 'stop_profile', return_value=True):
            self.manager.close_context(self.test_profile_id)

            # Verify context was removed
            self.assertNotIn(self.test_profile_id, self.manager.active_contexts)

    def test_close_context_not_found(self):
        """Test closing context that doesn't exist."""
        with patch.object(self.manager.adspower_client, 'stop_profile', return_value=True):
            # Should not raise an exception
            self.manager.close_context("non_existent_profile")

    def test_close_context_error_handling(self):
        """Test context closure with errors."""
        self.manager.active_contexts[self.test_profile_id] = self.mock_context
        self.mock_context.close.side_effect = Exception("Close error")

        with patch.object(self.manager.adspower_client, 'stop_profile', return_value=True):
            # Should handle the exception gracefully
            self.manager.close_context(self.test_profile_id)

    def test_cleanup_all_contexts(self):
        """Test cleanup of all active contexts."""
        # Add multiple contexts
        self.manager.active_contexts["profile_1"] = Mock()
        self.manager.active_contexts["profile_2"] = Mock()

        with patch.object(self.manager.adspower_client, 'stop_profile', return_value=True):
            self.manager.cleanup_all_contexts()

            # Verify all contexts were removed
            self.assertEqual(len(self.manager.active_contexts), 0)

    def test_get_profile_status(self):
        """Test getting profile status."""
        with patch.object(self.manager.adspower_client, 'check_profile_status', return_value="Active"):
            status = self.manager.get_profile_status(self.test_profile_id)
            self.assertEqual(status, "Active")


if __name__ == '__main__':
    unittest.main()
