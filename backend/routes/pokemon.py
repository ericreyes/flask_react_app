from flask import jsonify, send_from_directory, request, Blueprint
from marshmallow import ValidationError
from flask.views import MethodView
import os


from bson.regex import Regex
from schemas.pokemon import pagination_schema, pokemon_schema
from db import db

pokemon_api = Blueprint("pokemon_api", __name__)


# In production, static files will be served from the React build folder
REACT_BUILD_FOLDER = os.path.abspath("../../frontend/build")


class PokemonListAPI(MethodView):
    def get(self):
        """GET /api/pokemon - List Pokémon with pagination"""
        try:
            args = pagination_schema.load(request.args)
        except ValidationError as e:
            return (
                jsonify(
                    {"message": "ValidationError", "status": "error", "error": str(e)}
                ),
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

    def post(self):
        """POST /api/pokemon - create new pokemon"""
        try:
            data = request.get_json()
            validated_data = pokemon_schema.load(data)

        except ValidationError as e:
            return (
                jsonify(
                    {
                        "message": "ValidationError",
                        "status": "error",
                        "error": str(e) + "Invalid pokemon data format",
                    }
                ),
                400,  # bad request status code
            )

        existing_pokemon = db.pokemon.find_one({"name": validated_data["name"]})
        if existing_pokemon:
            return (
                jsonify(
                    {
                        "message": "PokemonAlreadyExists",
                        "status": "error",
                        "error": "Pokemon with this name already exists",
                    }
                ),
                409,  # conflict status code
            )

        validated_data["pokedex_number"] = db.pokemon.count_documents({}) + 1
        validated_data["_id"] = validated_data["pokedex_number"]
        db.pokemon.insert_one(validated_data)
        return (
            jsonify(
                {
                    "message": "Pokemon created",
                    "status": "success",
                    "data": validated_data,
                }
            )
        )


class PokemonDetailAPI(MethodView):
    def get(self, id):
        """GET /api/pokemon/<id> - Get Pokemon by ID"""
        pass

    def put(self, id):
        """PUT /api/pokemon/<id> - Update Pokemon by ID"""
        pass

    def delete(self, id):
        """DELETE /api/pokemon/<id> - Delete Pokemon by ID"""
        pass


class PokemonSearchAPI(MethodView):
    """GET /api/pokemon/search?q= - Search pokemon by type or name"""

    pass


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

@pokemon_api.errorhandler(403)
def not_found():
    return (
        jsonify(
            {
                "message": "NotAuthorized",
                "status": "error",
                "error": "User is not authorized",
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


pokemon_list_view = PokemonListAPI.as_view("pokemon_list_api")
pokemon_api.add_url_rule(
    "pokemon", view_func=pokemon_list_view, methods=["GET", "POST"]
)


# Method | Route | Description
# GET | /api/pokemon | List all Pokémon (paginated)
# GET | /api/pokemon/<id> | Get one Pokémon
# POST | /api/pokemon | Create new Pokémon
# PUT | /api/pokemon/<id> | Update Pokémon
# DELETE | /api/pokemon/<id> | Delete Pokémon
# GET | /api/pokemon/search?q= | Search by name/type
