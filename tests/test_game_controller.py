import battle_line

import unittest
from battle_line import game_controller as gm
from battle_line import game
from battle_line.line import Line
from battle_line import cards_util as util

class TestCards_Util(unittest.TestCase):

    def setUp(self):
        self.game1 = game.Game(**{'p1': 1, 'p2': 2, 'game_id': 1, 'current_player': 1, 
             'p1_hand': ['F4', 'C1', 'B7', 'C7', 'D7', 'A7', 'F1'], 
             'p2_hand': ['E7', 'E2', 'E4', 'A1', 'F7', 'F8', 'A3'], 
             'claim': {}, 'unresolved_scout': False, 'public_cards': [], 
             'winner': None, 
             'lines': [Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["F10", "F9"], 1: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["E9", "E8"], 1: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["D10", "D9", "D8"], 1: []}}),
                       Line(**{'won_by': None, 'sides': {1: ["B10", "B9"], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: ["C9", "C8"], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: ["A10", "A9", "A8"], 2: []}})]})
        
        self.game2 = game.Game(**{'p1': 1, 'p2': 2, 'game_id': 1, 'current_player': 1, 
             'p1_hand': ['F4', 'C1', 'B7', 'C7', 'D6', 'A7', 'F1'], 
             'p2_hand': ['E7', 'E2', 'E4', 'A1', 'F7', 'F8', 'A3'], 
             'claim': {}, 'unresolved_scout': False, 'public_cards': [], 
             'winner': None, 
             'lines': [Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: [], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["F10", "F9"], 1: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["E9", "E8"], 1: []}}), 
                       Line(**{'won_by': None, 'sides': {1: ["B10", "B9"], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {2: ["D7", "D2", "D8"], 1: []}}),
                       Line(**{'won_by': None, 'sides': {1: ["C9", "C8"], 2: []}}), 
                       Line(**{'won_by': None, 'sides': {1: ["A10", "A9", "A8"], 2: []}})]})


    def test_create_game(self):
        '''attempts to create a game to check if it works without errors'''
        gm.create_game(1, 2)

    def test_put_cards_back(self):
        '''tests if putting back cards will leave players with expected hands'''
        ctrl = gm.Game_Controller(self.game1)
        p1 = self.game1.p1
        p2 = self.game1.p2
        cards = set(['F4', 'B7'])
        # TODO we modified the cards, and need to adapt this here
        remaining_cards_p1 = set([ 'C1',  'C7', 'D7', 'A7', 'F1'])
        remaining_cards_p2 = set(['E7', 'E2', 'E4', 'A1', 'F7', 'F8', 'A3'])
        ctrl.put_cards_back(cards, 1)
        assert set(self.game1.hands[p1]) == remaining_cards_p1
        assert set(self.game1.hands[p2]) == remaining_cards_p2

    def test_action_sequence1(self):
        '''we do a number of turns as a big test, using a wide arrange of actions supported'''
        ctrl = gm.Game_Controller(self.game2)
        p1 = self.game2.p1
        p2 = self.game2.p2
        # p1 turn
        ctrl.play_card(player_id=p1, line_number=7, card="C7") 
        ctrl.draw_tactics(1, p1)
        assert sum([c in util.ALL_TACTICS    for c in self.game2.hands[p1] ]) == 1, "We drew a tactics card, so we should have one"
        ctrl.make_claim(p1, 7)
        ctrl.accept_claim(p2)
        assert self.game2.lines[7].won_by == p1, 'as the claim was accepted we expect p1 to have won this line'
        ctrl.turn_done(p1)
        # P2 turn
        ctrl.play_card(player_id=p2, line_number=3, card="F8") 
        ctrl.draw_numbers(1, p2)
        assert sum([c in util.ALL_TACTICS    for c in self.game2.hands[p2] ]) == 0, \
            "We drew a numbers card, so we should have no tactics card"
        # we claim the line where we have just completed the royal flush
        ctrl.make_claim(p2, 3)
        ctrl.accept_claim(p1)
        assert self.game2.lines[3].won_by == p2, 'as the claim was accepted we expect p2 to have won this line'
        # we make another claim, but p2 only has a flush there!
        ctrl.make_claim(p2, 6)
        ctrl.reject_claim(p1, ["F2", "C2", "A2"])
        assert self.game2.lines[6].won_by == p1, 'the counter example is valid. \
            Hence, we successfully reject the claim and won the line'
        ctrl.turn_done(p2)        
        # again p1
        ctrl.play_card(player_id=p1, line_number=0, card="F4") 
        ctrl.make_claim(p1, 8)
        ctrl.accept_claim(p2)
        ctrl.turn_done(p1)       
        assert self.game2.winner == p1, '''p1 won 3 adjacent lines''' 








    

