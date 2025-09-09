#!/usr/bin/env python3

"""
SCRAPING CONFIGURATION
Configuration file for the optimized scraping system
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class ScrapingConfig:
    """Configuration for optimized scraping"""
    
    # Batch Processing
    MAX_BATCH_SIZE: int = 15  # Reduced from 44 to 15
    MAX_CONCURRENT_WEBSITES: int = 10  # Process 10 websites simultaneously
    
    # Timeouts
    TIMEOUT_PER_WEBSITE: int = 300  # 5 minutes max per website
    TIMEOUT_PER_BATCH: int = 900  # 15 minutes max per batch
    TIMEOUT_PER_CHUNK: int = 600  # 10 minutes max per chunk
    
    # Resource Limits
    MAX_CPU_USAGE: float = 80.0  # Max 80% CPU usage
    MAX_MEMORY_USAGE: float = 85.0  # Max 85% memory usage
    MAX_DB_CONNECTIONS: int = 20  # Max database connections
    
    # Monitoring
    RESOURCE_CHECK_INTERVAL: int = 30  # Check resources every 30 seconds
    PROGRESS_UPDATE_INTERVAL: int = 10  # Update progress every 10 seconds
    
    # Retry Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 60  # 1 minute
    EXPONENTIAL_BACKOFF: bool = True
    
    # Queue Management
    MAX_QUEUE_SIZE: int = 100
    QUEUE_TIMEOUT: int = 300  # 5 minutes
    
    # Database
    BATCH_INSERT_SIZE: int = 50
    DB_POOL_SIZE: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "MAX_BATCH_SIZE": self.MAX_BATCH_SIZE,
            "MAX_CONCURRENT_WEBSITES": self.MAX_CONCURRENT_WEBSITES,
            "TIMEOUT_PER_WEBSITE": self.TIMEOUT_PER_WEBSITE,
            "TIMEOUT_PER_BATCH": self.TIMEOUT_PER_BATCH,
            "TIMEOUT_PER_CHUNK": self.TIMEOUT_PER_CHUNK,
            "MAX_CPU_USAGE": self.MAX_CPU_USAGE,
            "MAX_MEMORY_USAGE": self.MAX_MEMORY_USAGE,
            "MAX_DB_CONNECTIONS": self.MAX_DB_CONNECTIONS,
            "RESOURCE_CHECK_INTERVAL": self.RESOURCE_CHECK_INTERVAL,
            "PROGRESS_UPDATE_INTERVAL": self.PROGRESS_UPDATE_INTERVAL,
            "MAX_RETRIES": self.MAX_RETRIES,
            "RETRY_DELAY": self.RETRY_DELAY,
            "EXPONENTIAL_BACKOFF": self.EXPONENTIAL_BACKOFF,
            "MAX_QUEUE_SIZE": self.MAX_QUEUE_SIZE,
            "QUEUE_TIMEOUT": self.QUEUE_TIMEOUT,
            "BATCH_INSERT_SIZE": self.BATCH_INSERT_SIZE,
            "DB_POOL_SIZE": self.DB_POOL_SIZE,
            "DB_POOL_TIMEOUT": self.DB_POOL_TIMEOUT,
            "LOG_LEVEL": self.LOG_LEVEL,
            "LOG_FORMAT": self.LOG_FORMAT
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ScrapingConfig':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def validate(self) -> bool:
        """Validate configuration values"""
        if self.MAX_BATCH_SIZE <= 0:
            raise ValueError("MAX_BATCH_SIZE must be positive")
        
        if self.MAX_CONCURRENT_WEBSITES <= 0:
            raise ValueError("MAX_CONCURRENT_WEBSITES must be positive")
        
        if self.TIMEOUT_PER_WEBSITE <= 0:
            raise ValueError("TIMEOUT_PER_WEBSITE must be positive")
        
        if self.MAX_CPU_USAGE <= 0 or self.MAX_CPU_USAGE > 100:
            raise ValueError("MAX_CPU_USAGE must be between 0 and 100")
        
        if self.MAX_MEMORY_USAGE <= 0 or self.MAX_MEMORY_USAGE > 100:
            raise ValueError("MAX_MEMORY_USAGE must be between 0 and 100")
        
        return True

# Default configuration
DEFAULT_CONFIG = ScrapingConfig()

# Production configuration (more conservative)
PRODUCTION_CONFIG = ScrapingConfig(
    MAX_BATCH_SIZE=10,
    MAX_CONCURRENT_WEBSITES=5,
    TIMEOUT_PER_WEBSITE=180,  # 3 minutes
    MAX_CPU_USAGE=70.0,
    MAX_MEMORY_USAGE=80.0,
    MAX_RETRIES=2
)

# Development configuration (more aggressive)
DEVELOPMENT_CONFIG = ScrapingConfig(
    MAX_BATCH_SIZE=20,
    MAX_CONCURRENT_WEBSITES=15,
    TIMEOUT_PER_WEBSITE=600,  # 10 minutes
    MAX_CPU_USAGE=90.0,
    MAX_MEMORY_USAGE=90.0,
    MAX_RETRIES=5
)

def get_config(environment: str = "default") -> ScrapingConfig:
    """Get configuration for specified environment"""
    configs = {
        "default": DEFAULT_CONFIG,
        "production": PRODUCTION_CONFIG,
        "development": DEVELOPMENT_CONFIG
    }
    
    if environment not in configs:
        print(f"⚠️  Unknown environment '{environment}', using default")
        environment = "default"
    
    config = configs[environment]
    config.validate()
    
    print(f"✅ Loaded {environment} configuration:")
    print(f"   Max batch size: {config.MAX_BATCH_SIZE}")
    print(f"   Max concurrent websites: {config.MAX_CONCURRENT_WEBSITES}")
    print(f"   Timeout per website: {config.TIMEOUT_PER_WEBSITE}s")
    print(f"   Max CPU usage: {config.MAX_CPU_USAGE}%")
    print(f"   Max memory usage: {config.MAX_MEMORY_USAGE}%")
    
    return config

if __name__ == "__main__":
    # Test configuration loading
    print("🧪 Testing configuration loading...")
    
    configs = ["default", "production", "development"]
    for env in configs:
        print(f"\n📋 {env.upper()} Configuration:")
        config = get_config(env)
        print(f"   Config dict: {config.to_dict()}")
