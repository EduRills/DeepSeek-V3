"""Configuration loading utilities."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default to config/config.yaml in the project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "config" / "config.yaml"

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


def get_env_variable(key: str, default: Optional[str] = None) -> str:
    """
    Get environment variable with optional default.

    Args:
        key: Environment variable key
        default: Default value if key not found

    Returns:
        Environment variable value

    Raises:
        ValueError: If key not found and no default provided
    """
    # Load .env file if it exists
    load_dotenv()

    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable '{key}' not found and no default provided")

    return value


def get_database_url() -> str:
    """Get database URL from environment."""
    return get_env_variable('DATABASE_URL', 'sqlite:///nairobi.db')


def get_redis_url() -> str:
    """Get Redis URL from environment."""
    return get_env_variable('REDIS_URL', 'redis://localhost:6379/0')


def get_mongodb_url() -> str:
    """Get MongoDB URL from environment."""
    return get_env_variable('MONGODB_URL', 'mongodb://localhost:27017/')
