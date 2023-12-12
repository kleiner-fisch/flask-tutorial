from line_schema import Line_Schema
from marshmallow import Schema, fields

class Game_Schema(Schema):

    p0 = fields.Int()
    p1 = fields.Int()
    game_id = fields.Int()
    current_player = fields.Int()

    lines = fields.List(fields.Nested(Line_Schema()))
    public_cards = fields.List(fields.Str())
    unresolved_scout = fields.Bool()
    claim = fields.Dict(keys=fields.Str(), values=fields.Int())

        # TODO Non urgent : for players hands we need to show the number of cards of each type. 
        #   Probably also for the decks

    