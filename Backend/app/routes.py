from flask import Blueprint, jsonify, request

from .prediction_service import predict_food


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


@api_blueprint.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        result = predict_food(uploaded_file.read())
        return jsonify(result), 200
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 500
    except Exception as exc:
        print(f"Prediction error: {exc}")
        return jsonify({"error": "Prediction failed"}), 500