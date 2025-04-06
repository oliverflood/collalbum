import os
from torchvision.datasets import STL10
import torch

output_folder = "STL10_sample_images"
n_images = 100

os.makedirs(output_folder, exist_ok=True)

dataset = STL10(root='./data', split='train', download=True)

for i in range(n_images):
    img, label = dataset[i]
    img.save(os.path.join(output_folder, f"img_{i:03d}.png"))

print(f"Saved {n_images} images to {output_folder}")
