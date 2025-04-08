import numpy as np

def snap_images_x(coords, grid_size):
    coords_copy = coords.copy()
    sorted_indices = np.argsort(coords_copy[:, 0])
    snapped = np.zeros_like(coords_copy)

    for i in range(coords_copy.shape[0]):
        bucket = i // grid_size
        snapped[sorted_indices[i], 0] = bucket
        snapped[sorted_indices[i], 1] = coords_copy[sorted_indices[i], 1]

    return snapped

def snap_images_y(coords, grid_size):
    coords_copy = coords.copy()
    for bucket in range(grid_size):
        bucket_indices = np.where(coords_copy[:, 0] == bucket)[0]
        sorted_y = bucket_indices[np.argsort(-coords_copy[bucket_indices, 1])]
        for new_y, idx in enumerate(sorted_y):
            coords_copy[idx, 1] = grid_size - 1 - new_y
    return coords_copy

def center_crop_fraction(img, fraction=0.8):
    width, height = img.size
    new_width = int(width * fraction)
    new_height = int(height * fraction)
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    return img.crop((left, top, left + new_width, top + new_height))

def add_position_dependent_jitter(coords, jitter_strength=0.4):
    coords = coords.copy()
    center = coords.mean(axis=0)
    max_dist = np.linalg.norm(coords - center, axis=1).max()
    for i, (x, y) in enumerate(coords):
        dist_to_center = np.linalg.norm([x - center[0], y - center[1]])
        scale = 1 - (dist_to_center / max_dist)
        jitter = np.random.uniform(-jitter_strength, jitter_strength, 2) * scale
        coords[i] += jitter
    return coords
