import os
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
from backend.log import logger

# Load environment variables from .env file
load_dotenv()

mysql_host = os.getenv("mysql_host", "localhost")
mysql_port = int(os.getenv("mysql_port", "3306"))
mysql_user = os.getenv("mysql_user", "root")
mysql_password = os.getenv("mysql_password", "")
mysql_database = os.getenv("mysql_database", "chatbot")


# database URL
DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"


def test_db_connection():
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # Run a simple query
        print("✅ Database connection successful!")
        db.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")


test_db_connection()
