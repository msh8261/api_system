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

import uvicorn
import requests
import asyncio
import json
import groq
from traceback import format_exc
from pydantic import BaseModel
from fastapi import BackgroundTasks
from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import WebSocketDisconnect
from jose import JWTError, jwt
from dotenv import load_dotenv
from log import logger
from backend.utils.redis_cache import (
    get_cached_response,
    set_cached_response,
)  # Correct function names
from backend.utils.kafka_producer import send_message_to_kafka
from backend.utils.kafka_producer import send_message_to_kafka_v1
from backend.routers.users import login, register
from backend.database import get_db, Session
from pydantic import BaseModel
from backend.database import init_db

# Load environment variables from .env file
load_dotenv()

# Load environment variables
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL")
kafka_topic = os.getenv("KAFKA_TOPIC", "default_topic")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_groq_response(prompt: str):
    cached_response = get_cached_response(prompt)
    if cached_response:
        return json.loads(cached_response)

    try:
        # Run the blocking GROQ API call in a separate thread
        client = groq.Client(api_key=api_key)
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        result = response.json()
        set_cached_response(prompt, json.dumps(result), 3600)
        return result
    except Exception as e:
        logger.error(f"Error fetching response: {e}")
        return {"error": "Failed to fetch response"}


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Chat endpoint to get a response from the GROQ LLM API.

    Args:
        request (ChatRequest): The request containing the user's message.
        token (str): The access token for authentication.

    Returns:
        dict: The response from the API.
    """
    try:
        user_input = request.message
        response = await get_groq_response(user_input)
        # Convert the string to a Python dictionary
        parsed_data = json.loads(response)
        # Access the message content
        response = parsed_data["choices"][0]["message"]["content"]
        background_tasks.add_task(
            send_message_to_kafka_v1,
            kafka_topic,
            {"user_input": user_input, "response": response},
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process request")


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returns the decoded token payload if valid
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    # Extract the token from the query parameters
    token = websocket.query_params.get("token")
    logger.debug(f"Extracted token from the query parameters: {token}")
    if not token:
        await websocket.close(code=1008)  # Invalid token error
        logger.error("WebSocket connection failed: No token provided.")
        return

    # Verify the token here (this is where JWT validation happens)
    user = verify_token(token)  # No 'await' needed here
    if not user:
        await websocket.close(code=1008)  # Invalid token error
        logger.error("WebSocket connection failed: Invalid token.")
        return

    await websocket.accept()
    try:
        while True:
            logger.debug(f"Received data in websocket")
            data = await websocket.receive_text()
            logger.debug(f"Received data from client: {data}")  # Log the received data
            # Get response from GROQ
            response = await get_groq_response(data)
            # Convert the string to a Python dictionary
            parsed_data = json.loads(response)
            # Access the message content
            answer = parsed_data["choices"][0]["message"]["content"]
            logger.debug(f"Sending response: {answer}")  # Log the response to be sent
            # Send the answer back to the WebSocket client
            background_tasks.add_task(
                send_message_to_kafka_v1,
                kafka_topic,
                {"user_input": data, "response": answer},
            )
            if answer:
                await websocket.send_text(json.dumps(answer))
            else:
                logger.error("No answer found, sending error message.")
                await websocket.send_text(
                    json.dumps({"error": "No answer found"})
                )  # Send an error message if no answer
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint to authenticate users.

    Args:
        request (LoginRequest): The request containing the user's credentials.

    Returns:
        dict: The authentication response.
    """
    try:
        logger.debug(f"Login request received: {request}")
        response = login(request, db)
        logger.debug(f"Login response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process login request")


@app.post("/register")
def register_endpoint(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        logger.debug(f"Register request received: {request}")
        response = register(request, db)
        logger.debug(f"Register response: {response}")
        return response
    except Exception as e:
        logger.error(
            f"Error in Register endpoint: {str(e)}\n{format_exc()}"
        )  # Capture full error traceback
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.on_event("startup")
def startup():
    # Initialize the database
    init_db()


@app.get("/")
def read_root():
    return {"message": "Backend server is running"}


if __name__ == "__main__":
    uvicorn.run(
        app, host="0.0.0.0", port=int(os.getenv("PORT", 8022)), log_level="debug"
    )
