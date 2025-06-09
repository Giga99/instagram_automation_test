"""
Scalable Profile Management Module

Simple, scalable profile management system for automation:
- Dynamic profile loading from JSON configuration
- Secure credential management  
- Health monitoring and analytics
- Scalable profiles management
"""

import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ProfileHealth:
    success_rate: float = 1.0
    total_attempts: int = 0
    recent_failures: int = 0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    consecutive_failures: int = 0
    
    def update_success(self):
        self.total_attempts += 1
        self.recent_failures = 0
        self.consecutive_failures = 0
        self.last_success = datetime.now().isoformat()
        self._recalculate_success_rate()
    
    def update_failure(self, error_type: str = "unknown"):
        self.total_attempts += 1
        self.recent_failures += 1
        self.consecutive_failures += 1
        self.last_failure = datetime.now().isoformat()
        self._recalculate_success_rate()
    
    def _recalculate_success_rate(self):
        if self.total_attempts > 0:
            successes = self.total_attempts - self.recent_failures
            self.success_rate = max(0.0, successes / self.total_attempts)
    
    def is_healthy(self, min_success_rate: float = 0.7, max_consecutive_failures: int = 3) -> bool:
        return (self.success_rate >= min_success_rate and 
                self.consecutive_failures < max_consecutive_failures)


@dataclass
class ProfileConfig:
    id: str
    credential_key: str
    enabled: bool = True
    priority: int = 1  # 1=highest, 5=lowest
    settings: Dict = None
    health: ProfileHealth = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {
                "delay_between_comments": 45,
                "max_retries": 3,
                "headless": True,
                "max_comments_per_session": 5
            }
        if self.health is None:
            self.health = ProfileHealth()
    
    @property
    def delay_between_comments(self) -> int:
        return self.settings.get("delay_between_comments", 45)
    
    @property
    def max_retries(self) -> int:
        return self.settings.get("max_retries", 3)
    
    @property
    def headless(self) -> bool:
        return self.settings.get("headless", True)
    
    def can_be_used(self) -> bool:
        """Check if profile can be used right now"""
        return self.enabled and self.health.is_healthy()


class SecureCredentialManager:
    """Secure credential management with caching"""
    
    def __init__(self):
        self._credential_cache = {}
        self._last_cache_clear = time.time()
        self._cache_ttl = 3600  # 1 hour cache TTL for security
    
    def _clear_cache_if_expired(self):
        """Clear credential cache periodically for security"""
        if time.time() - self._last_cache_clear > self._cache_ttl:
            self._credential_cache.clear()
            self._last_cache_clear = time.time()
    
    def get_credentials(self, credential_key: str) -> Optional[Tuple[str, str]]:
        """Get username/password for a credential key"""
        self._clear_cache_if_expired()
        
        if credential_key in self._credential_cache:
            return self._credential_cache[credential_key]
        
        combined_cred = os.getenv(credential_key)
        if combined_cred and ':' in combined_cred:
            username, password = combined_cred.split(':', 1)
            self._credential_cache[credential_key] = (username, password)
            return (username, password)
        
        return None
    
    def validate_credential_key(self, credential_key: str) -> bool:
        """Check if credentials exist for a key"""
        return (os.getenv(credential_key) is not None or 
                (os.getenv(f"{credential_key}_USER") and os.getenv(f"{credential_key}_PASS")))


