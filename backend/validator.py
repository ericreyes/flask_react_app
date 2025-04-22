from marshmallow import Schema, fields, validate


class BaseStatsSchema(Schema):
  hp = fields.Int(required=True, validate=validate.Range(min=1))
  attack = fields.Int(required=True, validate=validate.Range(min=1))
  defense = fields.Int(required=True)
  speed = fields.Int(required=True))

  class PokemonSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    type =


