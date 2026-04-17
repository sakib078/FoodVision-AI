import base64

from flask import Blueprint, jsonify, request

from .prediction_service import predict_food
from . import resources


api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/", methods=["GET"])
def home():
    return (
        jsonify(
            {
                "status": "success",
                "message": "FoodVision API is running! Send image files via POST to the /predict endpoint.",
            }
        ),
        200,
    )


@api_blueprint.route("/health", methods=["GET"])
def health():
    """Health check endpoint for load balancers and orchestration platforms."""
    if resources.model is None:
        return jsonify({"status": "unhealthy", "reason": "Model not loaded"}), 503
    
    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "classes_count": len(resources.class_names)
    }), 200


def _extract_image_bytes():
    if "file" in request.files:
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return None, (jsonify({"error": "No selected file"}), 400)
        return uploaded_file.read(), None

    if request.is_json:
        payload = request.get_json(silent=True) or {}
        encoded_image = payload.get("image_base64") or payload.get("file_base64") or payload.get("image")
        if not encoded_image:
            return None, (jsonify({"error": "Missing image_base64 in JSON payload"}), 400)

        if isinstance(encoded_image, str) and encoded_image.startswith("data:") and "," in encoded_image:
            encoded_image = encoded_image.split(",", 1)[1]

        try:
            return base64.b64decode(encoded_image, validate=True), None
        except Exception:
            return None, (jsonify({"error": "Invalid base64 image payload"}), 400)

    return None, (jsonify({"error": "No file uploaded and no JSON image payload provided"}), 400)


@api_blueprint.route("/predict", methods=["POST"])
@api_blueprint.route("/infer", methods=["POST"])
def predict():
    image_bytes, error_response = _extract_image_bytes()
    if error_response is not None:
        return error_response

    try:
        result = predict_food(image_bytes)
        return jsonify(result), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(f"Prediction error: {exc}")
        return jsonify({"error": "Prediction failed"}), 500