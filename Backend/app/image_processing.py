import io

import numpy as np
import tensorflow as tf
from PIL import Image

from .config import IMAGE_SIZE


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode != "RGB":
        image = image.convert("RGB")

    image = image.resize(IMAGE_SIZE)
    image_array = tf.keras.preprocessing.image.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)
    return tf.keras.applications.mobilenet_v2.preprocess_input(image_array)