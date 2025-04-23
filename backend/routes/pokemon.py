from flask import jsonify, send_from_directory, request, Blueprint
from marshmallow import ValidationError
import os



from bson.regex import Regex
from schemas.pokemon import pagination_schema, pokemon_schema
from db import db

pokemon_api = Blueprint("pokemon_api", __name__)


# In production, static files will be served from the React build folder
REACT_BUILD_FOLDER = os.path.abspath("../../frontend/build")


@pokemon_api.route("pokemon", methods=["GET"])
def get_all_pokemon():
    """Get all pokemon with schema validation"""
    try:
        args = pagination_schema.load(request.args)
    except ValidationError as e:
        return (
            jsonify({"message": "ValidationError", "status": "error", "error": str(e)}),
            400,
        )

    limit = int(args.get("limit", 10))
    offset = int(args.get("offset", 0))
    cursor = db.pokemon.find({}, {"_id": 0}).skip(offset).limit(limit)
    pokemon_data = list(cursor)
    return (
        jsonify(
            {
                "message": "PokemonList retrieved and validated with many",
                "status": "success",
                "data": pokemon_schema.load(data=pokemon_data, many=True),
                "meta": {
                    "offset": offset,
                    "limit": limit,
                    "total_count": db.pokemon.count_documents({}),
                },
            }
        ),
        200,
    )


# Route to serve React app - for production use
@pokemon_api.route("/", defaults={"path": ""})
@pokemon_api.route("/<path:path>")
def serve_react(path):
    """Serve React app in production"""
    if path != "" and os.path.exists(os.path.join(REACT_BUILD_FOLDER, path)):
        return send_from_directory(REACT_BUILD_FOLDER, path)
    else:
        return send_from_directory(REACT_BUILD_FOLDER, "index.html")


# Error handlers
@pokemon_api.errorhandler(404)
def not_found(e):
    return (
        jsonify(
            {
                "message": "PokemonNotFound",
                "status": "error",
                "error": "Pokemon not found",
            }
        ),
        404,
    )


@pokemon_api.errorhandler(500)
def server_error(e):
    return (
        jsonify(
            {"message": "Internal server error", "status": "error", "error": str(e)}
        ),
        500,
    )



# Method | Route | Description
# GET | /api/pokemon | List all Pokémon (paginated)
# GET | /api/pokemon/<id> | Get one Pokémon
# POST | /api/pokemon | Create new Pokémon
# PUT | /api/pokemon/<id> | Update Pokémon
# DELETE | /api/pokemon/<id> | Delete Pokémon
# GET | /api/pokemon/search?q= | Search by name/type
