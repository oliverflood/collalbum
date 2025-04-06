from flask import Flask, request, jsonify, send_file
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import uuid
import requests
from io import BytesIO
import os

### Config ###

GRID_SIZE = 5
NUM_IMAGES = GRID_SIZE * GRID_SIZE
SAVE_DIR = "collages"
IMAGE_SIZE = (32, 32)
CANVAS_IMAGE_SIZE = (640, 640)

app = Flask(__name__)



### Image I/O Utilities ###

def load_images_from_urls(url_list):
    """
    Downloads and loads images from a list of URLs into memory.
    Returns a list of PIL Image objects.
    """
    images = []
    for i, url in enumerate(url_list):
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)

    print (f"NUMBER OF IMAGES: {len(images)}")
    return images

def save_images(images, save_dir="url_sample_images", prefix="img"):
    """
    Saves a list of PIL Images to a specified directory with auto-numbered filenames.
    """
    os.makedirs(save_dir, exist_ok=True)
    for i, img in enumerate(images):
        path = os.path.join(save_dir, f"{prefix}_{i:03d}.jpg")
        img.save(path)



### Image Processing ###

def flatten_images(images, size=IMAGE_SIZE):
    """
    Resizes and flattens images into 1D vectors for PCA.
    Returns a NumPy array of shape (num_images, features).
    """
    return np.array([np.asarray(img.resize(size)).flatten() for img in images])

def reduce_with_pca(data, n_components=2):
    """
    Reduces high-dimensional image data to 2D using PCA.
    """
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data)

def snap_images_x(coords, grid_size=GRID_SIZE):
    """
    Sorts and assigns x-grid positions based on PCA x-coords.
    """
    coords_copy = coords.copy()
    sorted_indices = np.argsort(coords_copy[:, 0])
    snapped = np.zeros_like(coords_copy)

    for i in range(coords_copy.shape[0]):
        bucket = i // grid_size
        snapped[sorted_indices[i], 0] = bucket
        snapped[sorted_indices[i], 1] = coords_copy[sorted_indices[i], 1]

    return snapped

def snap_images_y(coords, grid_size=GRID_SIZE):
    """
    For each x-bucket, sorts y-coordinates and assigns grid positions (top to bottom).
    """
    coords_copy = coords.copy()

    for bucket in range(grid_size):
        bucket_indices = np.where(coords_copy[:, 0] == bucket)[0]
        sorted_y = bucket_indices[np.argsort(-coords_copy[bucket_indices, 1])]

        for new_y, idx in enumerate(sorted_y):
            coords_copy[idx, 1] = grid_size - 1 - new_y

    return coords_copy

# def center_crop_fraction(img, fraction=0.8):
#     """
#     Center-crops an image to the specified fraction of its original size.
#     """
#     width, height = img.size
#     new_width = int(width * fraction)
#     new_height = int(height * fraction)

#     left = (width - new_width) // 2
#     top = (height - new_height) // 2
#     right = left + new_width
#     bottom = top + new_height

#     return img.crop((left, top, right, bottom))


### Visualization ###

