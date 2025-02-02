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

import os
import sys
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from log import logger
from dotenv import load_dotenv
from passlib.context import CryptContext  # For password hashing
from backend.database import User, get_db, get_user_from_db, Session, test_db_connection

# Load environment variables from .env file
load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    username: str
    password: str


def create_token(data: dict, expires_delta: timedelta):
    """
    Create a JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str):
    """
    Verify a plain password against a hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def login(user: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint.
    """
    logger.info(f"User login attempt: {user.username}")
    # Fetch user from the database
    db_user = get_user_from_db(db, user.username)

    if db_user and verify_password(user.password, db_user.password):
        # Create JWT token
        access_token = create_token(
            {"sub": user.username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    logger.warning(f"Invalid login attempt: {user.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")


def register(user: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Registering user: {user.username}")
    try:
        # Test the database connection before proceeding
        test_db_connection(db)
        # Check if user already exists
        logger.debug(f"Checking if user {user.username} already exists.")
        db_user = get_user_from_db(db, user.username)
        if db_user:
            logger.warning(f"Username {user.username} already taken.")
            raise HTTPException(status_code=400, detail="Username already taken")

        # Hash the password
        logger.debug(f"Hashing the password for {user.username}.")
        hashed_password = pwd_context.hash(user.password)
    except Exception as e:
        logger.error(f"Error during getting user from db {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user from db")

    try:
        # Create a new user and store in the database
        db_user = User(username=user.username, password=hashed_password)
    except Exception as e:
        logger.error(f"Error during creating a new user {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create a new user")
    try:
        logger.debug(f"Adding {user.username} to the database.")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User {user.username} successfully registered.")
        return {"message": "User registered successfully"}
    except Exception as e:
        logger.error(f"Error storing of user to the db {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to store of user to the db")
