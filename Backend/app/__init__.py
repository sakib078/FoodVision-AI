from flask import Flask
from flask_cors import CORS

from .routes import api_blueprint
from .resources import load_resources


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(api_blueprint)
    load_resources()
    return app