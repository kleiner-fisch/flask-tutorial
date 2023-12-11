from flask import Flask, jsonify, request
from game import Game

app = Flask(__name__)

games = dict()
player0 = 0
player1 = 1

def getGame(game_id):
    return games[game_id]

# ENDPOINTS
@app.route("/")
def hello_world():
    return "<p>Hello, World!!!</p>"


@app.get('/<int:game_id>/hands/<int:player_id>')
def get_hand(game_id, player_id):
    game = getGame(game_id)
    return jsonify(game.get_hand(player_id))

@app.patch('/<int:game_id>/hands/<int:player_id>')
def update_hand(game_id, player_id):
    # JSON Body desribing how many cards to put back
    game = getGame(game_id)
    content = request.json
    game.put_cards_back(content.get('put_back', []), player_id)
    game.draw_tactics(content.get('num_tactic_cards', 0), player_id)
    game.draw_tactics(content.get('num_number_cards', 0), player_id)
    return ''


def initiate_state():
    games[0] = Game(player0, player1)
#    games[0].hands[player0] = ["B1", "B2"]


if __name__ == "__main__":
    initiate_state()
    app.run(host='0.0.0.0', debug=True)