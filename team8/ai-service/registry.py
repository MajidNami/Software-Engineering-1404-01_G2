import torch
from transformers import pipeline
from image_tagging.model import ImageTagger
from comment.model import CommentClassifier
from summarizer.model import CommentSummarizer
from nsfw.model import NSFWDetector


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEFAULT_IMAGE_TAGGER_WEIGHTS = "image_tagging/convnext_weights.pth"
NSFW_MODEL = "Falconsai/nsfw_image_detection"
COMMENT_MODEL = "openai/gpt-oss-120b"


def get_image_tagger(weights_path=DEFAULT_IMAGE_TAGGER_WEIGHTS, device=DEVICE):
    return ImageTagger(weights_path=weights_path, device=device)

def get_comment_classifier():
    return CommentClassifier(model=COMMENT_MODEL)

def get_comment_summarizer():
    return CommentSummarizer()

def get_nsfw_detector():
    nsfw_pipe = pipeline("image-classification", model=NSFW_MODEL)
    return NSFWDetector(nsfw_pipe)

MODEL_REGISTRY = {
    "image_tagger": get_image_tagger,
    "comment_classifier": get_comment_classifier,
    "comment_summarizer": get_comment_summarizer,
    "nsfw_detector": get_nsfw_detector,
}

_MODEL_CACHE = {}

def get_model(name, **kwargs):
    if name not in _MODEL_CACHE:
        _MODEL_CACHE[name] = MODEL_REGISTRY[name](**kwargs)
    return _MODEL_CACHE[name]
