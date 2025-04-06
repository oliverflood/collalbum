import os
import requests
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL = "text-embedding-005"

credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
credentials.refresh(Request())
access_token = credentials.token

endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

text_input = "A one sentence description of my album collage."

payload = {
    "instances": [
        {"content": text_input}
    ]
}

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

response = requests.post(endpoint, headers=headers, json=payload)

if response.status_code == 200:
    embedding = response.json()["predictions"][0]["embeddings"]["values"]
    print("Embedding vector:", embedding)
else:
    print("Error:", response.status_code, response.text)
