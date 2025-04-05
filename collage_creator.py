import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import uuid


GRID_SIZE = 10
NUM_IMAGES = GRID_SIZE * GRID_SIZE

def load_and_flatten_images(folder, size=(64, 64), max_images=NUM_IMAGES):
    image_paths = [os.path.join(folder, f) for f in os.listdir(folder)
                   if f.lower().endswith(('.jpg', '.png'))][:max_images]
    images = []
    vectors = []

    for path in image_paths:
        img = Image.open(path).convert('RGB').resize(size)
        images.append(img)
        vectors.append(np.asarray(img).flatten())

    return images, np.array(vectors)

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

def plot_images_on_canvas(images, coords, zoom=0.6, save_dir="collages"):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(coords[:, 0].min() - 1, coords[:, 0].max() + 1)
    ax.set_ylim(coords[:, 1].min() - 1, coords[:, 1].max() + 1)
    ax.axis('off')

    for (x, y), img in zip(coords, images):
        imagebox = OffsetImage(img.resize((128, 128)), zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False)
        ax.add_artist(ab)

    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        unique_id = uuid.uuid4().hex[:6]  # short 6-char ID
        save_path = os.path.join(save_dir, f"collage_{unique_id}.png")
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f'Saved collage to {save_path}')

folder_path = "STL10_sample_images"
images, image_vectors = load_and_flatten_images(folder_path)
coords = reduce_with_pca(image_vectors)
plot_images_on_canvas(images, coords, save_dir=None)

snapped_coords = snap_images_x(coords)
plot_images_on_canvas(images, snapped_coords, save_dir=None)

snapped_coords = snap_images_y(snapped_coords)
plot_images_on_canvas(images, snapped_coords)

plt.show()