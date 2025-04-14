from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
from .collage_from_embeddings import generate_collage_from_image_urls
from PIL import Image
import requests
from io import BytesIO
import time
from starlette.concurrency import run_in_threadpool


app = FastAPI()

class CollageRequest(BaseModel):
    images: list[str]

def load_images_from_urls(url_list):
    images = []
    for url in url_list:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
    return images

@app.post("/generate_collage")
async def generate_collage(request: Request):
    data = await request.json()
    image_urls = data.get("images", [])

    collage_path = await run_in_threadpool(generate_collage_from_image_urls, image_urls, load_images_from_urls)

    return FileResponse(collage_path, media_type="image/jpeg")