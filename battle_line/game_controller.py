from .game import Game
from .cards_util import ALL_TACTICS, NUMBERS_CARDS, GUILE_TACTICS, JOKERS
from . import cards_util
from .invalid_user_input_error import InvalidUserInputError
import random
import pdb


def create_game(p1_pid, p2_pid, starting_player=None):
        '''creates a new game while choosing a random starting plaer if none is given'''
        starting_player = starting_player or random.sample([p1_pid, p2_pid], 1)[0]
        return Game(p1_pid, p2_pid, starting_player=starting_player)


class Game_Controller:
    '''processes the inputs received from outer layer.
    In particular, 
    - validates inputs,
    - implements the game logic.
    If invalid input is received the corresponding player loses the game. 
    Input validty is evaluated very strictly, even (in any way) incorrect counter examples to claims are invalid inputs.'''

    def __init__(self, game):
        self.game = game

    def get_other_player(self, player_id):
        if self.game.p0 == player_id:
            return self.game.p1
        elif self.game.p1 == player_id:
            return self.game.p0
        else:
            # ValueError is used for internal errors
            raise ValueError('received unexpected player_id: '+ str(player_id))
        
    
    def get_game_id(self):
        return self.game.game_id


    def make_claim(self, player_id, line_id):
        '''This method validates the received data and stores that a claim was made'''
        self.validate_make_claim(player_id, line_id)
        self.game.claim['player_id'] = player_id
        self.game.claim['line_id'] = line_id

    def reject_claim(self, player_id, counter_example):
        '''we assume <counter_example> has a sequence of cards serving as a legal counter example to the existing claim.
        This method validates the received data.
        '''
        self.validate_reject_claim(player_id, counter_example)
        # in the validity test we already ensured that the counter example is valid, i.e. is stronger
        line_id = self.game.claim['line_id']        
        self.game.lines[line_id].won_by = player_id
        self.game.claim.clear()

    def accept_claim(self, player_id):
        '''sets that the the claimed line is won by the claiming player
        '''
        claiming_player = self.game.claim['player_id']
        if player_id != self.get_other_player(claiming_player):
            raise InvalidUserInputError("unexpected game action")
         # in the validity test we already ensured that the counter example is valid, i.e. is stronger
        line_id = self.game.claim['line_id']        
        self.game.lines[line_id].won_by = claiming_player
        self.game.claim.clear()


    def check_winner(self, player_id):
        '''checks if the player has won, and if yes, records the winner in the game state'''
        won_lines =[self.game.lines[line_id].won_by == player_id for line_id in range(9)]
        won_5_lines = sum(won_lines) >= 5
        won_3_adjacent_lines = any([won_lines[line_id] and won_lines[line_id+1] and won_lines[line_id+2]
                                    for line_id in range(9 - 2)])
        return won_5_lines or won_3_adjacent_lines


    def validate_formation_complete(self, player_id, line_id, formation):
        is_muddy = self.game.lines[line_id].contains("MUD")
        has_4_cards = len(formation) == 4
        if is_muddy != has_4_cards:
            self.game.winner = self.get_other_player(player_id)
            raise InvalidUserInputError("provided counter example has incorrect length: " + str(len(formation)) + \
                                        "muddy flag: " + str(is_muddy))


    def validate_make_claim(self, player_id, line_id):
        ''' - it is this players turn
            - the claimed line is open (not won by either player)
            - that the claiming player has a complete line (3 or 4 cards)'''
        if self.game.current_player != player_id:
            self.game.winner = self.get_other_player(player_id)
            raise InvalidUserInputError("You can only make a claim on your turn.")
        if not self.game.lines[line_id].is_open():
            self.game.winner = self.get_other_player(player_id)
            raise InvalidUserInputError("The claimed line already is closed.")     
        line_cards = self.game.lines[line_id].sides[player_id]
        formation = [c for c in line_cards if c in JOKERS + NUMBERS_CARDS]
        self.validate_formation_complete(player_id, line_id, formation)

    def turn_done(self, pid):
        '''finishes the turn for this player and makes it the next players turn'''
        other_pid = self.get_other_player(pid)
        if self.check_winner(pid): 
            self.game.winner = pid
            return
        if self.check_winner(other_pid): 
            self.game.winner = other_pid
            return
        self.game.current_player = not self.game.current_player 


    def validate_reject_claim(self, player_id, counter_example):
        '''Validates that 
            - The other player made a claim
            - that the counter_example size is valid
                - If MUD has been played in this line, than the counter_example must have 4 cards, otherwise 3 cards
            - that the counter_example is an extension of the rejecting players side of that line (played_cards + playable_cards)
            - that the playerable_cards only involve number cards'''
        line_id = self.game.claim['line_id']
        other_player_id = self.get_other_player(player_id)
        if self.game.claim.get('player_id', None) != other_player_id:
            self.game.winner = other_player_id
            raise InvalidUserInputError("Other player has not made a claim")
        self.validate_counter_example_format(player_id, line_id, counter_example)
        self.validate_formation_complete(player_id, line_id, counter_example)
        self.validate_counter_example_strength(self, player_id, line_id, counter_example)

    def validate_counter_example_strength(self, player_id, line_id, counter_example):
        '''Checks that the counter_example is strictly stronger than <other_player> side of that line '''
        other_player_id = self.get_other_player(player_id)
        other_hand = self.game.lines[line_id][other_player_id]
        other_hand = [c for c in other_hand if c in JOKERS + NUMBERS_CARDS]
        is_foggy = self.game.lines[line_id].contains("FOG")
        if not cards_util.is_stronger(counter_example, other_hand, is_foggy):
            self.game.winner = other_player_id
            raise InvalidUserInputError("provided counter example not stronger."  \
                                        " Your counter example: " + str(counter_example) + \
                                        " Opponents hand: " + str(other_hand))

    def validate_counter_example_format(self, player_id, line_id, counter_example):
        '''checks that the counter example is possible, given the available public information'''
        other_player_id = self.get_other_player(player_id)
        played_cards = self.game.lines[line_id][player_id]
        # the counter example only has JOKERS + NUMBERS, Hence filter out GUILE_TACTICS from played_cards
        played_cards = [c for c in played_cards if c in JOKERS + NUMBERS_CARDS]
        if any([c not in counter_example for c in played_cards]):
            self.game.winner = other_player_id
            raise InvalidUserInputError("provided counter example is not an extension of played cards.")          
        if len(counter_example) == len(set(counter_example)):
            self.game.winner = other_player_id
            raise InvalidUserInputError("provided counter example has a card multiple times.")
        future_cards = [c for c in counter_example if c not in played_cards]
        public_cards = sum([line.get_all_cards() for line in self.game.lines], [])
        public_cards += self.game.public_cards
        available_cards = [c for c in NUMBERS_CARDS if c not in public_cards] 
        if any([c not in available_cards for c in future_cards]):
            self.game.winner = other_player_id
            raise InvalidUserInputError("provided counter example uses illegal card." \
                                        "Either planned with already used card, or a tactics card")
        
    def get_used_cards(self):
        '''returns all cards handed out to players, i.e. all cards _not_ part of a deck anymore'''
        public_cards = sum([line.get_all_cards() for line in self.game.lines], [])
        public_cards += self.game.public_cards
        hands = self.game.hands[self.game.p0] + self.game.hands[self.game.p1] 
        return public_cards + hands
    

    def put_cards_back(self, cards, pid):
        '''takes the given cards from the player and puts them back into thei respective decks.
        Input assumed to be validated already!'''
        self.game.hands[pid] = [c for c in self.game.hands[pid] if c not in cards]
        
    def get_numbers_deck(self):
        '''returns the numbers deck, that is all numbers cards without those already handed out to players'''
        return [c for c in NUMBERS_CARDS if c not in self.get_used_cards()]

    def get_tactics_deck(self):
        '''returns the tactics deck, that is all tactics cards without those already handed out to players'''
        return [c for c in ALL_TACTICS if c not in self.get_used_cards()]


    def draw_tactics(self, no_cards, pid):
        '''draws the number of cards from the tactics deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        new_cards = random.sample(self.get_tactics_deck(), no_cards)
        self.game.hands[pid] = self.game.hands[pid] + new_cards


    def draw_numbers(self, no_cards, pid):
        '''draws the number of cards from the numbers deck and gives them the given player
        Note that cards are drown from the start of the deck!
        Input assumed to be validated already!'''
        new_cards = random.sample(self.get_numbers_deck(), no_cards)
        self.game.hands[pid] = self.game.hands[pid] + new_cards

    def get_hand(self, player_id):
        return self.game.hands[player_id]
    
    def play_card(self, player_id, line_id, card, other_card=None):
        '''plays the given card in the specified line for the given player.
        Note that <other_card> is the name of a card that is affected by <card> (only relevant for a few tactics)
        - checks that the move is legal
        - performs all steps necessary to play the card
        - tracks in the game state whether further subturn steps are necessary by player (scout processing)'''
        # TODO rename line_id to line and similar for other variables
        self.validate_played_card(player_id, line_id, card, other_card)
        if card in ["REDEPLOY", "TRAITOR"]:
            self.move_card_to(other_card, player_id, line_id)
        elif card == "DESERTER":
            self.desert_card(other_card)
        g  = self.game
        g.hands[player_id].remove(card)
        self.add_card_to_line(player_id, line_id, card)
       
    def desert_card(self, card):
        '''moves the specified <card> from its battle line to a pool of public but unused and unusable cards'''
        self.remove_card(card)
        self.game.public_cards.append(card)
    
    def remove_card(self, card):
        '''finds <card> and removes it from its line (usually to be moved somewhere else).
        It is an error if the card is not found among the battle lines'''
        if not any(map(lambda line: line.remove_card(card), self.game.lines)):
            raise ValueError('Card to delete not found' + str(card))


    def move_card_to(self, card, player_id, line_id):
        '''moves the <card> to the given <line> on the side of <player_id>'''
        self.remove_card(card)
        # TODO it easily might happen to accidentally use line_id instead of player_id or vice versa. 
        #   That will be difficult to track down. Perhaps use enums to have type safety?
        self.game.lines[line_id].sides[player_id].append(card)

    def add_card_to_line(self, player, line, card):
        self.game.lines[line].sides[player].append(card)


    def validate_played_card(self, player_id, line_id, card, other_card):
        '''Checks that
        - the card is allowed to be played in the current state 
            - not too many tactics played
            - it is that players turn
            - card is in players hand
            - no other action expected (resolving SCOUT)
            - other_card is only non-None if actually needed (REDEPLOY, TRAITOR, DESERTER) 
        - the card can be played in the given line
            - the players section of the given line is not full (taking into consideration the tactics, e.g. MUD)
            - the line is not closed
        returns True if the move is legal, Fales otherwise'''
        #raise ValueError('FOOOO')
