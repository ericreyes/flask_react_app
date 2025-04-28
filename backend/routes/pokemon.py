from flask import send_from_directory, request, Blueprint
from marshmallow import ValidationError
from flask.views import MethodView
from utils.response import success_response, error_response
import os


from bson.regex import Regex
from schemas.pokemon import pagination_schema, pokemon_schema, pokemon_search_schema
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
            return error_response(
                error=str(e), message="Invalid pagination format", status_code=400
            )

        limit = int(args.get("limit", 10))
        offset = int(args.get("offset", 0))
        cursor = db.pokemon.find({}, {"_id": 0}).skip(offset).limit(limit)
        pokemon_data = list(cursor)
        data = pokemon_schema.load(data=pokemon_data, many=True)

        return success_response(
            data=data,
            message="PokemonList retrieved",
            meta={
                "offset": offset,
                "limit": limit,
                "total_count": db.pokemon.count_documents({}),
            },
        )

    def post(self):
        """POST /api/pokemon - create new pokemon"""
        try:
            data = request.get_json()
            validated_data = pokemon_schema.load(data)

        except ValidationError as e:
            return error_response(
                message="Invalid pokemon format", error=str(e), status_code=400
            )
        # Revisit this logic LBYL and EAFP
        # Check if the pokemon already exists

        validated_data["pokedex_number"] = db.pokemon.count_documents({}) + 1
        validated_data["_id"] = validated_data["pokedex_number"]
        db.pokemon.insert_one(validated_data)
        return success_response(
            data=validated_data,
            message="Pokemon created",
            meta={
                "total_count": db.pokemon.count_documents({}),
            },
        )


class PokemonDetailAPI(MethodView):
    def get(self, pokedex_number):
        """GET /api/pokemon/<pokedex_number> - Get Pokemon by pokedex_number"""
        try:
            pokedex_number = int(pokedex_number)
        except ValueError:
            return error_response(
                message="InvalidPokemonId", error="Invalid Pokemon ID", status_code=400
            )
        pokemon = db.pokemon.find({"pokedex_number": pokedex_number}, {"_id": 0})
        return success_response(data=pokemon, message="Pokemon retrieved")

    def put(self, pokedex_number):
        """PUT /api/pokemon/<pokedex_number> - Update Pokemon by pokedex_number"""
        try:
            data = request.get_json()
            validated_data = pokemon_schema.load(data)
            db.pokemon.replace_one({"pokedex_number": pokedex_number}, validated_data)
            return success_response(
                data=validated_data,
                message="Pokemon replaced",
                meta={
                    "total_count": db.pokemon.count_documents({}),
                },
            )
        except ValidationError as e:
            return error_response(
                message="Invalid pokemon format", error=str(e), status_code=400
            )

    def patch(self, pokedex_number):
        """PATCH /api/pokemon/<id> - Patch  Pokemon by pokedex_number"""
        try:
            data = request.get_json()
            validated_data = pokemon_schema.load(data, partial=True)
            db.pokemon.update_one(
                {"pokedex_number": pokedex_number}, {"$set": validated_data}
            )
            return success_response(
                data=validated_data,
                message="Pokemon updated",
                meta={
                    "total_count": db.pokemon.count_documents({}),
                },
            )
        except ValidationError as e:
            return error_response(
                message="Invalid pokemon format", error=str(e), status_code=400
            )

    def delete(self, pokedex_number):
        """DELETE /api/pokemon/<pokedex_number> - Delete Pokemon by pokedex_number"""
        try:
            pokedex_number = int(pokedex_number)
        except ValueError:
            return error_response(
                message="InvalidPokemonId", error="Invalid Pokemon ID", status_code=400
            )
        db.pokemon.delete_one({"pokedex_number": pokedex_number})
        return success_response(
            data={},
            message="Pokemon deleted",
            meta={
                "total_count": db.pokemon.count_documents({}),
            },
        )


class PokemonSearchAPI(MethodView):
    def post(self):
        """POST /api/pokemon/ - Search pokemon by type or name"""
        body = request.get_json() or {}
        try:
            validated_data = pokemon_search_schema.load(body, partial=True)
            args = pagination_schema.load(request.args, partial=True)
        except ValidationError as e:
            return error_response(
                message="Invalid pokemon format", error=str(e), status_code=400
            )

        query = {}
        limit = args.get("limit", 10)

        if "type" in validated_data:
            query["type"] = validated_data["type"]

        if "name" in validated_data:
            query["name"] = validated_data["name"]

        pokemon_results = db.pokemon.find(query, {"_id": 0}).limit(limit)

        return success_response(
            data=list(pokemon_results),
            message="Pokemon search retrieved",
            meta={
                "limit": limit,
                "total_count": db.pokemon.count_documents({}),
            },
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
    """Handle server errors"""
    return error_response(
        message="PokemonNotFound", error="Pokemon not found" + str(e), status_code=404
    )


@pokemon_api.errorhandler(403)
def not_authorized():
    """Handle server errors"""
    return error_response(
        message="NotAuthorized", error="User is not authorized", status_code=404
    )


@pokemon_api.errorhandler(500)
def server_error(e):
    """Handle server errors"""
    return error_response(
        message="Internal server error", error="Server error" + str(e), status_code=500
    )


pokemon_list_view = PokemonListAPI.as_view("pokemon_list_view")
pokemon_search_view = PokemonSearchAPI.as_view("pokemon_search_view")
pokemon_detail_api = PokemonDetailAPI.as_view("pokemon_detail_api")

pokemon_api.add_url_rule(
    "pokemon", view_func=pokemon_list_view, methods=["GET", "POST"]
)
pokemon_api.add_url_rule(
    "pokemon/search", view_func=pokemon_search_view, methods=["POST"]
)
pokemon_api.add_url_rule(
    "pokemon/<int:pokedex_number>",
    view_func=pokemon_detail_api,
    methods=["GET", "PUT", "PATCH", "DELETE"],
)
