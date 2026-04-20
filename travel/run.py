from flask import Flask
from flask_cors import CORS

from app.api.main import main_bp

App = Flask(__name__)

CORS(
    App,
    origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    supports_credentials=True,
)

App.register_blueprint(main_bp)


if __name__ == '__main__':
    App.run(debug=True, port=8080, use_reloader=False)



