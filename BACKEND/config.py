import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Application
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Security Headers
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate Limiting
    RATE_LIMIT = os.getenv('RATE_LIMIT', '100 per hour')
    
    # File Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    WORDLISTS_DIR = os.path.join(os.path.dirname(__file__), 'wordlists')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Analysis Settings
    MIN_PASSWORD_LENGTH = 1
    MAX_PASSWORD_LENGTH = 256
    ENTROPY_THRESHOLD_WEAK = 40
    ENTROPY_THRESHOLD_STRONG = 70
    
    # HIBP Settings
    HIBP_API_URL = "https://api.pwnedpasswords.com/range/"
    HIBP_TIMEOUT = 5

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get appropriate config based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])