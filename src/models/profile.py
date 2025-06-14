"""
Unified Profile Models

Project-level dataclasses that provide type-safe alternatives to dictionaries
used throughout the automation project. These models integrate with various
sources (AdsPower, manual configs, etc.) providing a consistent interface.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from src.utils.logger import get_current_timestamp


class ProfileStatus(Enum):
    """Profile health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class ProfileSource(Enum):
    """Source of profile configuration."""
    ADSPOWER = "adspower"
    MANUAL = "manual"
    IMPORTED = "imported"


@dataclass
class ProxyConfig:
    """Unified proxy configuration."""
    proxy_id: Optional[str] = None
    proxy_type: Optional[str] = None
    proxy_host: Optional[str] = None
    proxy_port: Optional[str] = None
    proxy_user: Optional[str] = None
    proxy_password: Optional[str] = None
    proxy_url: Optional[str] = None
    proxy_soft: Optional[str] = None
    global_config: Optional[str] = "0"

    @classmethod
    def from_adspower(cls, adspower_proxy_config) -> Optional['ProxyConfig']:
        """Create ProxyConfig from AdsPower proxy configuration."""
        if not adspower_proxy_config:
            return None

        return cls(
            proxy_id=adspower_proxy_config.id,
            proxy_type=adspower_proxy_config.proxy_type.value if adspower_proxy_config.proxy_type else None,
            proxy_host=adspower_proxy_config.proxy_host,
            proxy_port=adspower_proxy_config.proxy_port,
            proxy_user=adspower_proxy_config.proxy_user,
            proxy_password=adspower_proxy_config.proxy_password,
            proxy_url=adspower_proxy_config.proxy_url,
            proxy_soft=adspower_proxy_config.proxy_soft.value if adspower_proxy_config.proxy_soft else None,
            global_config=adspower_proxy_config.global_config
        )


@dataclass
class ProfileGroup:
    """Unified profile group."""
    id: str
    name: Optional[str] = None
    remark: Optional[str] = None

    @classmethod
    def from_adspower(cls, adspower_group) -> Optional['ProfileGroup']:
        """Create ProfileGroup from AdsPower group."""
        if not adspower_group:
            return None

        return cls(
            id=adspower_group.id,
            name=adspower_group.name,
            remark=adspower_group.remark
        )


@dataclass
class ProfileSettings:
    """Profile-specific automation settings."""
    delay_between_profiles: int = 30
    delay_between_comments: int = 45
    max_retries: int = 3
    retry_attempts: int = 3
    max_comments_per_session: int = 5
    headless: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "delay_between_profiles": self.delay_between_profiles,
            "delay_between_comments": self.delay_between_comments,
            "max_retries": self.max_retries,
            "retry_attempts": self.retry_attempts,
            "max_comments_per_session": self.max_comments_per_session,
            "headless": self.headless
        }


@dataclass
class ProfileHealth:
    """Profile health and usage statistics."""
    status: ProfileStatus = ProfileStatus.HEALTHY
    last_used: Optional[datetime] = None
    success_rate: float = 100.0
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "status": self.status.value,
            "last_used": self.last_used,
            "success_rate": self.success_rate,
            "total_attempts": self.total_attempts,
            "successful_attempts": self.successful_attempts,
            "failed_attempts": self.failed_attempts,
            "last_error": self.last_error
        }

    def update_success(self):
        """Update health metrics after successful operation."""
        self.total_attempts += 1
        self.successful_attempts += 1
        self.success_rate = (self.successful_attempts / self.total_attempts) * 100
        self.last_used = datetime.now()
        self.last_error = None

        # Update status based on success rate
        if self.success_rate >= 90:
            self.status = ProfileStatus.HEALTHY
        elif self.success_rate >= 70:
            self.status = ProfileStatus.WARNING
        else:
            self.status = ProfileStatus.UNHEALTHY

    def update_failure(self, error_message: str):
        """Update health metrics after failed operation."""
        self.total_attempts += 1
        self.failed_attempts += 1
        self.success_rate = (self.successful_attempts / self.total_attempts) * 100
        self.last_used = datetime.now()
        self.last_error = error_message

        # Update status based on success rate
        if self.success_rate >= 90:
            self.status = ProfileStatus.HEALTHY
        elif self.success_rate >= 70:
            self.status = ProfileStatus.WARNING
        else:
            self.status = ProfileStatus.UNHEALTHY


@dataclass
class AutomationProfile:
    """
    Unified automation profile that works with various sources.
    
    This dataclass replaces dictionary-based profile management throughout
    the project, providing type safety and consistent structure.
    """
    id: str
    username: str
    password: str
    profile_name: str
    source: ProfileSource = ProfileSource.MANUAL
    enabled: bool = True
    priority: int = 1

    # Optional fields
    domain_name: Optional[str] = None
    group: Optional[ProfileGroup] = None
    proxy_config: Optional[ProxyConfig] = None

    # Automation configuration
    settings: ProfileSettings = field(default_factory=ProfileSettings)
    health: ProfileHealth = field(default_factory=ProfileHealth)

    # Timestamps
    created_at: Optional[datetime] = None
    last_open_time: Optional[datetime] = None

    @classmethod
    def from_adspower(cls, adspower_profile) -> 'AutomationProfile':
        """Create AutomationProfile from AdsPower profile dataclass."""
        return cls(
            id=adspower_profile.profile_id,
            username=adspower_profile.username or "",
            password=adspower_profile.password or "",
            profile_name=adspower_profile.name,
            source=ProfileSource.ADSPOWER,
            domain_name=adspower_profile.domain_name,
            group=ProfileGroup.from_adspower(adspower_profile.group),
            proxy_config=ProxyConfig.from_adspower(adspower_profile.proxy_config),
            created_at=adspower_profile.created_at,
            last_open_time=adspower_profile.last_open_time
        )

    def update_success(self):
        """Update profile health after successful operation."""
        self.health.update_success()

    def update_failure(self, error_message: str):
        """Update profile health after failed operation."""
        self.health.update_failure(error_message)

    def is_healthy(self) -> bool:
        """Check if profile is in healthy state."""
        return self.health.status == ProfileStatus.HEALTHY


@dataclass
class ProfileResult:
    """Result of processing a single profile."""
    profile_id: str
    success: bool
    comment: str = ""
    error: Optional[str] = None
    timestamp: Optional[str] = get_current_timestamp()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backward compatibility."""
        return {
            "profile_id": self.profile_id,
            "success": self.success,
            "comment": self.comment,
            "error": self.error,
            "timestamp": self.timestamp
        }
