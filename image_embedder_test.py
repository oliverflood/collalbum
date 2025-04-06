from image_embedder import image_url_to_vector

image_url = "https://i.scdn.co/image/ab67616d0000b273bba7cfaf7c59ff0898acba1f"
embedding = image_url_to_vector(image_url)

print("Final Embedding Vector:", embedding)
