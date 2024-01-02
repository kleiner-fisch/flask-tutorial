
import itertools as iter
import random
from .line import Line
from .cards_util import ALL_TACTICS, NUMBERS_CARDS, GUILE_TACTICS
from .invalid_user_input_error import  InvalidUserInputError

HAND_SIZE = 7



class Game:

    # TODO rename variables to p1 and p2 globally
    # TODO starting_player instead should be current_player
    def __init__(self, p0, p1, game_id=None, starting_player=None,
                 p0_hand=[], p1_hand=[],
                 claim=dict(), unresolved_scout=False,
                 winner=None, public_cards=[],
                 lines = []):
        self.game_id = game_id
        self.p0 = p0
        self.p1 = p1
        self.current_player = starting_player or p0
        if p0_hand == [] and p1_hand == []:
            self.initialize_cards()
        elif p0_hand != [] and p1_hand != []:
            self.hands = {self.p0: p0_hand, self.p1 : p1_hand}
        else:
            raise ValueError("got unpexepcted hand. P0 hand : " + str(p0_hand) + " p1_hand: " +str(p1_hand))
        self.claim = claim
        self.unresolved_scout = unresolved_scout
        self.lines = lines or [Line(p0, p1) for x in range(9)]
        self.public_cards = public_cards
        self.winner = winner


    def initialize_cards(self):
        self.generate_decks()
        self.deal_cards()

    def deal_cards(self):
        self.hands = dict()
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
    

    def __repr__(self) -> str:
        return repr({'p0':self.p0, 'p1':self.p1, 'game_id': self.game_id, 'starting_player':self.current_player,
                     'p0_hand':self.hands[self.p0], 'p1_hand':self.hands[self.p1],
                     'claim':self.claim, 'unresolved_scout': self.unresolved_scout,
                     'public_cards':self.public_cards,
                     'winner':self.winner,
                     'lines':self.lines})
    
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False