class ProfilePool:
    """Simple profile pool manager for automation"""
    
    def __init__(self, config_file: str = "profiles.json"):
        self.config_file = config_file
        self.credential_manager = SecureCredentialManager()
        self.profiles: List[ProfileConfig] = []
        
        self._load_profiles()
    
    def _load_profiles(self) -> None:
        """Load profile configurations from JSON file"""
        if not os.path.exists(self.config_file):
            print(f"⚠️ Profile config file not found: {self.config_file}")
            self._create_sample_config()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            self.profiles = []
            for profile_data in data.get('profiles', []):
                try:
                    # Create health object if exists
                    health_data = profile_data.get('health')
                    health = ProfileHealth()
                    if health_data:
                        health.success_rate = health_data.get('success_rate', 1.0)
                        health.total_attempts = health_data.get('total_attempts', 0)
                        health.recent_failures = health_data.get('recent_failures', 0)
                        health.last_success = health_data.get('last_success')
                        health.last_failure = health_data.get('last_failure')
                        health.consecutive_failures = health_data.get('consecutive_failures', 0)
                    
                    profile = ProfileConfig(
                        id=profile_data['id'],
                        credential_key=profile_data['credential_key'],
                        enabled=profile_data.get('enabled', True),
                        priority=profile_data.get('priority', 1),
                        settings=profile_data.get('settings', {}),
                        health=health
                    )
                    
                    self.profiles.append(profile)
                    
                except (KeyError, ValueError) as e:
                    print(f"⚠️ Invalid profile config: {profile_data.get('id', 'unknown')} - {e}")
                    continue
            
            print(f"📋 Loaded {len(self.profiles)} profile configurations")
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {self.config_file}: {e}")
        except Exception as e:
            print(f"❌ Error loading profiles: {e}")
    
    def _create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "version": "1.0",
            "description": "Profile Management Configuration",
            "profiles": [
                {
                    "id": "profile_1",
                    "credential_key": "PROFILE_1", 
                    "enabled": True,
                    "priority": 1,
                    "settings": {
                        "delay_between_comments": 45,
                        "max_retries": 3,
                        "headless": True,
                        "max_comments_per_session": 5
                    }
                },
                {
                    "id": "profile_2", 
                    "credential_key": "PROFILE_2",
                    "enabled": True,
                    "priority": 1,
                    "settings": {
                        "delay_between_comments": 50,
                        "max_retries": 3,
                        "headless": True,
                        "max_comments_per_session": 4
                    }
                }
            ],
            "global_settings": {
                "default_delay_between_profiles": 30,
                "max_concurrent_profiles": 3,
                "health_check_interval": 3600,
                "auto_disable_unhealthy": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"✅ Created sample config: {self.config_file}")
        print(f"💡 Add your credentials to .env file:")
        print(f"   PROFILE_1=username1:password1")
        print(f"   PROFILE_2=username2:password2")
    
    def get_available_profiles(self, count: Optional[int] = None,
                            enabled_only: bool = True) -> List[Dict[str, any]]:
        """Get available profiles with credentials"""
        available = []
        
        for profile in self.profiles:
            # Skip disabled profiles if requested
            if enabled_only and not profile.can_be_used():
                continue
            
            # Check credentials
            credentials = self.credential_manager.get_credentials(profile.credential_key)
            if not credentials:
                print(f"⚠️ Skipping {profile.id} - no credentials found")
                continue
            
            username, password = credentials
            available.append({
                'profile': profile,
                'username': username,
                'password': password
            })
        
        # Sort by priority (1=highest priority)
        available.sort(key=lambda x: x['profile'].priority)
        
        # Limit count if specified
        if count:
            available = available[:count]
        
        return available
    
    def get_healthy_profiles(self, min_success_rate: float = 0.8) -> List[ProfileConfig]:
        """Get profiles with good health metrics"""
        return [p for p in self.profiles if p.health.success_rate >= min_success_rate]
    
    def update_profile_health(self, profile_id: str, success: bool, error_type: str = None):
        """Update profile health metrics"""
        for profile in self.profiles:
            if profile.id == profile_id:
                if success:
                    profile.health.update_success()
                else:
                    profile.health.update_failure(error_type or "unknown")
                break
        
        # Auto-save health metrics
        self.save_health_metrics()
    
    def save_health_metrics(self):
        """Save updated health metrics back to config file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Update health data for each profile
            for profile in self.profiles:
                for config_profile in data.get('profiles', []):
                    if config_profile['id'] == profile.id:
                        config_profile['health'] = asdict(profile.health)
                        break
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Error saving health metrics: {e}")
    
    def get_profile_by_id(self, profile_id: str) -> Optional[Dict[str, any]]:
        """Get specific profile with credentials"""
        for profile in self.profiles:
            if profile.id == profile_id:
                credentials = self.credential_manager.get_credentials(profile.credential_key)
                if credentials:
                    username, password = credentials
                    return {
                        'profile': profile,
                        'username': username,
                        'password': password
                    }
        return None
    
    def validate_all_credentials(self) -> Dict[str, bool]:
        """Validate that all profiles have accessible credentials"""
        results = {}
        for profile in self.profiles:
            has_creds = self.credential_manager.validate_credential_key(profile.credential_key)
            results[profile.id] = has_creds
            if not has_creds:
                print(f"❌ Missing credentials for {profile.id} (key: {profile.credential_key})")
        
        return results
    
    def reload_config(self):
        """Hot reload configuration from file"""
        print("🔄 Reloading profile configuration...")
        self._load_profiles()
        self.credential_manager._credential_cache.clear()
    
    def get_stats_summary(self) -> Dict:
        """Get dashboard stats"""
        total = len(self.profiles)
        enabled = len([p for p in self.profiles if p.enabled])
        healthy = len([p for p in self.profiles if p.health.is_healthy()])
        
        by_priority = {}
        for profile in self.profiles:
            priority = profile.priority
            by_priority[f"priority_{priority}"] = by_priority.get(f"priority_{priority}", 0) + 1
        
        return {
            "total_profiles": total,
            "enabled_profiles": enabled,
            "healthy_profiles": healthy,
            "health_rate": f"{(healthy/total*100):.1f}%" if total > 0 else "0%",
            "by_priority": by_priority,
            "timestamp": datetime.now().isoformat()
        } 