def plot_images_on_canvas(images, coords, save_dir=SAVE_DIR):
    """
    Plots images on a canvas based on 2D coordinates and saves to disk.
    Returns the save path of the generated collage image.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(coords[:, 0].min(), coords[:, 0].max())
    ax.set_ylim(coords[:, 1].min(), coords[:, 1].max())
    ax.axis('off')

    base_zoom = 1.1 / GRID_SIZE
    for i, ((x, y), img) in enumerate(zip(coords, images)):
        size_factor = 2 - 1 * (i / NUM_IMAGES)
        imagebox = OffsetImage(img.resize(CANVAS_IMAGE_SIZE), zoom=base_zoom * size_factor)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    os.makedirs(save_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:6]
    save_path = os.path.join(save_dir, f'collage_{unique_id}.png')

    plt.savefig(save_path, dpi=100, bbox_inches='tight', pad_inches=0.0, transparent=True)
    # plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.0)
    plt.close(fig)

    print(f'Saved collage to {save_path}')
    return save_path



### Flask Route ###

@app.route('/generate_collage', methods=['POST'])
def generate_collage():
    """
    Flask endpoint that accepts a JSON payload of image URLs,
    generates a PCA-based collage layout, and returns the resulting image.

    Method: POST
    Endpoint: /generate_collage
    Content-Type: application/json

    Args (JSON payload):
        {
            "images": [
                "https://i.scdn.co/image/ab67616d0000b273...",
                "https://i.scdn.co/image/ab67616d0000b273...",
                ...
            ]
        }

    Returns:
        On success: PNG image file (binary) with Content-Type: image/png
        On failure: JSON object with error message and HTTP 400 or 500 status

    Example `curl` request:
        curl -X POST http://localhost:5000/generate_collage \
            -H "Content-Type: application/json" \
            -d '{
                  "images": [
                    "https://i.scdn.co/image/ab67616d0000b273...",
                    "https://i.scdn.co/image/ab67616d0000b273...",
                    ...
                  ]
                }' \
            --output result.png

    Notes:
        The number of image URLs must match the configured NUM_IMAGES (default: 25).
        The response is a binary PNG file and not a JSON object.
    """
    data = request.get_json()
    image_urls = data.get('images', [])

    if len(image_urls) != NUM_IMAGES:
        return jsonify({'error': f'Expected {NUM_IMAGES} images, got {len(image_urls)}'}), 400

    # try:
    images = load_images_from_urls(image_urls)
    # save_images(images)  # Optional: comment this out if not needed (used to "cache")
    image_vectors = flatten_images(images)
    coords = reduce_with_pca(image_vectors)
    coords = snap_images_x(coords)
    coords = snap_images_y(coords)
    image_path = plot_images_on_canvas(images, coords)

    return send_file(image_path, mimetype='image/png')

    # except Exception as e:
    #     print("Exception occurred:", repr(e))
    #     return jsonify({'error': str(e)}), 500



def run_collage_generation_test():
    """
    Simulates the same logic as the /generate_collage POST endpoint,
    using a hardcoded list of image URLs from a test curl request.
    """
    image_urls = [
        "https://i.scdn.co/image/ab67616d0000b273f54b99bf27cda88f4a7403ce",
        "https://i.scdn.co/image/ab67616d0000b2732a7db835b912dc5014bd37f4",
        "https://i.scdn.co/image/ab67616d0000b273c42fc1fcf52cd04498619c02",
        "https://i.scdn.co/image/ab67616d0000b2737b1b6f41c1645af9757d5616",
        "https://i.scdn.co/image/ab67616d0000b273cfc824b65a3b1755d98a7e23",
        "https://i.scdn.co/image/ab67616d0000b273447289301b37e205337ddd61",
        "https://i.scdn.co/image/ab67616d0000b273e634bd400f0ed0ed5a6f0164",
        "https://i.scdn.co/image/ab67616d0000b273cd945b4e3de57edd28481a3f",
        "https://i.scdn.co/image/ab67616d0000b273721d0ec76ac1c81adfd73c55",
        "https://i.scdn.co/image/ab67616d0000b27388883701231713b18429f80b",
        "https://i.scdn.co/image/ab67616d0000b2730fb08616c78d44ceb4c8d061",
        "https://i.scdn.co/image/ab67616d0000b273ca74198e1f4ef261bf418029",
        "https://i.scdn.co/image/ab67616d0000b27377d6678d66fd48ecfed2cfe8",
        "https://i.scdn.co/image/ab67616d0000b2730744690248ef3ba7b776ea7b",
        "https://i.scdn.co/image/ab67616d0000b273072e9faef2ef7b6db63834a3",
        "https://i.scdn.co/image/ab67616d0000b2733ca9954e7b2b7ef7fa8bbd78",
        "https://i.scdn.co/image/ab67616d0000b2736a463f436bbf07f3c9e8c62a",
        "https://i.scdn.co/image/ab67616d0000b273bf5cce5a0e1ed03a626bdd74",
        "https://i.scdn.co/image/ab67616d0000b2736cfd9a7353f98f5165ea6160",
        "https://i.scdn.co/image/ab67616d0000b27380dacac510e9d085a591f981",
        "https://i.scdn.co/image/ab67616d0000b2732090f4f6cc406e6d3c306733",
        "https://i.scdn.co/image/ab67616d0000b27333ccb60f9b2785ef691b2fbc",
        "https://i.scdn.co/image/ab67616d0000b2737c0c6c1cfac7464b6211587d",
        "https://i.scdn.co/image/ab67616d0000b273e31a279d267f3b3d8912e6f1",
        "https://i.scdn.co/image/ab67616d0000b27300b39b4a73d28536690b355c",
        "https://i.scdn.co/image/ab67616d0000b273ab738b25b86bf02f0346c53d",
        "https://i.scdn.co/image/ab67616d0000b273db974f9533dd9b362891b5db",
        "https://i.scdn.co/image/ab67616d0000b273881d8d8378cd01099babcd44",
        "https://i.scdn.co/image/ab67616d0000b273bba7cfaf7c59ff0898acba1f",
        "https://i.scdn.co/image/ab67616d0000b27369f63a842ea91ca7c522593a",
        "https://i.scdn.co/image/ab67616d0000b273bf3e522cd3fed64ae064095f",
        "https://i.scdn.co/image/ab67616d0000b2739416ed64daf84936d89e671c",
        "https://i.scdn.co/image/ab67616d0000b27386badd635b69aea887862214",
        "https://i.scdn.co/image/ab67616d0000b2732624442cf48e4962d1422da8",
        "https://i.scdn.co/image/ab67616d0000b273384d10f967c2b914de7e2713",
        "https://i.scdn.co/image/ab67616d0000b2733d98a0ae7c78a3a9babaf8af"
    ]

    print("Running local test of collage generation with test image list...")
    images = load_images_from_urls(image_urls)
    image_vectors = flatten_images(images)
    coords = reduce_with_pca(image_vectors)
    coords = snap_images_x(coords)
    coords = snap_images_y(coords)
    image_path = plot_images_on_canvas(images, coords)
    print("Collage generated and saved to:", image_path)



### Run Server ###

if __name__ == '__main__':
    app.run(debug=True)
    # run_collage_generation_test()
