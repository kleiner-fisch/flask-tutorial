
from marshmallow import Schema, fields

class Game_Schema(Schema):

    class Meta :
        fields = ('p0', 'p1', 'id', 'game_id', 'lines',  'public_cards')
        # non-public data: hands, numbers_deck, tactics_deck
    p0 = fields.Integer()
    p1 = fields.Integer()
    id = fields.Integer()
    hands = fields.Dict()
    