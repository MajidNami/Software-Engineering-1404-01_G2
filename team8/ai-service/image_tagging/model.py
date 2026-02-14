import torch
import torch.nn as nn
from torchvision.models import convnext_base
from utils.image import load_and_preprocess_image
from utils.labels import image_classifier_locations as IMAGE_LABELS


class ImageTagger:
    def __init__(self, weights_path = "convnext_iranian_landmarksTop136.pth", device="cpu"):
        self.device = device
        self.num_classes = len(IMAGE_LABELS)

        model = convnext_base(weights=None)
        model.classifier[2] = nn.Linear(
            model.classifier[2].in_features,
            self.num_classes,
        )

        if torch.cuda.is_available():
            model.load_state_dict(torch.load(weights_path))
        else:
            model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
        model.eval()
        self.model = model.to(device)

    @torch.no_grad()
    def predict(self, image_path):
        x = load_and_preprocess_image(image_path, self.device)
        logits = self.model(x)

        probs = torch.softmax(logits, dim=1)
        idx = torch.argmax(probs, dim=1).item()

        return {
            "label": IMAGE_LABELS[idx],
            "confidence": probs[0, idx].item(),
        }
