
import itertools as iter
import random

HAND_SIZE = 7
ALL_TACTICS = ["Alexander", "Cavalerie", "Darius"]
NUMBERS_CARDS = list(map(''.join, \
                    iter.product(["B", "Y", "R", "O", "G", "L"], \
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])))

class Game:

    def __init__(self, p0, p1):
        self.hands = dict()
        self.p0 = p0
        self.p1 = p1
        self.initialize_game()

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
        #colors = ["B", "Y", "R", "O", "G", "L"]
        #numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        self.numbers_deck = list(NUMBERS_CARDS)
        random.shuffle(self.numbers_deck)

    def get_hand(self, player_id):
        return self.hands[player_id]
    

    def put_cards_back(self, cards, pid):
        '''takes the given cards from the player and puts them back into thei respective decks.
        Input assumed to be validated already!'''
        self.hands[pid] = [c for c in self.hands[pid] if c not in cards]
        self.numbers_deck =  [c for c in cards if c in self.numbers_deck ] + \
            self.numbers_deck
        self.tactics_deck =  [c for c in cards if c in self.tactics_deck ] + \
            self.tactics_deck

    def draw_tactics(self, no_cards, pid):
        '''draws the number of cards from the tactics deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        self.hands[pid] = self.hands[pid] + self.tactics_deck[:no_cards]
        self.tactics_deck = self.tactics_deck[no_cards:]


    def draw_numbers(self, no_cards, pid):
        '''draws the number of cards from the numbers deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        self.hands[pid] = self.hands[pid] + self.numbers_deck[:no_cards]
        self.numbers_deck = self.numbers_deck[no_cards:]