import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd'),
    'database': os.getenv('DB_NAME', 'coding_practice_system'),
    'port': int(os.getenv('DB_PORT', 3306))
}
