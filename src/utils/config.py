import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CACHE_DIR = os.getenv('CACHE_DIR', './temp_videos')
    PROXY_TIMEOUT = int(os.getenv('PROXY_TIMEOUT', '10'))
    MAX_PROXIES = int(os.getenv('MAX_PROXIES', '20'))
    PROXY_REFRESH_INTERVAL = int(os.getenv('PROXY_REFRESH_INTERVAL', '300'))
    VIDEO_QUALITY = os.getenv('VIDEO_QUALITY', 'best')
    FORCE_PROXY = os.getenv('FORCE_PROXY', 'True').lower() == 'true'
    ALLOW_FALLBACK = os.getenv('ALLOW_FALLBACK', 'True').lower() == 'true'
    CLEAN_CACHE_ON_EXIT = os.getenv('CLEAN_CACHE_ON_EXIT', 'True').lower() == 'true'
    MAX_CACHE_SIZE = int(os.getenv('MAX_CACHE_SIZE', '500'))