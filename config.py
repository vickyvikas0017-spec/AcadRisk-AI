import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'acadrisk-ai-super-secret-key-2026')
    BASE_DIR = BASE_DIR
    
    # Storage directories
    UPLOAD_FOLDER = os.path.join(BASE_DIR, os.getenv('UPLOAD_FOLDER', 'uploads'))
    MODEL_FOLDER = os.path.join(BASE_DIR, os.getenv('MODEL_FOLDER', 'trained_models'))
    BACKUP_FOLDER = os.path.join(BASE_DIR, os.getenv('BACKUP_FOLDER', 'backups'))
    DATASET_DIR = os.path.join(BASE_DIR, 'datasets')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    
    # Primary MySQL 8 configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'rootpassword')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'acadrisk_db')
    
    MYSQL_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    DATABASE_URL = os.getenv('DATABASE_URL', MYSQL_URL)
    
    ENABLE_FALLBACK = os.getenv('ENABLE_FALLBACK', 'true').lower() == 'true'
    FALLBACK_SQLITE_URL = os.getenv('FALLBACK_SQLITE_URL', f"sqlite:///{BASE_DIR / 'acadrisk_fallback.db'}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Thresholds
    HIGH_RISK_THRESHOLD = float(os.getenv('HIGH_RISK_THRESHOLD', 40.0))
    MEDIUM_RISK_THRESHOLD = float(os.getenv('MEDIUM_RISK_THRESHOLD', 60.0))

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_URL = f"sqlite:///{BASE_DIR / 'acadrisk_test.db'}"
    ENABLE_FALLBACK = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

