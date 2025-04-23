from flask import Flask
from flask_cors import CORS
from routes import register_pokemon_routes

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app)


app.config["DEBUG"] = True

register_pokemon_routes(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
