"""
Project-level models package

This package contains unified dataclasses used across the entire project,
replacing dictionary-based data structures for better type safety and maintainability.
"""

from .profile import (
    AutomationProfile,
    ProfileSettings,
    ProfileHealth,
    ProfileResult,
    ProxyConfig,
    ProfileGroup
)

__all__ = [
    'AutomationProfile',
    'ProfileSettings',
    'ProfileHealth',
    'ProfileResult',
    'ProxyConfig',
    'ProfileGroup'
] 