import uvicorn
from fastapi import FastAPI, WebSocket
import requests
import redis
import json
import groq

# Your API key and model
api_key = "your_api_key_here"
model = "your_model_here"


app = FastAPI()

# Initialize Redis cache
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_groq_response(prompt: str):
    cached_response = redis_client.get(prompt)
    if cached_response:
        return json.loads(cached_response)
    
    client = groq.Client(api_key=api_key)
    # Use chat.completions to send the prompt and get a response
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )    
    result = response.json()
    redis_client.setex(prompt, 3600, json.dumps(result))  # Cache for 1 hour
    return result

@app.post("/chat")
def chat(request: dict):
    user_input = request.get("message")
    response = get_groq_response(user_input)
    return {"response": response}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = get_groq_response(data)
        await websocket.send_text(json.dumps(response))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
