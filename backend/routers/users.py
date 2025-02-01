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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from backend.log import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    password: str

users_db = {"test_user": {"username": "test_user", "password": "test123"}}

def create_token(data: dict, expires_delta: timedelta):
    """
    Create a JWT token.
    
    Args:
        data (dict): The data to encode in the token.
        expires_delta (timedelta): The token expiration time.
    
    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(user: User):
    """
    User login endpoint.
    
    Args:
        user (User): The user credentials.
    
    Returns:
        dict: The access token and token type.
    
    Raises:
        HTTPException: If the credentials are invalid.
    """
    logger.info(f"User login attempt: {user.username}")
    if user.username in users_db and users_db[user.username]["password"] == user.password:
        access_token = create_token({"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "token_type": "bearer"}
    logger.warning(f"Invalid login attempt: {user.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")
