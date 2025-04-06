import os
import requests
from groq import Groq
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request

import numpy as np
from PIL import Image
from io import BytesIO
import diskcache as dc

# Constants
IMAGE_SIZE = (16, 16)

load_dotenv()

# Initialize Groq and Google settings
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL = "text-embedding-005"

# Save caches to the root of the project
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEMANTIC_CACHE_DIR = os.path.join(PROJECT_ROOT, "semantic_cache")
VISUAL_CACHE_DIR = os.path.join(PROJECT_ROOT, "visual_cache")

# Setup disk caches with fixed paths
semantic_cache = dc.Cache(SEMANTIC_CACHE_DIR)
visual_cache = dc.Cache(VISUAL_CACHE_DIR)


def image_url_to_semantic_vector(image_url: str) -> list[float]:
    if image_url in semantic_cache:
        return semantic_cache[image_url]

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

    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    access_token = credentials.token

    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {"instances": [{"content": description}]}
    response = requests.post(endpoint, headers=headers, json=payload)

    if response.status_code == 200:
        embedding = response.json()["predictions"][0]["embeddings"]["values"]
        semantic_cache[image_url] = embedding
        return embedding
    else:
        raise Exception(f"Google API error: {response.status_code} - {response.text}")

def image_urls_to_semantic_vectors(image_urls: list[str]) -> np.ndarray:
    vectors = [image_url_to_semantic_vector(url) for url in image_urls]
    return np.array(vectors, dtype=np.float32)

def load_images_from_urls(url_list: list[str]) -> list[Image.Image]:
    images = []
    for url in url_list:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
    return images

def flatten_images(images: list[Image.Image], size=IMAGE_SIZE) -> np.ndarray:
    return np.array([np.asarray(img.resize(size)).flatten() for img in images])

def image_url_to_visual_vector(image_url: str) -> np.ndarray:
    if image_url in visual_cache:
        print(f'used visual cache for image {image_url}')
        return visual_cache[image_url]

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img_resized = img.resize(IMAGE_SIZE)
    vector = np.asarray(img_resized).flatten().astype(np.float32)

    visual_cache[image_url] = vector
    return vector

def image_urls_to_visual_vectors(image_urls: list[str]) -> np.ndarray:
    vectors = [image_url_to_visual_vector(url) for url in image_urls]
    return np.array(vectors, dtype=np.float32)

def normalize_vectors(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.clip(norms, a_min=1e-8, a_max=None)

def image_urls_to_vectors(image_urls: list[str]) -> np.ndarray:
    semantic_vecs = image_urls_to_semantic_vectors(image_urls)
    visual_vecs = image_urls_to_visual_vectors(image_urls)

    # Fixes bug of semantic vecs being overpowered by visual vecs
    semantic_vecs = normalize_vectors(semantic_vecs)
    visual_vecs = normalize_vectors(visual_vecs)

    # print(f"semantic_vecs.shape {semantic_vecs.shape}")
    # print(f"visual_vecs.shape {visual_vecs.shape}")

    # print(f"semantic_vecs {semantic_vecs}")
    # print(f"visual_vecs {visual_vecs}")

    return np.concatenate([semantic_vecs, visual_vecs], axis=1)
