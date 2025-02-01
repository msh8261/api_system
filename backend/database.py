import os
import sys

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory path of the current file
current_dir_path = os.path.dirname(current_file_path)
# Get the parent directory path
parent_dir_path = os.path.dirname(current_dir_path)
# Add the parent directory path to the sys.path
sys.path.insert(0, parent_dir_path)


import pymysql
import pymongo
from dotenv import load_dotenv
from backend.log import logger

# Load environment variables from .env file
load_dotenv()


# MySQL Connection
mysql_conn = pymysql.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD", ""),
    database=os.getenv("MYSQL_DB", "chatbot")
)
logger.info("MySQL connection established")

# MongoDB Connection
mongo_client = pymongo.MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
mongo_db = mongo_client["chatbot"]
logger.info("MongoDB connection established")
