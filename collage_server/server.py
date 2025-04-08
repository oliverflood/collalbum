from flask import Flask, request, jsonify, send_file
from .collage_from_embeddings import generate_collage_from_image_urls
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)

def load_images_from_urls(url_list):
    images = []
    for url in url_list:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        images.append(img)
    return images

@app.route('/generate_collage', methods=['POST'])
def generate_collage():
    data = request.get_json()
    image_urls = data.get('images', [])

    if not image_urls or len(image_urls) < 4:
        return jsonify({"error": "Please provide at least 4 image URLs"}), 400

    try:
        collage_path = generate_collage_from_image_urls(image_urls, load_images_from_urls)
        return send_file("C:\\Users\\Jack Kammerer\\Desktop\\collalbum\\" + collage_path, mimetype="image/jpeg")

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
