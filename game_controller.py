from game import Game
from game import HAND_SIZE

import uuid


class Game_Controller:

    def __init__(self, p0, p1, game_id=None):
        '''for easier debugging we allow passing game_id
        TODO: how should game_ids be properly handled??'''
        self.game = Game(p0, p1)
        self.game_id = game_id if game_id != None else uuid.uuid4()
    
    def get_game_id(self):
        return self.game_id

    def play_card(self, pid, line_id, card_name):
        raise NotImplementedError
                  

    def deal_cards(self):
        g = self.game
        g.hands[g.p0] = g.numbers_deck[:g.HAND_SIZE]
        g.hands[g.p1] = g.numbers_deck[HAND_SIZE:2*HAND_SIZE]
        g.numbers_deck = g.numbers_deck[2*HAND_SIZE:]

    def put_cards_back(self, cards, pid):
        '''takes the given cards from the player and puts them back into thei respective decks.
        Input assumed to be validated already!'''
        g = self.game
        g.hands[pid] = [c for c in g.hands[pid] if c not in cards]
        g.numbers_deck =  [c for c in cards if c in g.numbers_deck ] + \
            g.numbers_deck
        g.tactics_deck =  [c for c in cards if c in g.tactics_deck ] + \
            g.tactics_deck

    def draw_tactics(self, no_cards, pid):
        '''draws the number of cards from the tactics deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        g  = self.game
        g.hands[pid] = g.hands[pid] + g.tactics_deck[:no_cards]
        g.tactics_deck = g.tactics_deck[no_cards:]


    def draw_numbers(self, no_cards, pid):
        '''draws the number of cards from the numbers deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        g = self.game
        g.hands[pid] = g.hands[pid] + g.numbers_deck[:no_cards]
        g.numbers_deck = g.numbers_deck[no_cards:]

    def get_hand(self, player_id):
        return self.game.hands[player_id]