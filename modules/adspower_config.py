"""
AdsPower Profile Loader

Simple loader for existing AdsPower profiles configured for Instagram automation.
"""

import os
from typing import Dict, List, Any

from modules.adspower_client import AdsPowerClient

# AdsPower Configuration
ADSPOWER_BASE_URL = os.getenv("ADSPOWER_BASE_URL", "http://127.0.0.1:50325")
ADSPOWER_API_KEY = os.getenv("ADSPOWER_API_KEY", "")

# Initialize AdsPower client
client = AdsPowerClient(ADSPOWER_BASE_URL, ADSPOWER_API_KEY)


def load_adspower_profiles() -> List[Dict[str, Any]]:
    """
    Load existing AdsPower profiles for Instagram automation.
    
    Returns:
        List of profile dictionaries compatible with main automation script
    """
    print("🔍 Discovering existing AdsPower profiles...")

    try:
        # Check if AdsPower is running
        if not client.check_connection():
            print("❌ AdsPower is not running or not accessible!")
            print("💡 Please ensure AdsPower desktop app is running")
            return []

        print("✅ Connected to AdsPower API")

        # Get all profiles
        all_profiles = client.get_profiles()

        if not all_profiles:
            print("❌ No AdsPower profiles found!")
            print("💡 Create profiles in AdsPower desktop app first")
            return []

        print(f"Got total: {len(all_profiles)} profiles from AdsPower API. Filtering and formatting...")

        # Filter and format profiles for Instagram automation
        instagram_profiles = []

        for profile_data in all_profiles:
            profile_id = profile_data.profile_id
            username = profile_data.username
            password = profile_data.password
            profile_name = profile_data.name
            group_name = profile_data.group.name if profile_data.group else None
            created_at = profile_data.created_at
            last_open_time = profile_data.last_open_time

            # Convert to automation format
            formatted_profile = {
                "id": profile_id,
                "username": username,
                "password": password,
                "profile_name": profile_name,
                "is_adspower": True,
                "group": group_name,
                "priority": 1,
                "settings": {
                    "delay_between_profiles": 30,
                    "retry_attempts": 3
                },
                "health": {
                    "status": "healthy",
                    "last_used": None,
                    "success_rate": 100
                },
                "created_at": created_at,
                "last_open_time": last_open_time
            }

            instagram_profiles.append(formatted_profile)

        print(f"✅ Found {len(instagram_profiles)} AdsPower profiles:")
        for profile in instagram_profiles:
            group_info = f" ({profile['group']})" if profile['group'] else ""
            print(f"   • {profile['id']}{group_info}")

        return instagram_profiles

    except Exception as e:
        print(f"❌ Error loading AdsPower profiles: {str(e)}")
        print("💡 Make sure AdsPower is running and API is accessible")
        return []


def test_adspower_connection() -> bool:
    """
    Test connection to AdsPower API.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        return client.check_connection()
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        return False


if __name__ == "__main__":
    """
    Test script to verify AdsPower profile loading.
    
    Usage:
        python adspower_config.py
    """
    print("🚀 AdsPower Profile Loader Test")
    print("=" * 40)

    # Test connection
    print("🔌 Testing AdsPower connection...")
    if test_adspower_connection():
        print("✅ AdsPower connection successful!")

        # Load profiles
        profiles = load_adspower_profiles()
        print(f"\n📊 Results: {len(profiles)} profiles ready for automation")

        if profiles:
            print("\n🎯 Ready to run: python main.py")
        else:
            print("\n💡 Create profiles in AdsPower desktop app first")
    else:
        print("❌ AdsPower connection failed!")
        print("💡 Please start AdsPower desktop application")
