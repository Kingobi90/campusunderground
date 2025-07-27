#!/usr/bin/env python3
"""
Configuration module for Moodle integration
This module provides configuration settings and environment variable management
for the Moodle integration in Campus Underground.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('moodle_config')

class MoodleConfig:
    """Configuration manager for Moodle integration."""
    
    # Default configuration values
    DEFAULT_CONFIG = {
        'MOODLE_URL': 'https://moodle.concordia.ca',
        'MOODLE_API_TOKEN': '',
        'FLASK_SECRET_KEY': 'campus-underground-secret-key',
        'PORT': 5002,
        'DEBUG': True,
        'LOG_LEVEL': 'INFO',
        'USE_MOCK_DATA': False,
        'TIMEOUT': 30,  # API request timeout in seconds
        'RETRY_ATTEMPTS': 3,  # Number of retry attempts for API calls
        'CACHE_ENABLED': True,  # Enable response caching
        'CACHE_TIMEOUT': 300,  # Cache timeout in seconds (5 minutes)
    }
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._config = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from environment variables."""
        for key, default_value in self.DEFAULT_CONFIG.items():
            # Get value from environment or use default
            value = os.getenv(key, default_value)
            
            # Convert string values to appropriate types
            if isinstance(default_value, bool):
                if isinstance(value, str):
                    value = value.lower() in ('true', 'yes', '1', 'y')
            elif isinstance(default_value, int):
                if isinstance(value, str):
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {key}: {value}, using default: {default_value}")
                        value = default_value
            
            self._config[key] = value
            
        # Special case: Force mock data if no token is provided
        if not self._config['MOODLE_API_TOKEN'] or self._config['MOODLE_API_TOKEN'] == 'your_moodle_api_token_here':
            self._config['USE_MOCK_DATA'] = True
            logger.info("No valid Moodle API token found, forcing mock data mode")
            
        # Set logging level
        log_level = self._config['LOG_LEVEL'].upper()
        try:
            logging.getLogger().setLevel(getattr(logging, log_level))
        except AttributeError:
            logger.warning(f"Invalid log level: {log_level}, using INFO")
            logging.getLogger().setLevel(logging.INFO)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
        
    def __getitem__(self, key: str) -> Any:
        """Dictionary-style access to configuration values."""
        return self._config[key]
        
    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        return key in self._config
        
    def as_dict(self) -> Dict[str, Any]:
        """
        Get a copy of the configuration as a dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self._config.copy()
        
    def create_env_file(self, path: Optional[str] = None) -> None:
        """
        Create a .env file with default configuration.
        
        Args:
            path: Path to the .env file, defaults to current directory
        """
        if path is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
            
        # Don't overwrite existing .env file
        if os.path.exists(path):
            logger.info(f".env file already exists at {path}")
            return
            
        with open(path, 'w') as f:
            f.write("""# Moodle API Configuration
# URL of the Moodle instance
MOODLE_URL=https://moodle.concordia.ca

# API token for Moodle Web Services
# You need to generate this token in your Moodle account
# If empty or set to the default value, mock data will be used
MOODLE_API_TOKEN=your_moodle_api_token_here

# Flask server settings
FLASK_SECRET_KEY=campus-underground-secret-key
PORT=5002
DEBUG=True

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Force mock data even if token is provided
USE_MOCK_DATA=False

# API request timeout in seconds
TIMEOUT=30

# Number of retry attempts for API calls
RETRY_ATTEMPTS=3

# Caching settings
CACHE_ENABLED=True
CACHE_TIMEOUT=300
""")
        logger.info(f"Created .env file at {path}")
        
# Create a singleton instance
config = MoodleConfig()

# For testing
if __name__ == '__main__':
    print("Moodle Configuration:")
    for key, value in config.as_dict().items():
        # Don't print the token
        if key == 'MOODLE_API_TOKEN':
            value = '********' if value else '(not set)'
        print(f"{key}: {value}")
