import os
from groq import Groq
from dotenv import load_dotenv
from google.cloud import aiplatform

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def describe_image(image_url):
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this album cover in a sentence."},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=0.7,
        max_completion_tokens=256,
    )

    return response.choices[0].message.content

image_url = "https://i.scdn.co/image/ab67616d0000b273bba7cfaf7c59ff0898acba1f"
description = describe_image(image_url)
print(description)