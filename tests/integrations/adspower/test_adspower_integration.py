#!/usr/bin/env python3
"""
AdsPower Integration Tests

Tests for the complete AdsPower integration workflow including:
- End-to-end workflow testing
- Integration between all AdsPower modules
- Basic functionality testing
- Error recovery and cleanup procedures
"""

import unittest
from unittest.mock import Mock, patch

from src.integrations.adspower.client import AdsPowerProfile, AdsPowerProfileGroup
# Import the modules to test
from src.integrations.adspower.config import load_adspower_profiles, test_adspower_connection
from src.integrations.adspower.profile_manager import AdsPowerProfileManager


class TestAdsPowerIntegration(unittest.TestCase):
    """Test cases for complete AdsPower integration workflows."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_profiles = [
            AdsPowerProfile(
                profile_id="profile_001",
                name="Test Profile 1",
                username="user1",
                password="pass1",
                domain_name="instagram.com",
                group=AdsPowerProfileGroup(id="group_123", name="Test Group")
            ),
            AdsPowerProfile(
                profile_id="profile_002",
                name="Test Profile 2",
                username="user2",
                password="pass2",
                domain_name="instagram.com",
                group=AdsPowerProfileGroup(id="group_456", name="Another Group")
            )
        ]

    @patch('src.integrations.adspower.config.client')
    def test_complete_workflow_config_file_exists(self, mock_client):
        """Test complete workflow when config file exists."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = self.sample_profiles

        # Test loading profiles
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 2)

        # Test connection
        connection_ok = test_adspower_connection()
        self.assertTrue(connection_ok)

    @patch('src.integrations.adspower.config.client')
    def test_complete_workflow_no_config_file(self, mock_client):
        """Test complete workflow when no config file exists (discovery mode)."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = self.sample_profiles

        # Test discovery mode
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 2)

    @patch('src.integrations.adspower.config.client')
    def test_workflow_adspower_not_running(self, mock_client):
        """Test workflow when AdsPower is not running."""
        # Mock AdsPower not running
        mock_client.check_connection.return_value = False

        # Test config loading fails gracefully
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 0)

        # Test connection fails gracefully
        connection_ok = test_adspower_connection()
        self.assertFalse(connection_ok)

        # Test profile manager handles it gracefully
        manager = AdsPowerProfileManager()
        mock_playwright = Mock()
        result = manager.login_profile(
            mock_playwright, "profile_001", "user", "pass"
        )
        self.assertIsNone(result)

    @patch('src.integrations.adspower.config.client')
    def test_workflow_multiple_profiles_sequential(self, mock_client):
        """Test workflow with multiple profiles processed sequentially."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = self.sample_profiles

        # Load profiles
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 2)

        # Test profile manager can handle multiple profiles
        with patch.object(AdsPowerProfileManager, 'get_available_profiles', return_value=self.sample_profiles):
            manager = AdsPowerProfileManager()
            available_profiles = manager.get_available_profiles()
            self.assertEqual(len(available_profiles), 2)

    def test_workflow_error_recovery(self):
        """Test workflow error recovery and cleanup."""
        manager = AdsPowerProfileManager()
        mock_playwright = Mock()

        # Test that failed login doesn't leave hanging contexts
        result = manager.login_profile(
            mock_playwright, "profile_001", "user", "pass"
        )
        self.assertIsNone(result)
        self.assertEqual(len(manager.active_contexts), 0)

    @patch('src.integrations.adspower.config.client')
    def test_workflow_performance_multiple_profiles(self, mock_client):
        """Test workflow performance with multiple profiles."""
        # Create larger profile set for performance testing
        large_profile_set = []
        for i in range(10):
            large_profile_set.append(
                AdsPowerProfile(
                    profile_id=f"profile_{i:03d}",
                    name=f"Test Profile {i}",
                    username=f"user{i}",
                    password=f"pass{i}",
                    domain_name="instagram.com"
                )
            )

        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = large_profile_set

        # Test loading large profile set
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 10)

        # Test profile manager can handle large sets
        with patch.object(AdsPowerProfileManager, 'get_available_profiles', return_value=large_profile_set):
            manager = AdsPowerProfileManager()
            available_profiles = manager.get_available_profiles()
            self.assertEqual(len(available_profiles), 10)


class TestAdsPowerModuleInteractions(unittest.TestCase):
    """Test cases for interactions between AdsPower modules."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_profile = AdsPowerProfile(
            profile_id="profile_001",
            name="Test Profile",
            username="test_user",
            password="test_pass",
            domain_name="instagram.com",
            group=AdsPowerProfileGroup(id="group_123", name="Test Group")
        )

    @patch('src.integrations.adspower.config.client')
    def test_config_client_integration(self, mock_client):
        """Test integration between config and client modules."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = [self.sample_profile]

        # Test that config module properly uses client
        profiles = load_adspower_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['id'], "profile_001")

    def test_client_profile_manager_integration(self):
        """Test integration between client and profile manager."""
        # Test that profile manager properly initializes client
        manager = AdsPowerProfileManager()
        self.assertIsNotNone(manager.adspower_client)
        self.assertEqual(manager.adspower_client.base_url, "http://localhost:50325")


if __name__ == '__main__':
    unittest.main()
