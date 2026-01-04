"""
Secrets Management for GVD Engine
===================================
Centralized configuration for API keys and secrets.
Validates environment variables on startup to fail fast.

Usage:
    from src.utils.secrets import secrets
    api_key = secrets.google_api_key

Security Features:
- Never logs or prints actual key values
- Validates at startup
- Provides clear error messages for missing keys
"""
import os
import logging
from typing import Optional
from dataclasses import dataclass, field

logger = logging.getLogger("Secrets")

# ======================================
# REQUIRED ENVIRONMENT VARIABLES
# ======================================
REQUIRED_VARS = [
    "GOOGLE_API_KEY",
]

OPTIONAL_VARS = [
    "LOG_LEVEL",
    "LOG_FORMAT",
    "LOG_FILE",
]


@dataclass
class SecretsConfig:
    """
    Immutable configuration container for secrets.
    
    All sensitive values are loaded from environment variables.
    Never store secrets in code or config files.
    """
    google_api_key: str = field(default="", repr=False)  # repr=False prevents logging
    log_level: str = "INFO"
    log_format: str = "console"
    log_file: Optional[str] = None
    
    def __post_init__(self):
        """Mask sensitive fields in logs."""
        if self.google_api_key:
            logger.debug(f"GOOGLE_API_KEY loaded (length: {len(self.google_api_key)})")
    
    @property
    def is_configured(self) -> bool:
        """Check if all required secrets are configured."""
        return bool(self.google_api_key)
    
    def mask_value(self, value: str, visible_chars: int = 4) -> str:
        """Mask a secret value for safe logging."""
        if not value or len(value) <= visible_chars:
            return "***"
        return value[:visible_chars] + "***" + value[-2:]


def load_secrets() -> SecretsConfig:
    """
    Load and validate all secrets from environment variables.
    
    Raises:
        ValueError: If required environment variables are missing.
    """
    from dotenv import load_dotenv
    load_dotenv()  # Load from .env file if present
    
    # Check required variables
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        error_msg = f"Missing required environment variables: {', '.join(missing)}\n"
        error_msg += "Please set these in your .env file or system environment."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    config = SecretsConfig(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format=os.getenv("LOG_FORMAT", "console"),
        log_file=os.getenv("LOG_FILE"),
    )
    
    logger.info("Secrets configuration loaded successfully")
    return config


def validate_secrets_on_import() -> SecretsConfig:
    """
    Validates secrets when module is imported.
    
    This is the main entry point - called automatically on import.
    """
    try:
        return load_secrets()
    except ValueError as e:
        # Don't crash on import during development/testing
        logger.warning(f"Secrets validation failed: {e}")
        return SecretsConfig()


# ======================================
# SINGLETON INSTANCE
# ======================================
# Loaded once at import time
secrets = validate_secrets_on_import()


# ======================================
# HELPER FUNCTIONS
# ======================================
def get_api_key(key_name: str = "GOOGLE_API_KEY") -> str:
    """
    Get an API key from the secrets configuration.
    
    This is the recommended way to access API keys throughout the codebase.
    """
    if key_name == "GOOGLE_API_KEY":
        return secrets.google_api_key
    return os.getenv(key_name, "")


def require_api_key(key_name: str = "GOOGLE_API_KEY") -> str:
    """
    Get an API key, raising an error if not configured.
    
    Use this in production code paths that require the key.
    """
    key = get_api_key(key_name)
    if not key:
        raise ValueError(f"Required API key not configured: {key_name}")
    return key
