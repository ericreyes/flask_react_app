from marshmallow import Schema, fields, validate

POKEMON_TYPES = [
    "Bug",
    "Dragon",
    "Electric",
    "Fighting",
    "Fire",
    "Flying",
    "Ghost",
    "Grass",
    "Ground",
    "Ice",
    "Normal",
    "Poison",
    "Psychic",
    "Rock",
    "Water",
]

class BaseStatsSchema(Schema):
    hp = fields.Int(required=True, validate=validate.Range(min=1))
    attack = fields.Int(required=True, validate=validate.Range(min=1))
    defense = fields.Int(required=True)
    speed = fields.Int(required=True)


class PokemonSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    type = fields.List(
        fields.Str(validate=validate.OneOf(POKEMON_TYPES)),
        required=True,
        validate=validate.Length(min=1, max=2),
    )
    base_stats = fields.Nested(BaseStatsSchema, required=True)

    description = fields.Str(required=False, validate=validate.Length(min=1))
    pokedex_number = fields.Int(required=True, validate=validate.Range(min=1))

class PaginationSchema(Schema):
    limit = fields.Int(required=False, validate=validate.Range(min=1, max=100))
    offset = fields.Int(required=False, validate=validate.Range(min=1, max=1000))
    sort = fields.Str(required=False, validate=validate.OneOf(["asc", "desc"]))
    sort_by = fields.Str(required=False, validate=validate.OneOf(["name", "pokedex_number"]))

# class PokemonFilterSchema(Schema):

pagination_schema = PaginationSchema()
pokemon_schema = PokemonSchema()
