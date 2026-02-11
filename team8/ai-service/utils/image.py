import io
from urllib import request
from PIL import Image
from torchvision import transforms
import os
from dotenv import load_dotenv
from minio import Minio

TARGET_SIZE = 384
load_dotenv()

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("S3_SECRET_KEY")
MINIO_BUCKET = os.getenv("S3_BUCKET_NAME")

val_transform = transforms.Compose([
    transforms.Resize((TARGET_SIZE, TARGET_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])

def get_minio_client(file_path):       
    response = minio_client.get_object(
            MINIO_BUCKET,
            file_path
    )

    image_bytes = response.read()
    response.close()
    response.release_conn()

    return Image.open(io.BytesIO(image_bytes)).convert("RGB")



def resize_and_center_crop(img, size = 384):
    w, h = img.size
    scale = size / min(w, h)
    new_w, new_h = int(w * scale), int(h * scale)

    img = img.resize((new_w, new_h), Image.BILINEAR)

    left = (new_w - size) // 2
    top = (new_h - size) // 2
    right = left + size
    bottom = top + size

    return img.crop((left, top, right, bottom))


def load_and_preprocess_image(path ,device):
    image = get_minio_client(path)
    img = resize_and_center_crop(image, 384)
    tensor = val_transform(img).unsqueeze(0).to(device)
    return tensor




