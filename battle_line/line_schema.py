
from marshmallow import Schema, fields

class Line_Schema(Schema):

    sides = fields.Dict(keys=fields.Int(), values=fields.List(fields.Str()))
    won_by = fields.Int()
