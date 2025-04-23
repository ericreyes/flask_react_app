from routes.pokemon import pokemon_api

def register_pokemon_routes(app):
    """Register all routes with the Flask app."""
    app.register_blueprint(pokemon_api, url_prefix="/api")
