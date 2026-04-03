from __future__ import annotations

from typing import List, Optional

import tensorflow as tf

from .config import CLASSES_PATH, MODEL_PATH


model: Optional[tf.keras.Model] = None
class_names: List[str] = []


def _read_class_names() -> List[str]:
    if not CLASSES_PATH.exists():
        print(f"Warning: classes file not found at {CLASSES_PATH}")
        return []

    with CLASSES_PATH.open("r", encoding="utf-8") as file_handle:
        content = file_handle.read().strip()

    if "\n" in content:
        return [line.strip() for line in content.split("\n") if line.strip()]

    return content.replace(",", " ").split()


def _normalize_class_count(expected_classes: int) -> None:
    global class_names

    if len(class_names) == expected_classes:
        return

    if len(class_names) > expected_classes:
        class_names = class_names[:expected_classes]
        return

    while len(class_names) < expected_classes:
        class_names.append(f"Class_{len(class_names)}")


def load_resources() -> None:
    global model, class_names

    print("--- Loading Resources ---")
    class_names = _read_class_names()
    print(f"Loaded {len(class_names)} class names")

    if not MODEL_PATH.exists():
        print(f"Critical: model not found at {MODEL_PATH}")
        model = None
        return

    try:
        model = tf.keras.models.load_model(str(MODEL_PATH))
        output_shape = model.output_shape[-1]
        _normalize_class_count(output_shape)
        print(f"Model loaded. Output classes: {output_shape}")
    except Exception as exc:
        model = None
        print(f"Error loading model: {exc}")