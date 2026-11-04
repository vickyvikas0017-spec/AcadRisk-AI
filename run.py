import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app
from app.database.connection import db_manager
from scripts.init_db import initialize_database
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Verify database is initialized
try:
    initialize_database()
except Exception as e:
    logger.warning(f"Database check warning: {e}")

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    logger.info(f"Starting AcadRisk AI System on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

