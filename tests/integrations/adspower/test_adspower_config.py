#!/usr/bin/env python3
"""
AdsPower Config Module Tests

Tests for the AdsPower configuration functionality including:
- Profile loading and discovery
- Connection testing and validation
- Error handling for missing AdsPower or API failures
- Profile formatting and data conversion
"""

import unittest
from unittest.mock import patch

from src.integrations.adspower.client import AdsPowerProfile, AdsPowerProfileGroup
# Import the modules to test
from src.integrations.adspower.config import load_adspower_profiles, test_adspower_connection


class TestAdsPowerConfig(unittest.TestCase):
    """Test cases for AdsPower configuration functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.sample_adspower_profiles = [
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
    def test_load_adspower_profiles_success(self, mock_client):
        """Test successful loading of AdsPower profiles from API."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = self.sample_adspower_profiles

        profiles = load_adspower_profiles()

        self.assertEqual(len(profiles), 2)
        self.assertEqual(profiles[0]['id'], "profile_001")
        self.assertEqual(profiles[1]['id'], "profile_002")

    @patch('src.integrations.adspower.config.client')
    def test_load_adspower_profiles_with_no_group(self, mock_client):
        """Test loading profiles where some profiles have no group."""
        profiles_with_no_group = [
            AdsPowerProfile(
                profile_id="profile_003",
                name="No Group Profile",
                username="user3",
                password="pass3",
                domain_name="instagram.com",
                group=None
            )
        ]

        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = profiles_with_no_group

        profiles = load_adspower_profiles()

        self.assertEqual(len(profiles), 1)
        self.assertEqual(profiles[0]['id'], "profile_003")
        self.assertIsNone(profiles[0]['group'])

    @patch('src.integrations.adspower.config.client')
    def test_load_adspower_profiles_no_connection(self, mock_client):
        """Test loading profiles when AdsPower is not connected."""
        mock_client.check_connection.return_value = False

        profiles = load_adspower_profiles()

        self.assertEqual(len(profiles), 0)

    @patch('src.integrations.adspower.config.client')
    def test_load_adspower_profiles_no_profiles(self, mock_client):
        """Test loading profiles when no profiles exist in AdsPower."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.return_value = []

        profiles = load_adspower_profiles()

        self.assertEqual(len(profiles), 0)

    @patch('src.integrations.adspower.config.client')
    def test_load_adspower_profiles_api_error(self, mock_client):
        """Test loading profiles when API throws an error."""
        mock_client.check_connection.return_value = True
        mock_client.get_profiles.side_effect = Exception("API Error")

        profiles = load_adspower_profiles()

        self.assertEqual(len(profiles), 0)

    @patch('src.integrations.adspower.config.client')
    def test_test_adspower_connection_success(self, mock_client):
        """Test successful AdsPower connection test."""
        mock_client.check_connection.return_value = True

        result = test_adspower_connection()

        self.assertTrue(result)

    @patch('src.integrations.adspower.config.client')
    def test_test_adspower_connection_failure(self, mock_client):
        """Test AdsPower connection test failure."""
        mock_client.check_connection.return_value = False

        result = test_adspower_connection()

        self.assertFalse(result)

    @patch('src.integrations.adspower.config.AdsPowerClient')
    def test_test_adspower_connection_exception(self, mock_client_class):
        """Test AdsPower connection test with exception."""
        mock_client_class.side_effect = Exception("Connection error")

        result = test_adspower_connection()

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
