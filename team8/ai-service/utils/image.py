from PIL import Image
from torchvision import transforms
import os
TARGET_SIZE = 384

val_transform = transforms.Compose([
    transforms.Resize((TARGET_SIZE, TARGET_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


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
def load_and_preprocess_image(path, device):

    try:
        with Image.open(path) as img:
            img = img.convert("RGB")
            img = resize_and_center_crop(img, 384)
            img.save(path, quality=95, subsampling=0)

    except Exception as e:
        print(f"❌ Skipped corrupted image: {path}")
    img = Image.open(path).convert("RGB")
    tensor = val_transform(img).unsqueeze(0).to(device)
    return tensor




