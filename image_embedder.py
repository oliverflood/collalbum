import os
import requests
from groq import Groq
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request

import numpy as np
from PIL import Image
from io import BytesIO

# Constants
IMAGE_SIZE = (16, 16)

load_dotenv()

# Initialize Groq and Google settings
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL = "text-embedding-005"

def image_urls_to_semantic_vectors(image_urls: list[str]) -> np.ndarray:
    descriptions = []
    for url in image_urls:
        groq_response = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this album cover in a sentence."},
                        {"type": "image_url", "image_url": {"url": url}},
                    ],
                }
            ],
            temperature=0.7,
            max_completion_tokens=256,
        )
        description = groq_response.choices[0].message.content
        print(f"Groq Description: {description}")
        descriptions.append({"content": description})

    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    access_token = credentials.token

    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {"instances": descriptions}
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        embeddings = [pred["embeddings"]["values"] for pred in response.json()["predictions"]]
        return np.array(embeddings, dtype=np.float32)
    else:
        raise Exception(f"Google API error: {response.status_code} - {response.text}")

def load_images_from_urls(url_list: list[str]) -> list[Image.Image]:
    images = []
    for url in url_list:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
    return images

def flatten_images(images: list[Image.Image], size=IMAGE_SIZE) -> np.ndarray:
    return np.array([np.asarray(img.resize(size)).flatten() for img in images])

def image_urls_to_visual_vectors(image_urls: list[str]) -> np.ndarray:
    images = load_images_from_urls(image_urls)
    flattened = flatten_images(images)
    return flattened.astype(np.float32)

def image_urls_to_vectors(image_urls: list[str]) -> np.ndarray:
    semantic_vecs = image_urls_to_semantic_vectors(image_urls)
    visual_vecs = image_urls_to_visual_vectors(image_urls)

    print(f"semantic_vecs.shape {semantic_vecs.shape}")
    print(f"visual_vecs.shape {visual_vecs.shape}")

    return np.concatenate([semantic_vecs, visual_vecs], axis=1)
