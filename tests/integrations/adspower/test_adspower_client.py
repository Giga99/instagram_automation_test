#!/usr/bin/env python3
"""
AdsPower Client Module Tests

Tests for the AdsPower client functionality including:
- API connection and status checking
- Profile retrieval and management
- Browser session control (start/stop)
- Error handling and edge cases
"""

import unittest
from datetime import datetime
from unittest.mock import Mock, patch

import requests

# Import the modules to test
from src.integrations.adspower.client import AdsPowerClient, AdsPowerProfile, AdsPowerProfileGroup


class TestAdsPowerClient(unittest.TestCase):
    """Test cases for AdsPowerClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = AdsPowerClient()
        self.test_profile_id = "test_profile_123"

    def test_init_default_params(self):
        """Test client initialization with default parameters."""
        client = AdsPowerClient()
        self.assertEqual(client.base_url, "http://127.0.0.1:50325")
        self.assertIsNone(client.api_key)

    def test_init_custom_params(self):
        """Test client initialization with custom parameters."""
        client = AdsPowerClient("http://localhost:8080", "test_api_key")
        self.assertEqual(client.base_url, "http://localhost:8080")
        self.assertEqual(client.api_key, "test_api_key")

    def test_init_url_trailing_slash(self):
        """Test URL normalization removes trailing slash."""
        client = AdsPowerClient("http://localhost:8080/")
        self.assertEqual(client.base_url, "http://localhost:8080")

    @patch('requests.Session.get')
    def test_check_connection_success(self, mock_get):
        """Test successful connection check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = self.client.check_connection()
        self.assertTrue(result)
        mock_get.assert_called_once_with("http://127.0.0.1:50325/status", timeout=5)

    @patch('requests.Session.get')
    def test_check_connection_failure(self, mock_get):
        """Test connection check failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = self.client.check_connection()
        self.assertFalse(result)

    @patch('requests.Session.get')
    def test_check_connection_bad_status(self, mock_get):
        """Test connection check with bad status code."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = self.client.check_connection()
        self.assertFalse(result)

    @patch('requests.Session.get')
    def test_get_profiles_success(self, mock_get):
        """Test successful profile retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "list": [{
                    "user_id": "profile_001",
                    "name": "Test Profile",
                    "username": "test_user",
                    "password": "test_pass",
                    "domain_name": "instagram.com",
                    "group_id": "group_123",
                    "group_name": "Test Group",
                    "created_time": "1640995200",
                    "last_open_time": "1640995200"
                }]
            }
        }
        mock_get.return_value = mock_response

        profiles = self.client.get_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertIsInstance(profiles[0], AdsPowerProfile)
        self.assertEqual(profiles[0].profile_id, "profile_001")
        self.assertEqual(profiles[0].name, "Test Profile")

    @patch('requests.Session.get')
    def test_get_profiles_no_group(self, mock_get):
        """Test profile retrieval for profile without group."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "list": [{
                    "user_id": "profile_001",
                    "name": "Test Profile",
                    "username": "test_user",
                    "password": "test_pass",
                    "domain_name": "instagram.com",
                    "group_id": "0",
                    "group_name": "",
                    "created_time": "1640995200",
                    "last_open_time": "1640995200"
                }]
            }
        }
        mock_get.return_value = mock_response

        profiles = self.client.get_profiles()
        self.assertEqual(len(profiles), 1)
        self.assertIsNone(profiles[0].group)

    @patch('requests.Session.get')
    def test_get_profiles_with_group_filter(self, mock_get):
        """Test profile retrieval with group filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "list": [{
                    "user_id": "profile_001",
                    "name": "Test Profile",
                    "username": "test_user",
                    "password": "test_pass",
                    "domain_name": "instagram.com",
                    "group_id": "group_123",
                    "group_name": "Test Group",
                    "created_time": "1640995200",
                    "last_open_time": "1640995200"
                }]
            }
        }
        mock_get.return_value = mock_response

        profiles = self.client.get_profiles("group_123")
        self.assertEqual(len(profiles), 1)

    @patch('requests.Session.get')
    def test_get_profiles_network_error(self, mock_get):
        """Test profile retrieval with network error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        profiles = self.client.get_profiles()
        self.assertEqual(len(profiles), 0)

    @patch('requests.Session.get')
    def test_get_profiles_api_error(self, mock_get):
        """Test profile retrieval with API error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 1,
            "msg": "API Error"
        }
        mock_get.return_value = mock_response

        profiles = self.client.get_profiles()
        self.assertEqual(len(profiles), 0)

    @patch('requests.Session.get')
    def test_get_profiles_malformed_response(self, mock_get):
        """Test profile retrieval with malformed response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_get.return_value = mock_response

        profiles = self.client.get_profiles()
        self.assertEqual(len(profiles), 0)

    @patch('requests.Session.get')
    def test_start_profile_success(self, mock_get):
        """Test successful profile start."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "ws": {"puppeteer": "ws://localhost:9222"},
                "debug_port": 9222
            }
        }
        mock_get.return_value = mock_response

        result = self.client.start_profile(self.test_profile_id)
        self.assertIsNotNone(result)
        self.assertIn("ws", result)

    @patch('requests.Session.get')
    def test_start_profile_headless_false(self, mock_get):
        """Test profile start with headless=False."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {"ws": {"puppeteer": "ws://localhost:9222"}}
        }
        mock_get.return_value = mock_response

        result = self.client.start_profile(self.test_profile_id, headless=False)
        self.assertIsNotNone(result)

    @patch('requests.Session.get')
    def test_start_profile_network_error(self, mock_get):
        """Test profile start with network error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = self.client.start_profile(self.test_profile_id)
        self.assertIsNone(result)

    @patch('requests.Session.get')
    def test_start_profile_api_error(self, mock_get):
        """Test profile start with API error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 1,
            "msg": "Profile not found"
        }
        mock_get.return_value = mock_response

        result = self.client.start_profile(self.test_profile_id)
        self.assertIsNone(result)

    @patch('requests.Session.get')
    def test_stop_profile_success(self, mock_get):
        """Test successful profile stop."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 0}
        mock_get.return_value = mock_response

        result = self.client.stop_profile(self.test_profile_id)
        self.assertTrue(result)

    @patch('requests.Session.get')
    def test_stop_profile_network_error(self, mock_get):
        """Test profile stop with network error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        result = self.client.stop_profile(self.test_profile_id)
        self.assertFalse(result)

    @patch('requests.Session.get')
    def test_stop_profile_api_error(self, mock_get):
        """Test profile stop with API error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"code": 1}
        mock_get.return_value = mock_response

        result = self.client.stop_profile(self.test_profile_id)
        self.assertFalse(result)

    @patch('requests.Session.get')
    def test_check_profile_status_active(self, mock_get):
        """Test checking status of active profile."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {"status": "Active"}
        }
        mock_get.return_value = mock_response

        status = self.client.check_profile_status(self.test_profile_id)
        self.assertEqual(status, "Active")

    @patch('requests.Session.get')
    def test_check_profile_status_inactive(self, mock_get):
        """Test checking status of inactive profile."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {}  # Empty data means inactive
        }
        mock_get.return_value = mock_response

        status = self.client.check_profile_status(self.test_profile_id)
        self.assertEqual(status, "Inactive")

    @patch('requests.Session.get')
    def test_check_profile_status_error(self, mock_get):
        """Test checking profile status with error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        status = self.client.check_profile_status(self.test_profile_id)
        self.assertEqual(status, "Error")

    @patch('requests.Session.get')
    def test_get_groups_success(self, mock_get):
        """Test successful groups retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": [
                {
                    "group_id": "group_001",
                    "group_name": "Instagram Automation",
                    "remark": "Profiles for Instagram automation"
                },
                {
                    "group_id": "group_002", 
                    "group_name": "Test Profiles",
                    "remark": None
                }
            ]
        }
        mock_get.return_value = mock_response

        groups = self.client.get_groups()
        self.assertEqual(len(groups), 2)
        self.assertIsInstance(groups[0], AdsPowerProfileGroup)
        self.assertEqual(groups[0].id, "group_001")
        self.assertEqual(groups[0].name, "Instagram Automation")
        self.assertEqual(groups[0].remark, "Profiles for Instagram automation")

    @patch('requests.Session.get')
    def test_get_groups_empty(self, mock_get):
        """Test groups retrieval when no groups exist."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": []
        }
        mock_get.return_value = mock_response

        groups = self.client.get_groups()
        self.assertEqual(len(groups), 0)

    @patch('requests.Session.get')
    def test_get_groups_network_error(self, mock_get):
        """Test groups retrieval with network error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        groups = self.client.get_groups()
        self.assertEqual(len(groups), 0)

    @patch('requests.Session.post')
    def test_create_group_success(self, mock_post):
        """Test successful group creation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "group_id": "group_new",
                "group_name": "New Test Group",
                "remark": "Test group description"
            }
        }
        mock_post.return_value = mock_response

        group = self.client.create_group("New Test Group", "Test group description")
        self.assertIsNotNone(group)
        self.assertEqual(group.id, "group_new")
        self.assertEqual(group.name, "New Test Group")
        self.assertEqual(group.remark, "Test group description")

    @patch('requests.Session.post')
    def test_create_group_without_remark(self, mock_post):
        """Test group creation without remark."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 0,
            "data": {
                "group_id": "group_new",
                "group_name": "New Test Group",
                "remark": None
            }
        }
        mock_post.return_value = mock_response

        group = self.client.create_group("New Test Group")
        self.assertIsNotNone(group)
        self.assertEqual(group.id, "group_new")
        self.assertEqual(group.name, "New Test Group")
        self.assertIsNone(group.remark)

    @patch('requests.Session.post')
    def test_create_group_api_error(self, mock_post):
        """Test group creation with API error."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": 1,
            "msg": "Group name already exists"
        }
        mock_post.return_value = mock_response

        group = self.client.create_group("Existing Group")
        self.assertIsNone(group)

    @patch('requests.Session.post')
    def test_create_group_network_error(self, mock_post):
        """Test group creation with network error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        group = self.client.create_group("New Group")
        self.assertIsNone(group)


class TestAdsPowerProfile(unittest.TestCase):
    """Test cases for AdsPowerProfile dataclass."""

    def test_profile_creation_minimal(self):
        """Test creating a profile with minimal data."""
        profile = AdsPowerProfile(
            profile_id="test_001",
            name="Test Profile"
        )
        self.assertEqual(profile.profile_id, "test_001")
        self.assertEqual(profile.name, "Test Profile")
        self.assertIsNone(profile.username)

    def test_profile_creation_full(self):
        """Test creating a profile with all data."""
        group = AdsPowerProfileGroup(id="group_123", name="Test Group")
        profile = AdsPowerProfile(
            profile_id="test_001",
            name="Test Profile",
            username="test_user",
            password="test_pass",
            domain_name="instagram.com",
            group=group,
            created_at=datetime.now(),
            last_open_time=datetime.now()
        )
        self.assertEqual(profile.profile_id, "test_001")
        self.assertEqual(profile.username, "test_user")
        self.assertEqual(profile.group.name, "Test Group")


class TestAdsPowerProfileGroup(unittest.TestCase):
    """Test cases for AdsPowerProfileGroup dataclass."""

    def test_profile_group_creation_full(self):
        """Test creating a profile group with all fields."""
        group = AdsPowerProfileGroup(id="group_123", name="Test Group", remark="Test description")
        self.assertEqual(group.id, "group_123")
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.remark, "Test description")

    def test_profile_group_creation_minimal(self):
        """Test creating a profile group with minimal fields."""
        group = AdsPowerProfileGroup(id="group_123")
        self.assertEqual(group.id, "group_123")
        self.assertIsNone(group.name)
        self.assertIsNone(group.remark)

    def test_profile_group_with_name_only(self):
        """Test creating a profile group with name but no remark."""
        group = AdsPowerProfileGroup(id="group_123", name="Test Group")
        self.assertEqual(group.id, "group_123")
        self.assertEqual(group.name, "Test Group")
        self.assertIsNone(group.remark)


if __name__ == '__main__':
    unittest.main()
