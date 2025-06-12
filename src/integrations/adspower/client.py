"""
AdsPower Local API Client

Provides integration with AdsPower Local API for managing browser profiles.
This module handles profile operations, browser automation, and session management.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any

import requests

from src.utils.date_utils import parse_timestamp

logger = logging.getLogger(__name__)


@dataclass
class AdsPowerProfileGroup:
    """Represents an AdsPower profile group."""
    id: str
    name: Optional[str] = None
    remark: Optional[str] = None


@dataclass
class AdsPowerProfile:
    """Represents an AdsPower profile configuration."""
    profile_id: str
    name: str
    created_at: Optional[datetime] = None
    username: Optional[str] = None
    password: Optional[str] = None
    domain_name: Optional[str] = None
    group: Optional[AdsPowerProfileGroup] = None
    last_open_time: Optional[datetime] = None
    # proxy_config: Optional[Dict[str, Any]] = None TODO check if this is needed
    # fingerprint_config: Optional[Dict[str, Any]] = None
    # platform_config: Optional[Dict[str, Any]] = None


class AdsPowerClient:
    """
    Client for interacting with AdsPower Local API.
    
    Handles browser profile management, automation setup, and session control.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:50325", api_key: Optional[str] = None):
        """
        Initialize AdsPower client.
        
        Args:
            base_url: AdsPower Local API base URL
            api_key: API key for headless mode (optional for GUI mode)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()

        # Set up headers for API requests
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def check_connection(self) -> bool:
        """
        Check if AdsPower Local API is accessible.
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to AdsPower API: {str(e)}")
            return False

    def get_profiles(self, group_id: Optional[str] = None) -> List[AdsPowerProfile]:
        """
        Retrieve all available profiles.
        
        Args:
            group_id: Optional group ID to filter profiles
            
        Returns:
            List of AdsPowerProfile objects
        """
        try:
            url = f"{self.base_url}/api/v1/user/list"
            params = {}
            if group_id:
                params["group_id"] = group_id
            params["page"] = 1
            params["page_size"] = 100

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            profiles = []

            if data.get("code") == 0 and "data" in data:
                for profile_data in data["data"].get("list", []):
                    try:
                        profile_group = AdsPowerProfileGroup(
                            id=profile_data.get("group_id"),
                            name=profile_data.get("group_name"),
                            remark=profile_data.get("group_remark")
                        ) if profile_data.get("group_id") and profile_data.get("group_id") != "0" else None
                        profile = AdsPowerProfile(
                            profile_id=profile_data.get("user_id"),
                            name=profile_data.get("name"),
                            username=profile_data.get("username"),
                            password=profile_data.get("password"),
                            domain_name=profile_data.get("domain_name"),
                            group=profile_group,
                            created_at=parse_timestamp(profile_data.get("created_time")),
                            last_open_time=parse_timestamp(profile_data.get("last_open_time")),
                        )
                        profiles.append(profile)
                    except Exception as e:
                        logger.error(f"Failed to parse profile: {str(e)}")

            return profiles

        except Exception as e:
            logger.error(f"Failed to get profiles: {str(e)}")
            return []

    def start_profile(self, profile_id: str, headless: bool = True) -> Optional[Dict[str, Any]]:
        """
        Start a browser profile and get automation endpoints.
        
        Args:
            profile_id: Profile ID to start
            headless: Whether to run in headless mode
            
        Returns:
            Dictionary with browser connection info or None if failed
        """
        try:
            url = f"{self.base_url}/api/v1/browser/start"
            params = {
                "user_id": profile_id,
                "headless": str(headless).lower()
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == 0:
                return data.get("data")
            else:
                logger.error(f"Failed to start profile {profile_id}: {data.get('msg')}")
                return None

        except Exception as e:
            logger.error(f"Failed to start profile {profile_id}: {str(e)}")
            return None

    def stop_profile(self, profile_id: str) -> bool:
        """
        Stop a running browser profile.
        
        Args:
            profile_id: Profile ID to stop
            
        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/api/v1/browser/stop"
            params = {"user_id": profile_id}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            return data.get("code") == 0

        except Exception as e:
            logger.error(f"Failed to stop profile {profile_id}: {str(e)}")
            return False

    def check_profile_status(self, profile_id: str) -> str:
        """
        Check the status of a browser profile.
        
        Args:
            profile_id: Profile ID to check
            
        Returns:
            Profile status ('Active', 'Inactive', etc.)
        """
        try:
            url = f"{self.base_url}/api/v1/browser/active"
            params = {"user_id": profile_id}

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("status", "Inactive")
            return "Unknown"

        except Exception as e:
            logger.error(f"Failed to check profile status {profile_id}: {str(e)}")
            return "Error"

    def get_groups(self) -> List[AdsPowerProfileGroup]:
        """
        Get all profile groups.
        
        Returns:
            List of AdsPowerProfileGroup objects
        """
        try:
            url = f"{self.base_url}/api/v1/group/list"
            response = self.session.get(url)
            response.raise_for_status()

            data = response.json()
            groups = []

            if data.get("code") == 0 and "data" in data:
                group_list = data["data"]
                if isinstance(group_list, dict) and "list" in group_list:
                    group_list = group_list["list"]
                
                for group_data in group_list:
                    try:
                        group = AdsPowerProfileGroup(
                            id=group_data.get("group_id"),
                            name=group_data.get("group_name"),
                            remark=group_data.get("remark")
                        )
                        groups.append(group)
                    except Exception as e:
                        logger.error(f"Failed to parse group: {str(e)}")

            return groups

        except Exception as e:
            logger.error(f"Failed to get groups: {str(e)}")
            return []

    def create_group(self, name: str, remark: Optional[str] = None) -> Optional[AdsPowerProfileGroup]:
        """
        Create a new profile group.
        
        Args:
            name: Name of the group to create
            remark: Optional remark/description for the group
            
        Returns:
            AdsPowerProfileGroup object if successful, None otherwise
        """
        try:
            url = f"{self.base_url}/api/v1/group/create"
            data = {
                "group_name": name
            }
            if remark:
                data["remark"] = remark

            response = self.session.post(url, json=data)
            response.raise_for_status()

            result = response.json()
            if result.get("code") == 0 and "data" in result:
                group_data = result["data"]
                return AdsPowerProfileGroup(
                    id=group_data.get("group_id"),
                    name=group_data.get("group_name"),
                    remark=group_data.get("remark")
                )
            else:
                logger.error(f"Failed to create group '{name}': {result.get('msg')}")
                return None

        except Exception as e:
            logger.error(f"Failed to create group '{name}': {str(e)}")
            return None
