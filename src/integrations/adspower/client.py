"""
AdsPower Local API Client

Provides integration with AdsPower Local API for managing browser profiles.
This module handles profile operations, browser automation, and session management.
"""

import logging
from typing import Dict, List, Optional, Any

import requests

from src.integrations.adspower.models import AdsPowerProfile, AdsPowerProfileGroup, AdsPowerProxyConfig, \
    AdsPowerProxyType, AdsPowerProxySoft
from src.utils.date_utils import parse_timestamp

logger = logging.getLogger(__name__)


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
            params["user_id"] = "kyjb303"

            response = self.session.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            profiles = []

            if data.get("code") == 0 and "data" in data:
                for profile_data in data["data"].get("list", []):
                    try:
                        group_id = profile_data.get("group_id")
                        profile_group = AdsPowerProfileGroup(
                            id=group_id,
                            name=profile_data.get("group_name")
                        ) if group_id and group_id != "0" else None

                        proxy_id = profile_data.get("fbcc_proxy_acc_id")
                        user_proxy_config = profile_data.get("user_proxy_config")
                        proxy_config = AdsPowerProxyConfig(
                            id=proxy_id,
                            proxy_soft=AdsPowerProxySoft(user_proxy_config.get("proxy_soft")),
                            proxy_type=AdsPowerProxyType(user_proxy_config.get("proxy_type")),
                            proxy_host=user_proxy_config.get("proxy_host"),
                            proxy_port=user_proxy_config.get("proxy_port"),
                            proxy_user=user_proxy_config.get("proxy_user"),
                            proxy_password=user_proxy_config.get("proxy_password"),
                            proxy_url=user_proxy_config.get("proxy_url"),
                            global_config=user_proxy_config.get("global_config")
                        ) if proxy_id and proxy_id != "0" and user_proxy_config else None

                        profile = AdsPowerProfile(
                            profile_id=profile_data.get("user_id"),
                            name=profile_data.get("name"),
                            username=profile_data.get("username"),
                            password=profile_data.get("password"),
                            domain_name=profile_data.get("domain_name"),
                            group=profile_group,
                            created_at=parse_timestamp(profile_data.get("created_time")),
                            last_open_time=parse_timestamp(profile_data.get("last_open_time")),
                            proxy_config=proxy_config,
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
            params = {"page": 1, "page_size": 100}
            response = self.session.get(url, params=params)
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
