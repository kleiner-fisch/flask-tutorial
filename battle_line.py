from flask import Flask, jsonify, request, make_response
from game_schema import Game_Schema
from game_controller import Game_Controller

import pdb

app = Flask(__name__)

id2ctrl = dict()
player0 = 0
player1 = 1



def get_ctrl(game_id):
    return id2ctrl[game_id]


# TODO currently the plan is to use uuid for ids. This may be unpractibable as URIs may be terribly long if we chain such ids...
#   - uuid as ids would require to use uuid as type in the path, i.e. use <uuid:game_id>


# TODO game creation
# TODO winning of game

@app.patch('/<int:game_id>/card/<int:player_id>/<int:line_id>/<string:card_name>')
def play_card(game_id, player_id, line_id, card_name):
    ctrl = get_ctrl(game_id)
    try:
        content = request.json
        other_card = content.get('affected_card', None)
        ctrl.play_card(player_id, line_id, card_name, other_card)
        return ''
    except ValueError as e:
        return e.args[0], 422 
    

@app.patch('/<int:game_id>/<int:player_id>/<int:line_id>')
def manage_claim(game_id, player_id, line_id):
    ctrl = get_ctrl(game_id)
    try:
        content = request.json
        action = content.get('action', None)
        counter_example = content.get('counter_example', None)
        ctrl.manage_claim(player_id, line_id, action, counter_example)
        return ''
    except ValueError as e:
        return e.args[0], 422 


@app.get('/<int:game_id>')
def get_game(game_id):
    # pdb.set_trace()
    game = get_ctrl(game_id).game
    schema = Game_Schema()
    return schema.dump(game)

@app.get('/<int:game_id>/hands/<int:player_id>')
def get_hand(game_id, player_id):
    ctrl = get_ctrl(game_id)
    return jsonify(ctrl.get_hand(player_id))

@app.patch('/<int:game_id>/hands/<int:player_id>')
def update_hand(game_id, player_id):
    ctrl = get_ctrl(game_id)
    content = request.json
    ctrl.put_cards_back(content.get('put_back', []), player_id)
    ctrl.draw_tactics(content.get('num_tactic_cards', 0), player_id)
    ctrl.draw_numbers(content.get('num_number_cards', 0), player_id)
    return ''


def initiate_state(player0, player1, game_id):
    #pdb.set_trace()
    ctrl = Game_Controller(player0, player1, game_id=game_id)
    id2ctrl[ctrl.get_game_id()] = ctrl
    print(id2ctrl)


if __name__ == "__main__":
    initiate_state(0, 1, 0)
    app.run(host='0.0.0.0', debug=True)