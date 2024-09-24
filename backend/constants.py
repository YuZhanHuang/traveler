import os

LOG_PATH = os.environ.get('LOGGER_PATH', '/app/logs')
LOG_FILE = os.environ.get('LOG_FILE', 'admin_dealer_service')
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOCAL_TZ = 'Asia/Taipei'