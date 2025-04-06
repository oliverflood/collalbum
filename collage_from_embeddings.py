import os
import uuid
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from io import BytesIO
from collage_utils import snap_images_x, snap_images_y, center_crop_fraction, add_position_dependent_jitter
from image_embedder import image_urls_to_vectors


SAVE_DIR = "collages"
CANVAS_IMAGE_SIZE = (640, 640)

def reduce_with_pca(data, n_components=2):
    pca = PCA(n_components=n_components)
    return pca.fit_transform(data)

def plot_images_on_canvas(images, coords, grid_size, crop_fraction=0.9, zorder_imgs=False):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(coords[:, 0].min(), coords[:, 0].max())
    ax.set_ylim(coords[:, 1].min(), coords[:, 1].max())
    ax.axis('off')

    if zorder_imgs:
        # Calculate Manhattan distance from center
        center = coords.mean(axis=0)
        manhattan_distances = np.sum(np.abs(coords - center), axis=1)
        zorders = -manhattan_distances  # higher zorder = plotted on top
    else:
        zorders = zorders = np.zeros(len(images))

    base_zoom = 1.1 / grid_size
    for i, ((x, y), img, z) in enumerate(zip(coords, images, zorders)):
        size_factor = 1.82 - 1 * (i / (grid_size * grid_size))
        imagebox = OffsetImage(img.resize(CANVAS_IMAGE_SIZE), zoom=base_zoom * size_factor)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=z)
        ax.add_artist(ab)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0.0, transparent=True)
    plt.close(fig)
    buf.seek(0)
    collage_img = Image.open(buf).convert("RGB")

    if crop_fraction < 1.0:
        collage_img = center_crop_fraction(collage_img, crop_fraction)

    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, f"collage_{uuid.uuid4().hex[:6]}.jpg")
    collage_img.save(path, format="JPEG", quality=85)
    return path


def generate_collage_from_embeddings(embeddings: np.ndarray, images: list[Image.Image]) -> str:
    if len(embeddings) != len(images):
        raise ValueError("Embeddings and images must have the same length.")

    grid_size = int(np.floor(np.sqrt(len(images))))
    if grid_size * grid_size != len(images):
        images = images[:grid_size * grid_size]
        embeddings = embeddings[:grid_size * grid_size]

    coords = reduce_with_pca(embeddings)
    coords = snap_images_x(coords, grid_size)
    coords = snap_images_y(coords, grid_size)
    coords = add_position_dependent_jitter(coords, jitter_strength=0.25)
    coords = coords[:, [1, 0]]  # flip x/y for visual aesthetics

    return plot_images_on_canvas(images, coords, grid_size, crop_fraction=0.85)

def generate_collage_from_image_urls(image_urls: list[str], image_loader) -> str:
    # Trim to closest square number of images
    grid_size = int(np.floor(np.sqrt(len(image_urls))))
    num_images = grid_size * grid_size
    image_urls = image_urls[:num_images]

    print(f"Using grid size {grid_size}x{grid_size} ({num_images} images)")
    print("Fetching images")
    images = image_loader(image_urls)

    print("Computing semantic + visual embeddings (batched)")
    embeddings = image_urls_to_vectors(image_urls)

    return generate_collage_from_embeddings(embeddings, images)