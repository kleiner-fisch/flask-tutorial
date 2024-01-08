

import pytest
from battle_line import create_app
import tempfile
import os
from battle_line.line import Line
from battle_line.game import Game
from battle_line import game_util
from battle_line import cards_util

@pytest.fixture()
def game1():
    def _game1(pid1, pid2, current_player=None):
        return "Game({p1}, {p2}, None, {current_player}, \
                ['F4', 'C1', 'B7', 'C7', 'D6', 'A7', 'F1'], \
                ['E7', 'E2', 'E4', 'A1', 'F7', 'F8', 'A3'],             \
                dict(), False, None, [], \
                [Line(dict([({p2},  []), ({p1},  [])]), None, None), \
                 Line(dict([({p2},  []), ({p1},  [])]), None, None), \
                 Line(dict([({p2},  []), ({p1},  [])]), None, None), \
                 Line(dict([({p2},  ['F10', 'F9']), ({p1},  [])]), None, None), \
                 Line(dict([({p2},  ['E9', 'E8']), ({p1},  [])]), None, None), \
                 Line(dict([({p1},  ['B10', 'B9']), ({p2},  [])]), None, None), \
                 Line(dict([({p2},  ['D7', 'D2', 'D8']), ({p1},  [])]), None, None), \
                 Line(dict([({p1},  ['C9', 'C8']), ({p2},  [])]), None, None), \
                 Line(dict([({p1},  ['A10', 'A9', 'A8']), ({p2},  [])]), \
                      None, None)])".format(p1=pid1, p2=pid2, current_player=(pid1 if current_player is None else current_player))



    return _game1

@pytest.fixture()
def app():
    app = create_app()
    db_fd, db_path = tempfile.mkstemp()

    #db_test_url = os.path.join(app.instance_path, 'test.db')
    app.config.update({
        #"DATABASE_URL": db_test_url,
        "DATABASE_URL": db_path
    })

    # other setup can go here

    yield app

    # clean up / reset resources here
    #os.remove(db_test_url)
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_create_game1(client):
    '''tests whether we can create a game and then get it'''
    body1 = {'mail':'mail', 'password':'abc','username':'bob'}
    client.post("/user", json=body1)
    body2 = {'mail':'mail', 'password':'abc','username':'alice'}
    client.post("/user", json=body2)
    create_game_body = {"username": "bob", "password":"abc", "username_other":"alice"}
    game_post_response = client.post("/game", json=create_game_body)
    # the first game should have id 1. But mainly we care whether it was created at all
    assert game_post_response.status_code == 200
    assert game_post_response.json['game_id'] == 1
    # We check whether the game is in the db
    game_get_response = client.get('/game/{}'.format(1))
    assert game_get_response.status_code == 200
    

def test_create_game2(client):
    '''tests whether we can create a game and then get it, while providing a starting player'''
    body1 = {'mail':'mail', 'password':'abc','username':'bob'}
    client.post("/user", json=body1)
    body2 = {'mail':'mail', 'password':'abc','username':'alice'}
    client.post("/user", json=body2)
    create_game_body = {"username": "bob", "password":"abc", "username_other":"alice", 
                        "starting_player":"alice"}
    game_post_response = client.post("/game", json=create_game_body).json
    game_id=game_post_response['game_id']
    # We check whether the game is in the db
    game_json = client.get('/game/{}'.format(game_id)).json
    assert game_json['current_player'] == game_json['p2'], 'We expect alice to be the starting player'

def test_create_game3(client, game1):
    '''tests whether we can instantiate a game with a predefined state'''
    body1 = {'mail':'mail', 'password':'abc','username':'bob'}
    pid1=client.post("/user", json=body1).json['pid']
    body2 = {'mail':'mail', 'password':'abc','username':'alice'}
    pid2=client.post("/user", json=body2).json['pid']
    game_state = game1(pid1, pid2)
    create_game_body = {"username": "bob", "password":"abc", "game_state": game_state}
    game_post_response = client.post("/game", json=create_game_body)
    game_id = game_post_response.json['game_id']
    new_game = client.get('/game/{}'.format(game_id)).json
    hand_p1 = client.get('/game/{}/hand'.format(game_id), json={'password':'abc','username':'bob'}).json
    hand_p2 = client.get('/game/{}/hand'.format(game_id), json={'password':'abc','username':'alice'}).json
    org_game = eval(game_state)
    loaded_game = game_util.game_from_json(new_game)
    loaded_game.hands = {pid1 : hand_p1, pid2 : hand_p2}
    # the returns json object does not have line_ids or a game_
    assert game_util.weakly_equal(org_game, loaded_game), \
        "We expect the original version, and the stored and then retrieved games to be equal, except for game_id and line_ids"


