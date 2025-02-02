# import json
# import os
# import groq
# from dotenv import load_dotenv


# # Load environment variables from .env file
# load_dotenv()

# # Load environment variables
# api_key = os.getenv("GROQ_API_KEY")
# model = os.getenv("MODEL")


# def get_groq_response(prompt: str):
#     """
#     Get a response from the GROQ LLM API, using Redis cache if available.

#     Args:
#         prompt (str): The user's prompt.

#     Returns:
#         dict: The response from the API.
#     """
#     print(f"Fetching response for prompt: {prompt}")
#     try:
#         client = groq.Client(api_key=api_key)
#         response = client.chat.completions.create(
#             model=model, messages=[{"role": "user", "content": prompt}]
#         )
#         result = response.json()
#         print(f"Cache set for prompt: {prompt}")
#         return result
#     except Exception as e:
#         print(f"Error fetching response: {e}")
#         return {"error": "Failed to fetch response"}


# prompt = "hello"
# data = get_groq_response(prompt)
# print(data)
# # Convert the string to a Python dictionary
# parsed_data = json.loads(data)

# # Access the message content
# message_content = parsed_data["choices"][0]["message"]["content"]

# print(message_content)
# print(json.dumps(message_content))


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

from passlib.context import CryptContext
import bcrypt

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


from typing import Dict


def login(user: Dict, db: Session = Depends(get_db)):
    """
    User login endpoint.
    """
    logger.info(f"User login attempt")

    # Simulating fetching the user from the database
    db_user = {
        "password": "$2b$12$rAmQ/AWbhQZdaWrkA22KiuZnmPw1j8glx7ORGeA/Wm7i9Tjo59HlO"
    }

    # Correctly accessing the dictionary values
    if db_user and verify_password(user["password"], db_user["password"]):
        # Create JWT token
        access_token = create_token(
            {"sub": user["username"]}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    logger.warning(f"Invalid login attempt")
    raise HTTPException(status_code=401, detail="Invalid credentials")


def register(user: Dict, db: Session = Depends(get_db)):
    logger.info(f"Registering user: {user['username']}")
    try:
        # Test the database connection before proceeding
        # Check if user already exists
        logger.debug(f"Checking if user {user['username']} already exists.")

        # Hash the password
        logger.debug(f"Hashing the password for {user['username']}.")
        hashed_password = pwd_context.hash(user["password"])
        print(hashed_password)
    except Exception as e:
        logger.error(f"Error during getting user from db {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user from db")

    try:
        # Create a new user and store in the database
        db_user = User(username=user["username"], password=hashed_password)
        print(db_user)
    except Exception as e:
        logger.error(f"Error during creating a new user {user['username']}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create a new user")
    # try:
    #     logger.debug(f"Adding {user.username} to the database.")
    #     db.add(db_user)
    #     db.commit()
    #     db.refresh(db_user)
    #     logger.info(f"User {user.username} successfully registered.")
    #     return {"message": "User registered successfully"}
    # except Exception as e:
    #     logger.error(f"Error storing of user to the db {user.username}: {str(e)}")
    #     raise HTTPException(status_code=500, detail="Failed to store of user to the db")


print(bcrypt.__version__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("test123")
print(hashed_password)
print(login({"username": "test_user", "password": "test123"}))
print(register({"username": "user1", "password": "user1"}))
