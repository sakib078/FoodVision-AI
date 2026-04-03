from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "model.h5"
CLASSES_PATH = BASE_DIR / "classes.txt"

IMAGE_SIZE = (224, 224)
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000