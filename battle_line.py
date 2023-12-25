from flask import Flask, jsonify, request, make_response
from game_schema import Game_Schema
from game_controller import Game_Controller
import game_controller
from db_wrapper import DB_Wrapper

#from Flask-HTTPAuth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import pdb

app = Flask(__name__)
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

id2ctrl = dict()


def get_ctrl(game_id):
    return id2ctrl[game_id]





app = Flask(__name__)

def verify_password(username, password):
    user = app.db.get_user(username)
    return username == user.username and \
            check_password_hash(user.password, password)









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
    


@app.post('/user')
def create_user():
    try:
        content = request.json
        mail = content.get('mail')
        password = content.get('password')
        username = content.get('username')
        app.db.create_user(username, password, mail)
        return ''
    except (ValueError, KeyError) as e:
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


@app.post('/game')
def create_game():   
    try:
        content = request.json
        username = content.get('username')
        password = content.get('password')
        if not verify_password(username, password):
            return 'Authentification error', 401

        user1 = app.db.get_user(username)
        user2 = app.db.get_user(content.get('username_other'))

        p1_pid, p2_pid = user1.id, user2.id
        starting_player = content.get('starting_player', None)
        game_id = app.db.create_game(p1_pid, p2_pid, starting_player)
        return jsonify({'game_id': game_id})
    except ValueError as e:
        return e.args[0], 422 


@app.get('/game/<int:game_id>')
def get_game(game_id):   
    game = app.db.get_game(game_id)
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


if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)
    app.db = DB_Wrapper()
    app.run(host='localhost', debug=True)
