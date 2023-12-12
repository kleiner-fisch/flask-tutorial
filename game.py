
import itertools as iter
import random
from line import Line

HAND_SIZE = 7
ALL_TACTICS = ["ALEXANDER", "CAVALRY", "DARIUS", "MUD", "SHIELD_BEARER", "FOG", "SCOUT", "REDEPLOY", "DESERTER", "TRAITOR"]
GUILE_TACTICS= ["SCOUT", "REDEPLOY", "DESERTER", "TRAITOR"]
NUMBERS_CARDS = list(map(''.join, \
                    iter.product(["A", "B", "C", "D", "E", "F"], \
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])))


class Game:

    def __init__(self, p0, p1, game_id, starting_player=None):
        self.current_player = starting_player or p0
        self.game_id = game_id
        self.hands = dict()
        self.p0 = p0
        self.p1 = p1
        self.claim = dict()
        self.unresolved_scout = False
        self.lines = [Line(p0, p1) for x in range(9)]
        self.initialize_game()
        self.public_cards = []


    def initialize_game(self):
        self.generate_decks()
        self.deal_cards()

    def deal_cards(self):
        self.hands[self.p0] = self.numbers_deck[:HAND_SIZE]
        self.hands[self.p1] = self.numbers_deck[HAND_SIZE:2*HAND_SIZE]
        self.numbers_deck = self.numbers_deck[2*HAND_SIZE:]


    def generate_decks(self):
        self.tactics_deck = list(ALL_TACTICS)
        random.shuffle(self.tactics_deck)
        self.numbers_deck = list(NUMBERS_CARDS)
        random.shuffle(self.numbers_deck)

    def get_hand(self, player_id):
        return self.hands[player_id]
    

