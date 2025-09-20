"""
Configuration module for autocoder - handles environment variable detection
and API endpoint configuration for Claude Code SDK.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Any

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class AutocoderConfig:
    """Handles autocoder configuration from environment variables and .env files."""
    
    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path.cwd()
        self.config = {}
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from .env file and environment variables."""
        # Try to load .env file from project directory
        if DOTENV_AVAILABLE:
            env_file = self.project_dir / '.env'
            if env_file.exists():
                load_dotenv(env_file)
        
        # Collect relevant environment variables
        self.config = {
            'base_url': os.getenv('ANTHROPIC_BASE_URL'),
            'api_key': os.getenv('ANTHROPIC_API_KEY') or os.getenv('ANTHROPIC_AUTH_TOKEN'),
            'model': os.getenv('ANTHROPIC_MODEL'),
            'small_fast_model': os.getenv('ANTHROPIC_SMALL_FAST_MODEL'),
            'timeout_ms': self._parse_int(os.getenv('API_TIMEOUT_MS')),
            'bedrock_region': os.getenv('AWS_REGION'),
            'vertex_project': os.getenv('VERTEX_PROJECT_ID'),
        }
    
    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Safely parse integer from environment variable."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def get_api_info(self) -> Dict[str, Any]:
        """Get API configuration information for display to user."""
        info = {}
        
        if self.config['base_url']:
            info['endpoint'] = self.config['base_url']
            info['custom'] = True
            
            # Detect known providers
            if 'z.ai' in self.config['base_url']:
                info['provider'] = 'Zhipu (GLM-4.5)'
            elif 'bedrock' in self.config['base_url']:
                info['provider'] = 'AWS Bedrock'
            elif 'vertex' in self.config['base_url']:
                info['provider'] = 'Google Vertex AI'
            else:
                info['provider'] = 'Custom API'
        else:
            info['endpoint'] = 'api.anthropic.com'
            info['provider'] = 'Anthropic Claude'
            info['custom'] = False
        
        if self.config['model']:
            info['model'] = self.config['model']
        
        return info
    
    def get_claude_code_options_updates(self) -> Dict[str, Any]:
        """Get additional options to pass to ClaudeCodeOptions."""
        updates = {}
        
        # Add any SDK-specific environment variables that might be supported
        # Note: This depends on what the Claude Code SDK actually supports
        
        return updates
    
    def has_custom_config(self) -> bool:
        """Check if any custom configuration is present."""
        return any(value is not None for value in self.config.values())
    
    def get_masked_config(self) -> Dict[str, Any]:
        """Get configuration with masked sensitive values for logging."""
        masked = {}
        for key, value in self.config.items():
            if value is None:
                continue
            if 'key' in key.lower() or 'token' in key.lower():
                masked[key] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
            else:
                masked[key] = value
        return masked