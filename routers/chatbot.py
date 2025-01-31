from fastapi import APIRouter
import requests
import os

router = APIRouter()

GROQ_LLM_API = os.getenv("GROQ_LLM_API", "https://api.groq.com/v1/chat")

@router.post("/")
def get_chat_response(message: str):
    payload = {"message": message}
    response = requests.post(GROQ_LLM_API, json=payload)
    return response.json()
