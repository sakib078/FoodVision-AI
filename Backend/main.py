from app import create_app
from app.config import DEFAULT_HOST, DEFAULT_PORT


app = create_app()

if __name__ == '__main__':
    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, debug=False)
