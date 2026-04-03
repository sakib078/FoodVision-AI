from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from .calorie_database import CALORIE_DATABASE
from .image_processing import preprocess_image
from . import resources


def _build_fallback_portions() -> List[Dict[str, Any]]:
    return [
        {"size": "small", "grams": 100, "description": "Small serving", "calories": 150},
        {"size": "medium", "grams": 200, "description": "Regular serving", "calories": 300},
        {"size": "large", "grams": 300, "description": "Large serving", "calories": 450},
    ]


def _build_portion_options(food_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    options: List[Dict[str, Any]] = []
    for size, info in food_data["portions"].items():
        calories = int((food_data["per_100g"] / 100) * info["grams"])
        options.append(
            {
                "size": size,
                "grams": info["grams"],
                "description": info["description"],
                "calories": calories,
            }
        )
    return options


def _calorie_payload(predicted_label: str) -> Dict[str, Any]:
    lookup_key = predicted_label.lower().replace(" ", "_")
    food_data = CALORIE_DATABASE.get(lookup_key)

    if not food_data:
        return {
            "calories": 300,
            "portion_options": _build_fallback_portions(),
        }

    portions = _build_portion_options(food_data)
    default_portion = food_data["portions"].get("medium", next(iter(food_data["portions"].values())))
    default_calories = int((food_data["per_100g"] / 100) * default_portion["grams"])
    return {
        "calories": default_calories,
        "portion_options": portions,
    }


def predict_food(image_bytes: bytes) -> Dict[str, Any]:
    if resources.model is None:
        raise RuntimeError("Model not loaded")

    processed_image = preprocess_image(image_bytes)
    predictions = resources.model.predict(processed_image)

    predicted_idx = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][predicted_idx])

    predicted_label = (
        resources.class_names[predicted_idx]
        if predicted_idx < len(resources.class_names)
        else f"Class {predicted_idx}"
    )
    calorie_info = _calorie_payload(predicted_label)

    return {
        "label": predicted_label,
        "confidence": confidence,
        "calories": calorie_info["calories"],
        "portion_options": calorie_info["portion_options"],
        "class_id": predicted_idx,
    }