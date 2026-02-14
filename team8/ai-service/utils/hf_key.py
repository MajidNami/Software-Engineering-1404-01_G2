import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")

load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("HF_API_KEY")

CLIENT = InferenceClient(api_key=API_KEY)