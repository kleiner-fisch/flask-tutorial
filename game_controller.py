from game import Game
from game import  GUILE_TACTICS

import uuid


class Game_Controller:

    def __init__(self, p0, p1, game_id=None):
        '''for easier debugging we allow passing game_id
        TODO: how should game_ids be properly handled??'''
        game_id = game_id if game_id != None else uuid.uuid4()
        self.game = Game(p0, p1, game_id)
        
    
    def get_game_id(self):
        return self.game.game_id



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

        # lines = self.get_all_lines()
        # for line in lines:
        #     try:
        #         # When the card is not present the return statement is not executed
        #         line.remove(card)
        #         return
        #     except ValueError:
        #         pass



    # def get_all_lines(self):
    #     '''returns a list of all lines. 
    #     <result> is a list of lists and has lines from both players'''
    #     super_list = self.game.lines.values()
    #     return [line for lines in super_list for line in lines]


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
