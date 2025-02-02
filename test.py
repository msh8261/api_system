import json
import os
import groq
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Load environment variables
api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("MODEL")


def get_groq_response(prompt: str):
    """
    Get a response from the GROQ LLM API, using Redis cache if available.

    Args:
        prompt (str): The user's prompt.

    Returns:
        dict: The response from the API.
    """
    print(f"Fetching response for prompt: {prompt}")
    try:
        client = groq.Client(api_key=api_key)
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        result = response.json()
        print(f"Cache set for prompt: {prompt}")
        return result
    except Exception as e:
        print(f"Error fetching response: {e}")
        return {"error": "Failed to fetch response"}


prompt = "hello"
data = get_groq_response(prompt)
print(data)
# Convert the string to a Python dictionary
parsed_data = json.loads(data)

# Access the message content
message_content = parsed_data["choices"][0]["message"]["content"]

print(message_content)
print(json.dumps(message_content))
