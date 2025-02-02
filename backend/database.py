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


from sqlalchemy.orm import Session
from passlib.context import CryptContext  # For password hashing
from database import SessionLocal, init_db
import pymongo
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from database import Base
from dotenv import load_dotenv
from backend.log import logger

# Load environment variables from .env file
load_dotenv()

mysql_host=os.getenv("MYSQL_HOST", "localhost")
mysql_user=os.getenv("MYSQL_USER", "root")
mysql_password=os.getenv("MYSQL_PASSWORD", "")
mysql_database=os.getenv("MYSQL_DB", "chatbot")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# database URL 
DATABASE_URL = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"

# SQLAlchemy setup
Base = declarative_base()

# Create a MySQL engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

mongo_host=os.getenv("mongo_host")
mongo_port=os.getenv("mongo_port")
mongo_database=os.getenv("mongo_database") 
localhost:27017
# MongoDB Connection
mongo_client = pymongo.MongoClient(f"mongodb://{mongo_host}:{mongo_port}")
mongo_db = mongo_client[mongo_database]
logger.info("MongoDB connection established")



# create model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))



def init_db():
    """ initialize the database"""
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_db(db: Session, username: str):
    """
    Get a user from the database by username.
    """
    return db.query(User).filter(User.username == username).first()