def test_action_sequence1(client, game1):
    '''tests whether we can instantiate a game with a predefined state'''
    # First we create the game
    alice=  {'password':'abc','username':'alice'}
    bob = {'password':'abc','username':'bob'}
    pid1=client.post("/user", json=bob | {'mail':'mail'}).json['pid']
    pid2=client.post("/user", json=alice | {"mail":"mail"}).json['pid']
    game_state = game1(pid1, pid2)
    game_post_response = client.post("/game", json=bob | {"game_state": game_state})
    game_id = game_post_response.json['game_id']
    # play a card
    card1 = "C7"
    game_path = '/game/{game_id}'.format(game_id=game_id)
    line_path = lambda line_number: '{}/{}'.format(game_path, line_number)
    hand_path = game_path + '/hand'
    client.patch(line_path(7), json=bob | { "card":card1, "action":"PLAY_CARD"})
    hand_p1 = client.get(hand_path, json=bob).json
    assert card1 not in hand_p1, "we expect the card we just played not to be in our hand"
    assert len(hand_p1) == 6, "we just played a card, so we should have 7 cards now"
    # draw card
    client.patch(hand_path, json=bob | {"num_tactic_cards":1})
    hand_p1 = client.get(hand_path, json=bob).json
    assert sum([c in cards_util.ALL_TACTICS for c in hand_p1]) == 1, "we drew a tactics card, so we should have 1 now"
    # make claim
    client.patch(line_path(7), json=bob | {"action" : "MAKE_CLAIM"})
    game = client.get(game_path).json
    assert game['claim']['player_id'], game['claim']['line_number'] == (pid1, 7)
    # accept claim
    client.patch(game_path, json=alice | { "action":"ACCEPT_CLAIM"} )
    assert game['lines'][7]['won_by'] is None, "Just to be sure that actually accepting a claim sets the won_by-bit"
    game = client.get(game_path).json
    assert game['lines'][7]['won_by'] == pid1
    # turn done
    client.patch(game_path, json=bob | { "action":"TURN_DONE"} )
    game = client.get(game_path).json
    assert game['current_player'] == pid2, 'as bob finished his turn, it is alices turn now'
    # alice plays a card
    client.patch(line_path(3), json=alice | { "card":"F8", "action":"PLAY_CARD"})
    # draw card
    client.patch(hand_path, json=alice | {"num_number_cards":1})
    hand_p2 = client.get(hand_path, json=alice).json
    assert sum([c in cards_util.NUMBERS_CARDS for c in hand_p2]) == 7, "we drew a numbers card, so we should have 7 again"
    # make claim
    client.patch(line_path(3), json=alice | {"action" : "MAKE_CLAIM"})
    game = client.get(game_path).json
    assert game['claim']['player_id'], game['claim']['line_number'] == (pid2, 3)
    # accept claim
    client.patch(game_path, json=bob | { "action":"ACCEPT_CLAIM"} )
    assert game['lines'][3]['won_by'] is None, "Just to be sure that actually accepting a claim sets the won_by-bit"
    game = client.get(game_path).json
    assert game['lines'][3]['won_by'] == pid2
    # make another claim
    client.patch(line_path(6), json=alice | {"action" : "MAKE_CLAIM"})
    # reject claim
    body_counter_example = {'counter_example' : ["F2", "C2", "A2"], 'action' : 'REJECT_CLAIM'}
    client.patch(game_path, json=bob | body_counter_example )
    game = client.get(game_path).json
    assert game['lines'][6]['won_by'] == pid1, 'as bob provided a correct counter example to alice claims, bob has won the line'
    # turn done
    client.patch(game_path, json=alice | { "action":"TURN_DONE"} )
    # finish the game, 
    client.patch(line_path(0), json=bob | { "card":'F4', "action":"PLAY_CARD"})
    client.patch(line_path(8), json=bob | {"action" : "MAKE_CLAIM"})
    client.patch(game_path, json=alice | { "action":"ACCEPT_CLAIM"} )
    game_before = client.get(game_path).json
    assert game_before['winner'] is None, 'No winner yet'
    client.patch(game_path, json=bob | { "action":"TURN_DONE"} )
    game_after = client.get(game_path).json
    assert game_after['winner'] == pid1, 'bob has won 3 adjacent lines, and has won'




# TODO should have a test with complicated tactics: REDEPLOY, SCOUT, TRAITOR



# TODO currently no tests (and also no server side checking) for proper validation, 
#   and handling of incorrect inputs and proper responses to incorrect inputs






def test_play_card(client):
    '''tests if we can play a card'''
    # create game
    body1 = {'mail':'mail', 'password':'abc','username':'bob'}
    client.post("/user", json=body1)
    body2 = {'mail':'mail', 'password':'abc','username':'alice'}
    client.post("/user", json=body2)
    create_game_body = {"username": "bob", "password":"abc", "username_other":"alice"}
    game_post_response = client.post("/game", json=create_game_body)
    game_id = game_post_response.json['game_id']
    
    # first get the hand ...
    bob_auth = {'password':'abc','username':'bob'}
    get_hand_response = client.get('/game/{}/hand'.format(game_id), json=bob_auth)
    assert get_hand_response.status_code == 200
    hand = get_hand_response.json
    assert len(hand) == 7, 'initially we have 7 cards in our hand'
    # ... to play our first card to line 2
    card, line_no = hand[0], 2
    play_card = {'action':'PLAY_CARD', 'card':card}
    play_card.update(bob_auth)
    play_card_response = client.patch('/game/{}/{}'.format(game_id, line_no), json=play_card)
    assert play_card_response.status_code == 200

    # verify that the card was played as expected
    # First we check our hand
    new_hand_response = client.get('/game/{}/hand'.format(game_id), json=bob_auth)
    assert new_hand_response.status_code == 200
    new_hand = new_hand_response.json
    assert len(new_hand) == 6, 'as we played a card we expect to have 6 cards'
    assert card not in new_hand, 'the card should not be in our hand'
    # the we check the line
    game = client.get('/game/{}'.format(game_id)).json
    p1, p2 = game['p1'], game['p2']
    for index, line in enumerate(game['lines']):
        # Note that in JSON keys are always strings, which we so far did not really consider..
        if index == line_no:
            assert [card] == line['sides'][str(p1)], 'We expect the played card in line 2'
            assert len(line['sides'][str(p2)]) == 0, 'We expect the other side t obe empty, as the player has not played a card'
        else:
            assert len(line['sides'][str(p1)]) == 0, 'We expect the other lines to be empty, for both sides'
            assert len(line['sides'][str(p2)]) == 0, 'We expect the other lines to be empty, for both sides'


# TODO create test cases:
#   - where we do several turns 
#   - make/reject a claim --> Here ctreating an arbitrary state would be helpful
#   - win the game


