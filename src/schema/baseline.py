"""
Security Baseline Model — Canonical Schema
Vendor-neutral representation of device security configuration
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class DeviceInfo(BaseModel):
    hostname: str
    vendor: str
    os_version: str
    serial_number: Optional[str] = None

class RemoteAccess(BaseModel):
    ssh_version: Optional[int] = None
    telnet_enabled: Optional[bool] = None
    http_management_enabled: Optional[bool] = None

class Authentication(BaseModel):
    password_encryption: Optional[bool] = None
    min_password_length: Optional[int] = None
    aaa_enabled: Optional[bool] = None

class Logging(BaseModel):
    admin_access_logging: Optional[bool] = None
    syslog_configured: Optional[bool] = None

class AccessControl(BaseModel):
    acl_count: Optional[int] = None
    default_deny_present: Optional[bool] = None

class SecurityBaseline(BaseModel):
    remote_access: RemoteAccess = Field(default_factory=RemoteAccess)
    authentication: Authentication = Field(default_factory=Authentication)
    logging: Logging = Field(default_factory=Logging)
    access_control: AccessControl = Field(default_factory=AccessControl)

class DeviceConfig(BaseModel):
    device: DeviceInfo
    baseline: SecurityBaseline
    unmapped_lines: List[Dict[str, Any]] = Field(default_factory=list)
    provenance: Dict[str, Dict] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
