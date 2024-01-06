

import pytest
from battle_line import create_app
import tempfile
import os

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




    






