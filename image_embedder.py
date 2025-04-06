import os
import requests
from groq import Groq
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request

load_dotenv()

# Initialize Groq and Google settings
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL = "text-embedding-005"

def image_url_to_vector(image_url: str) -> list[float]:
    """
    Given an image URL, returns a semantic vector embedding using Groq + Google Vertex AI.
    """
    # Describe the image using Groq
    groq_response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this album cover in a sentence."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0.7,
        max_completion_tokens=256,
    )
    description = groq_response.choices[0].message.content
    print(f"Groq Description: {description}")

    # Get embedding from Google Vertex AI
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    access_token = credentials.token

    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "instances": [
            {"content": description}
        ]
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        embedding = response.json()["predictions"][0]["embeddings"]["values"]
        return embedding
    else:
        raise Exception(f"Google API error: {response.status_code} - {response.text}")
