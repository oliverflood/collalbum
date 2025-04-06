from collage_from_embeddings import generate_collage_from_image_urls
from server import load_images_from_urls
from PIL import Image
import numpy as np

def run_collage_generation_test():
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
        # "https://i.scdn.co/image/ab67616d0000b273ca74198e1f4ef261bf418029",
        # "https://i.scdn.co/image/ab67616d0000b27377d6678d66fd48ecfed2cfe8",
        # "https://i.scdn.co/image/ab67616d0000b2730744690248ef3ba7b776ea7b",
        # "https://i.scdn.co/image/ab67616d0000b273072e9faef2ef7b6db63834a3",
        # "https://i.scdn.co/image/ab67616d0000b2733ca9954e7b2b7ef7fa8bbd78",
        # "https://i.scdn.co/image/ab67616d0000b2736a463f436bbf07f3c9e8c62a",
        # "https://i.scdn.co/image/ab67616d0000b273bf5cce5a0e1ed03a626bdd74",
        # "https://i.scdn.co/image/ab67616d0000b2736cfd9a7353f98f5165ea6160",
        # "https://i.scdn.co/image/ab67616d0000b27380dacac510e9d085a591f981",
        # "https://i.scdn.co/image/ab67616d0000b2732090f4f6cc406e6d3c306733",
        # "https://i.scdn.co/image/ab67616d0000b27333ccb60f9b2785ef691b2fbc",
        # "https://i.scdn.co/image/ab67616d0000b2737c0c6c1cfac7464b6211587d",
        # "https://i.scdn.co/image/ab67616d0000b273e31a279d267f3b3d8912e6f1",
        # "https://i.scdn.co/image/ab67616d0000b27300b39b4a73d28536690b355c",
        # "https://i.scdn.co/image/ab67616d0000b273ab738b25b86bf02f0346c53d",
        # "https://i.scdn.co/image/ab67616d0000b273db974f9533dd9b362891b5db",
        # "https://i.scdn.co/image/ab67616d0000b273881d8d8378cd01099babcd44",
        # "https://i.scdn.co/image/ab67616d0000b273bba7cfaf7c59ff0898acba1f",
        # "https://i.scdn.co/image/ab67616d0000b27369f63a842ea91ca7c522593a",
        # "https://i.scdn.co/image/ab67616d0000b273bf3e522cd3fed64ae064095f",
        # "https://i.scdn.co/image/ab67616d0000b2739416ed64daf84936d89e671c",
        # "https://i.scdn.co/image/ab67616d0000b27386badd635b69aea887862214",
        # "https://i.scdn.co/image/ab67616d0000b2732624442cf48e4962d1422da8",
        # "https://i.scdn.co/image/ab67616d0000b273384d10f967c2b914de7e2713",
        # "https://i.scdn.co/image/ab67616d0000b2733d98a0ae7c78a3a9babaf8af"
    ]

    print("Running collage test...")
    collage_path = generate_collage_from_image_urls(image_urls, load_images_from_urls)
    print("Collage generated at:", collage_path)
    

if __name__ == '__main__':
    run_collage_generation_test()
