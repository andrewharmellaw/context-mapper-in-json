"""
Configuration management for Context Mapper JSON Converter
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
EXAMPLES_DIR = PROJECT_ROOT / "examples"
TESTS_DIR = PROJECT_ROOT / "tests"

# Logging configuration
def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration for the application."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("cml_converter.log")
        ]
    )

# Default configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    "validation": {
        "strict_mode": True,
        "allow_additional_properties": False,
        "validate_references": True,
    },
    "conversion": {
        "indent_size": 2,
        "line_ending": "\n",
        "include_comments": True,
    },
    "output": {
        "format_output": True,
        "validate_output": True,
    },
    "performance": {
        "max_contexts": 1000,
        "timeout_seconds": 300,
    }
}

class Config:
    """Configuration class for the Context Mapper JSON Converter."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """Initialize configuration with optional custom settings."""
        self.config = DEFAULT_CONFIG.copy()
        if config_dict:
            self._update_config(config_dict)
    
    def _update_config(self, config_dict: Dict[str, Any]) -> None:
        """Recursively update configuration with new values."""
        for key, value in config_dict.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'validation.strict_mode')."""
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation."""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value

# Global configuration instance
config = Config()

# Environment-based configuration
if os.getenv("CML_CONVERTER_ENV") == "development":
    config.set("validation.strict_mode", False)
    setup_logging("DEBUG")
elif os.getenv("CML_CONVERTER_ENV") == "production":
    config.set("validation.strict_mode", True)
    setup_logging("WARNING")
else:
    setup_logging("INFO")