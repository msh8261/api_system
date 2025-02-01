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
import json
import groq
from fastapi import FastAPI, WebSocket, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi import WebSocketDisconnect 
from jose import JWTError, jwt
from dotenv import load_dotenv
from backend.log import logger
from backend.utils.redis_cache import get_cached_response, set_cached_response  # Correct function names
from backend.utils.kafka_producer import send_message  # Import Kafka producer function
from backend.routers.users import login  # Import login function
from pydantic import BaseModel

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

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
async def login_endpoint(request: LoginRequest):
    """
    Login endpoint to authenticate users.
    
    Args:
        request (LoginRequest): The request containing the user's credentials.
    
    Returns:
        dict: The authentication response.
    """
    try:
        logger.debug(f"Login request received: {request}")
        response = login(request)
        logger.debug(f"Login response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to process login request")

def get_groq_response(prompt: str):
    """
    Get a response from the GROQ LLM API, using Redis cache if available.
    
    Args:
        prompt (str): The user's prompt.
    
    Returns:
        dict: The response from the API.
    """
    logger.info(f"Fetching response for prompt: {prompt}")
    cached_response = get_cached_response(prompt)
    if (cached_response):
        logger.info(f"Cache hit for prompt: {prompt}")
        return json.loads(cached_response)
    
    try:
        client = groq.Client(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )    
        result = response.json()
        set_cached_response(prompt, json.dumps(result), 3600)  # Cache for 1 hour
        logger.info(f"Cache set for prompt: {prompt}")
        return result
    except Exception as e:
        logger.error(f"Error fetching response: {e}")
        return {"error": "Failed to fetch response"}

@app.post("/chat")
def chat(request: dict, token: str = Depends(oauth2_scheme)):
    """
    Chat endpoint to get a response from the GROQ LLM API.
    
    Args:
        request (dict): The request containing the user's message.
        token (str): The access token for authentication.
    
    Returns:
        dict: The response from the API.
    """
    try:
        user_input = request.get("message")
        response = get_groq_response(user_input)
        send_message(kafka_topic, {"user_input": user_input, "response": response})  # Send message to Kafka
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return {"error": "Failed to process request"}



async def verify_token(token: str):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Extract the token from the query parameters
    token = websocket.query_params.get("token")
    logger.debug(f"Extracted token from the query parameters: {token}")
    if not token:
        await websocket.close(code=1008)  # Invalid token error
        logger.error("WebSocket connection failed: No token provided.")
        return

    # Verify the token here (this is where JWT validation happens)
    user = await verify_token(token)
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
            response = get_groq_response(data)
            logger.debug(f"Sending response: {response}")  # Log the response to be sent
            send_message(kafka_topic, {"user_input": data, "response": response})  # Send message to Kafka
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


@app.get("/")
def read_root():
    return {"message": "Backend server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8022)), log_level="debug")

