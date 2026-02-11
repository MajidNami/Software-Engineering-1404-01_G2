from PIL import Image
from utils.image import get_minio_client



class NSFWDetector:
    def __init__(self, classifier):
        self.classifier = classifier

    def detect(self, image_path):
        output = {}
        img = get_minio_client(image_path)
        results = self.classifier(img)
        for result in results:
            output[result['label']] = result['score']
        return output