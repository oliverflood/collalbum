from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import uuid
import requests
from io import BytesIO
import os
from flask import send_file

GRID_SIZE = 5
NUM_IMAGES = GRID_SIZE * GRID_SIZE
SAVE_DIR = "collages"

app = Flask(__name__)

def load_images_from_urls(url_list):
    images = []
    for url in url_list:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
    return images

def flatten_images(images):
    return np.array([np.asarray(img.resize((32, 32))).flatten() for img in images])

def reduce_with_pca(data, n_components=2):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data)

def snap_images_x(coords, grid_size=GRID_SIZE):
    coords_copy = coords.copy()
    sorted_indices = np.argsort(coords_copy[:, 0])
    snapped = np.zeros_like(coords_copy)
    for i in range(coords_copy.shape[0]):
        bucket = i // grid_size
        snapped[sorted_indices[i], 0] = bucket
        snapped[sorted_indices[i], 1] = coords_copy[sorted_indices[i], 1]
    return snapped

def snap_images_y(coords, grid_size=GRID_SIZE):
    coords_copy = coords.copy()
    for bucket in range(grid_size):
        bucket_indices = np.where(coords_copy[:, 0] == bucket)[0]
        sorted_y = bucket_indices[np.argsort(-coords_copy[bucket_indices, 1])]
        for new_y, idx in enumerate(sorted_y):
            coords_copy[idx, 1] = grid_size - 1 - new_y
    return coords_copy

def plot_images_on_canvas(images, coords, save_dir=SAVE_DIR):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(coords[:, 0].min(), coords[:, 0].max())
    ax.set_ylim(coords[:, 1].min(), coords[:, 1].max())
    ax.axis('off')

    zoom = 1.1 / GRID_SIZE
    for (x, y), img in zip(coords, images):
        imagebox = OffsetImage(img.resize((640, 640)), zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    os.makedirs(save_dir, exist_ok=True)
    unique_id = uuid.uuid4().hex[:6]
    save_path = os.path.join(save_dir, f'collage_{unique_id}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)

    print(f"Saved collage to {save_path}")
    return save_path

@app.route('/generate_collage', methods=['POST'])
def generate_collage():
    data = request.get_json()
    image_urls = data.get('images', [])

    if len(image_urls) != NUM_IMAGES:
        return jsonify({"error": f"Expected {NUM_IMAGES} images, got {len(image_urls)}"}), 400

    try:
        images = load_images_from_urls(image_urls)
        image_vectors = flatten_images(images)
        coords = reduce_with_pca(image_vectors)
        coords = snap_images_x(coords)
        coords = snap_images_y(coords)
        image_path = plot_images_on_canvas(images, coords)
        # return jsonify({"image_path": image_path})
        return send_file(image_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
