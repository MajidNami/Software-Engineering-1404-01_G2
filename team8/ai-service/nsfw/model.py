from PIL import Image

class NSFWDetector:
    def __init__(self, classifier):
        self.classifier = classifier

    def detect(self, image_path):
        output = {}
        img = Image.open(image_path).convert("RGB")
        results = self.classifier(img)
        for result in results:
            output[result['label']] = result['score']
        return output