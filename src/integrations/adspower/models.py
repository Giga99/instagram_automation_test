from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AdsPowerProxySoft(Enum):
    """Supported proxy software types."""
    BRIGHTDATA = "brightdata"
    BRIGHTAUTO = "brightauto"
    OXYLABSAUTO = "oxylabsauto"
    S922S5AUTO = "922S5auto"
    IPIDEAAUTO = "ipideaauto"
    IPFOXYAUTO = "ipfoxyauto"
    S922S5AUTH = "922S5auth"
    KOOKAUTO = "kookauto"
    SSH = "ssh"
    OTHER = "other"
    NOPROXY = "noproxy"


class AdsPowerProxyType(Enum):
    """Supported proxy types."""
    HTTP = "http"
    HTTPS = "https"
    SOCKS5 = "socks5"


@dataclass
class AdsPowerProxyConfig:
    """Represents AdsPower user proxy configuration."""
    id: str
    proxy_soft: AdsPowerProxySoft
    proxy_type: Optional[AdsPowerProxyType] = None
    proxy_host: Optional[str] = None
    proxy_port: Optional[str] = None
    proxy_user: Optional[str] = None
    proxy_password: Optional[str] = None
    proxy_url: Optional[str] = None
    global_config: Optional[str] = "0"


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
    proxy_config: Optional[AdsPowerProxyConfig] = None
    # fingerprint_config: Optional[Dict[str, Any]] = None
    # platform_config: Optional[Dict[str, Any]] = None
