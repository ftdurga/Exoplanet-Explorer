import os
import mysql.connector
from dotenv import load_dotenv

# Custom Database Connection Error
class DatabaseConnectionError(Exception):
    pass

load_dotenv()  # reads .env into the environment                                
def get_connection():
    try: 
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),  
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
    except mysql.connector.Error as e:
        raise DatabaseConnectionError(f"Could not connect to {os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}: {e}") from e
    # preserves the original traceback via from e
    