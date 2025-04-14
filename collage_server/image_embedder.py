import os
import requests
from groq import Groq
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image
from io import BytesIO
import diskcache as dc
from more_itertools import chunked
import base64

# Constants
IMAGE_SIZE = (16, 16) # Used for visual embeddings
REDUCED_IMAGE_SIZE = (64, 64) # Used for semantic embeddings


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


def image_url_to_description(image_url: str) -> str:
    key = image_url + "_desc"
    if key in semantic_cache:
        return semantic_cache[key]

    try:
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img_resized = img.resize(REDUCED_IMAGE_SIZE)

        buffer = BytesIO()
        img_resized.save(buffer, format="JPEG")
        base64_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        data_url = f"data:image/jpeg;base64,{base64_img}"

    except Exception as e:
        raise RuntimeError(f"Failed to download/encode image from {image_url}: {e}")

    # Groq call using base64-encoded image
    groq_response = groq_client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this album cover in a sentence. Absolutely no more than 10 words. Avoid boilerplate words like 'The album cover features' and instead get straight into the description."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url
                        }
                    },
                ],
            }
        ],
        temperature=0.7,
        max_completion_tokens=256,
    )

    description = groq_response.choices[0].message.content
    print(f"Groq Description: {description}")
    semantic_cache[key] = description
    return description


def image_urls_to_semantic_vectors(image_urls: list[str]) -> np.ndarray:
    # Get or generate descriptions
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=1) as executor:
        descriptions = list(executor.map(image_url_to_description, image_urls))

    # Generate embeddings (batch call)
    vectors = get_google_embeddings(descriptions)

    # Cache final embeddings
    for url, vector in zip(image_urls, vectors):
        semantic_cache[url] = vector

    return np.array(vectors, dtype=np.float32)


def get_google_embeddings(descriptions: list[str]) -> list[list[float]]:
    print("Starting google batch embeddings")
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(Request())
    access_token = credentials.token

    endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{MODEL}:predict"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "instances": [{"content": desc} for desc in descriptions]
    }

    response = requests.post(endpoint, headers=headers, json=payload)

    print("Ending google batch embeddings")

    if response.status_code == 200:
        return [pred["embeddings"]["values"] for pred in response.json()["predictions"]]
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

def image_url_to_visual_vector(image_url: str) -> np.ndarray:
    if image_url in visual_cache:
        print(f'Cache hit: {image_url[24:]}')
        return visual_cache[image_url]

    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img_resized = img.resize(IMAGE_SIZE)
    vector = np.asarray(img_resized).flatten().astype(np.float32)

    visual_cache[image_url] = vector
    return vector

def image_urls_to_visual_vectors(image_urls: list[str]) -> np.ndarray:
    with ThreadPoolExecutor(max_workers=5) as executor:
        vectors = list(executor.map(image_url_to_visual_vector, image_urls))
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
