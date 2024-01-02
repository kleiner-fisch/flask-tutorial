from flask import Flask, jsonify, request, make_response
from .game_schema import Game_Schema
from .game_controller import Game_Controller
from . import game_controller
from .db_wrapper import DB_Wrapper
from .invalid_user_input_error import InvalidUserInputError
import os

#from Flask-HTTPAuth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import pdb






def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE_URL=os.path.join(app.instance_path, 'battle_line.db'),
        DATABASE_ECHO=True
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    if not os.path.isdir(app.instance_path):
        os.makedirs(app.instance_path, exist_ok=False)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db_wrapper

    ######
    #
    # The Endpoints
    #
    def verify_password(username, password):
        db = db_wrapper.get_db()
        user = db.get_user(username)
        return username == user.username and \
                check_password_hash(user.password, password)


    # TODO currently the plan is to use uuid for ids. This may be unpractibable as URIs may be terribly long if we chain such ids...
    #   - uuid as ids would require to use uuid as type in the path, i.e. use <uuid:game_id>


    # TODO game creation
    # TODO winning of game

    @app.patch('/game/<int:game_id>/<int:line_id>')
    def play_card(game_id, line_id):
        db = db_wrapper.get_db()
        try:
            # TODO should rename line_id to line_number to avoid confusion
            content = request.json
            password = content.get('password')
            username = content.get('username')
            if not verify_password(username, password):
                return 'Authentification error', 401
            user = db.get_user(username)
            card = content.get('card')
            other_card = content.get('affected_card', None)
            
            game = db.get_game(game_id)
            ctrl = Game_Controller(game)
            ctrl.play_card(user.id, line_id, card, other_card)
            db.store_game(game)
            return ''
        except ValueError as e:
            return e.args[0], 422 
        


    @app.post('/user')
    def create_user():
        db = db_wrapper.get_db()
        try:
            content = request.json
            mail = content.get('mail')
            password = content.get('password')
            username = content.get('username')
            db.create_user(username, password, mail)
            return ''
        except (ValueError, KeyError) as e:
            return e.args[0], 422 


    @app.patch('/game/<int:game_id>')
    def game_action(game_id):
        db = db_wrapper.get_db()
        try:
            content = request.json
            username = content.get('username')
            password = content.get('password')
            if not verify_password(username, password):
                return 'Authentification error', 401  
            game = db.get_game(game_id)
            user = db.get_user(username)
            ctrl = Game_Controller(game)
            action = content.get('action')
            if action == 'TURN_DONE':
                ctrl.turn_done(user.id)
            elif action == 'REJECT_CLAIM':
                counter_example = content.get('counter_example', None)
                ctrl.reject_claim(user.id, counter_example)
            elif action == 'ACCEPT_CLAIM':         
                ctrl.accept_claim(user.id)
            else:
                raise InvalidUserInputError("invalid game action: " + action)
            db.store_game(game)
            return ''
        except ValueError as e:
            return e.args[0], 422 
        

    @app.patch('/game/<int:game_id>/<int:line_id>')
    def line_action(game_id, line_id):
        db = db_wrapper.get_db()
        try:
            content = request.json
            username = content.get('username')
            password = content.get('password')
            if not verify_password(username, password):
                return 'Authentification error', 401  
            game = db.get_game(game_id)
            user = db.get_user(username)
            ctrl = Game_Controller(game)
            action = content.get('action')
            if action == 'MAKE_CLAIM':
                ctrl.make_claim(user.id, line_id)
            elif action == 'PLAY_CARD':
                card = content.get('card')
                other_card = content.get('affected_card', None)            
                ctrl.play_card(user.id, line_id, card, other_card)
            else:
                raise InvalidUserInputError("invalid line action: " + action)
            db.store_game(game)
            return ''
        except ValueError as e:
            return e.args[0], 422 


    @app.post('/game')
    def create_game():   
        # TODO currently in each request several connections are made to DB.
        #   It would be better to have only one connection, and make sure it is closed after the request (or during an error)
        db = db_wrapper.get_db()
        try:
            #pdb.set_trace()
            content = request.json
            username = content.get('username')
            password = content.get('password')
            if not verify_password(username, password):
                return 'Authentification error', 401

            user1 = db.get_user(username)
            user2 = db.get_user(content.get('username_other'))

            p1_pid, p2_pid = user1.id, user2.id
            # TODO inconsistent that I expect a player ID for starting player..
            starting_player = content.get('starting_player', None)
            game_id = db.create_game(p1_pid, p2_pid, starting_player)
            return jsonify({'game_id': game_id})
        except ValueError as e:
            return e.args[0], 422 


    @app.get('/game/<int:game_id>')
    def get_game(game_id):   
        db = db_wrapper.get_db()
        game = db.get_game(game_id)
        schema = Game_Schema()
        return schema.dump(game)

    @app.get('/game/<int:game_id>/hand')
    def get_hand(game_id):
        db = db_wrapper.get_db()
        content = request.json
        username = content.get('username')
        password = content.get('password')
        if not verify_password(username, password):
            return 'Authentification error', 401
        game = db.get_game(game_id)
        user = db.get_user(username)

        return jsonify(game.hands[user.id])

    @app.patch('/game/<int:game_id>/hand')
    def update_hand(game_id):
        db = db_wrapper.get_db()
        content = request.json
        username = content.get('username')
        password = content.get('password')
        if not verify_password(username, password):
            return 'Authentification error', 401
        
        # TODO need to check if the action is permitted 
        game = db.get_game(game_id)
        ctrl = Game_Controller(game)

        user = db.get_user(username)
        
        # TODO when we put cards back we need to remember the top cards of the stack!
        ctrl.put_cards_back(content.get('put_back', []), user.id)
        ctrl.draw_tactics(content.get('num_tactic_cards', 0), user.id)
        ctrl.draw_numbers(content.get('num_number_cards', 0), user.id)
        db.store_game(game)
        return ''
        
    return app



# if __name__ == "__main__":
#     # app.run(host='0.0.0.0', debug=True)
#     app = create_app()
#     app.run(host='localhost', debug=True)
