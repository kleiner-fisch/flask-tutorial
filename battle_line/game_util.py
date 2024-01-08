
import operator 
import json
from .line import Line
from .game import Game

def copy_ids(copy_from, copy_to):
    '''copies the game ID and the line IDs IDs from one game to another game.    '''
    copy_to.game_id = copy_from.game_id
    for index, line in enumerate(copy_from.lines):
        copy_to.lines[index].id = line.id

def weakly_equal(g1, g2):
    '''checks whether two games are equal, ignoring game IDs and line IDs''' 
    game_attr = operator.attrgetter("p1", "p2", "current_player", "claim", "unresolved_scout", "public_cards", "winner")

    #game_attr = operator.attrgetter("p1", "p2", "current_player", "hands", "claim", "unresolved_scout", "public_cards", "winner")
    lines1 = [(line.sides, line.won_by) for line in g1.lines]
    lines2 = [(line.sides, line.won_by) for line in g2.lines]
    result =  game_attr(g1) == game_attr(g2)
    return result and lines1 == lines2

def game_from_json(game):
    '''creates a game object from a json serialization of it.
    In the json serialization integer dictionary keys are stores as strings. 
    This method fixes that.
    does not modify the original input obhject'''
    game = json.loads(json.dumps(game))
    pid1, pid2 = game['p1'], game['p2']
    for line in game['lines']:
        line['sides'][pid1] = line['sides'].pop(str(pid1))
        line['sides'][pid2] = line['sides'].pop(str(pid2))
    game['lines']=[Line(line['sides'], line['won_by']) for line in game['lines']]
    # TODO currently always when we create a game we create hand for it. 
    #   Seems cleaner to only generate a hand upon explicit request
    return Game(**game)

