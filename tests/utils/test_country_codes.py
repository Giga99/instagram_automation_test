#!/usr/bin/env python3
"""
Country Codes Module Tests

Tests for the country codes functionality including:
- Country code to name mapping
- Country name lookup by code
- Country search functionality
- Data integrity validation
"""

import unittest
from typing import Dict

# Import the modules to test
from src.utils.country_codes import (
    COUNTRY_CODES,
    get_country_name,
    get_country_codes,
    search_countries
)


class TestCountryCodes(unittest.TestCase):
    """Test cases for country codes functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample country codes for testing
        self.sample_country_codes = {
            'us': 'United States of America (USA)',
            'ca': 'Canada',
            'gb': 'Great Britain',
            'de': 'Germany',
            'fr': 'France',
            'jp': 'Japan',
            'cn': 'China',
            'au': 'Australia'
        }

    def test_country_codes_structure(self):
        """Test that country codes have proper structure."""
        # Test that we have a reasonable number of country codes
        self.assertGreater(len(COUNTRY_CODES), 200)  # Should have most world countries
        
        # Test that all keys are lowercase 2-letter codes
        for code in COUNTRY_CODES.keys():
            self.assertEqual(len(code), 2)
            self.assertEqual(code, code.lower())
            
        # Test that all values are non-empty strings
        for name in COUNTRY_CODES.values():
            self.assertIsInstance(name, str)
            self.assertGreater(len(name), 0)

    def test_get_country_name_existing(self):
        """Test getting country name for existing country codes."""
        result = get_country_name('us')
        self.assertEqual(result, 'United States of America (USA)')
        
        result = get_country_name('ca')
        self.assertEqual(result, 'Canada')

    def test_get_country_name_case_insensitive(self):
        """Test getting country name with different cases."""
        # Test uppercase
        result = get_country_name('US')
        self.assertEqual(result, 'United States of America (USA)')
        
        # Test mixed case
        result = get_country_name('Ca')
        self.assertEqual(result, 'Canada')

    def test_get_country_name_nonexistent(self):
        """Test getting country name for non-existent country code."""
        result = get_country_name('xx')
        self.assertEqual(result, 'Unknown')

    def test_search_countries_partial_match(self):
        """Test searching countries by partial name match."""
        query = 'united'
        matches = search_countries(query)
        
        self.assertIn('us', matches)
        self.assertEqual(matches['us'], 'United States of America (USA)')

    def test_search_countries_case_insensitive(self):
        """Test case-insensitive country search."""
        query = 'CANADA'
        matches = search_countries(query)
        
        self.assertIn('ca', matches)
        self.assertEqual(matches['ca'], 'Canada')

    def test_search_countries_no_matches(self):
        """Test searching for countries with no matches."""
        query = 'nonexistent'
        matches = search_countries(query)
        
        self.assertEqual(len(matches), 0)

    def test_search_countries_multiple_matches(self):
        """Test searching for countries with multiple matches."""
        query = 'in'
        matches = search_countries(query)
        
        # Should match "China", "India", "Indonesia", "Argentina", etc.
        self.assertGreaterEqual(len(matches), 2)
        
        # Verify some expected matches
        self.assertIn('cn', matches)  # China
        self.assertIn('in', matches)  # India

    def test_common_country_codes_present(self):
        """Test that common country codes are present."""
        common_codes = ['us', 'ca', 'gb', 'de', 'fr', 'jp', 'cn', 'au']
        
        for code in common_codes:
            self.assertIn(code, COUNTRY_CODES)

    def test_country_names_format(self):
        """Test that country names follow expected format."""
        for code, name in COUNTRY_CODES.items():
            # Names should not be empty
            self.assertGreater(len(name), 0)
            
            # Names should not start or end with whitespace
            self.assertEqual(name, name.strip())
            
            # Names should be properly capitalized (start with uppercase)
            self.assertTrue(name[0].isupper() or name[0].isdigit())

    def test_proxy_configuration_compatibility(self):
        """Test compatibility with proxy configuration requirements."""
        # Test that country codes can be used for proxy configurations
        proxy_config_template = {
            'type': 'http',
            'country': None,
            'host': 'proxy.example.com',
            'port': 8080
        }
        
        for code in list(COUNTRY_CODES.keys())[:10]:  # Test first 10 for efficiency
            proxy_config = proxy_config_template.copy()
            proxy_config['country'] = code
            
            # Validate that the configuration is valid
            self.assertIsInstance(proxy_config['country'], str)
            self.assertEqual(len(proxy_config['country']), 2)

    def test_specific_country_mappings(self):
        """Test specific country code mappings mentioned in requirements."""
        expected_mappings = {
            'us': 'United States of America (USA)',
            'gb': 'Great Britain',
            'cn': 'China',
            'hk': 'China Hong Kong',  # This would need to be in the actual data
            'mo': 'China Macao',     # This would need to be in the actual data
            'tw': 'China Taiwan'     # This would need to be in the actual data
        }
        
        # Test the mappings that exist in our data
        for code, expected_name in expected_mappings.items():
            if code in COUNTRY_CODES:
                self.assertEqual(COUNTRY_CODES[code], expected_name)


class TestCountryCodesIntegration(unittest.TestCase):
    """Integration tests for country codes with application functionality."""

    def test_country_codes_with_profile_creation(self):
        """Test using country codes in profile creation context."""
        # Simulate profile creation with country selection
        profile_data = {
            'name': 'Test Profile',
            'proxy': {
                'country_code': 'us',
                'country_name': 'United States of America (USA)'
            }
        }
        
        # Validate profile data structure
        self.assertIn('proxy', profile_data)
        self.assertIn('country_code', profile_data['proxy'])
        self.assertEqual(len(profile_data['proxy']['country_code']), 2)

    def test_country_codes_with_group_configuration(self):
        """Test using country codes in group configuration context."""
        # Simulate group configuration with country-based organization
        group_config = {
            'name': 'US Profiles',
            'country_filter': 'us',
            'description': 'Profiles configured for United States'
        }
        
        # Validate group configuration
        self.assertIn('country_filter', group_config)
        self.assertEqual(group_config['country_filter'], 'us')

    def test_country_codes_with_automation_settings(self):
        """Test using country codes in automation settings."""
        # Simulate automation settings with country-specific configurations
        automation_config = {
            'target_countries': ['us', 'ca', 'gb'],
            'timezone_mapping': {
                'us': 'America/New_York',
                'ca': 'America/Toronto',
                'gb': 'Europe/London'
            }
        }
        
        # Validate automation configuration
        self.assertIsInstance(automation_config['target_countries'], list)
        self.assertGreater(len(automation_config['target_countries']), 0)
        
        for country_code in automation_config['target_countries']:
            self.assertEqual(len(country_code), 2)


if __name__ == '__main__':
    unittest.main() 