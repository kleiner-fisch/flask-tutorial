import battle_line

import unittest
from battle_line import game_controller as gm
from battle_line import game

class TestCards_Util(unittest.TestCase):

    def setUp(self):
        self.game1 = game.Game(**{'p1': 1, 'p2': 0, 'game_id': 1, 'current_player': 1, 
             'p1_hand': ['F4', 'C1', 'B7', 'C8', 'D7', 'A7', 'F10'], 
             'p2_hand': ['E7', 'E9', 'E4', 'A1', 'F7', 'A8', 'A9'], 
             'claim': {}, 'unresolved_scout': False, 'public_cards': [], 
             'winner': None, 
             'lines': [{'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}, 
                       {'won_by': None, 'sides': '{1: [], 0: []}'}]})


    def test_create_game(self):
        gm.create_game(1, 2)

    def test_put_cards_back(self):
        ctrl = gm.Game_Controller(self.game1)
        p1 = self.game1.p1
        p2 = self.game1.p2
        cards = set(['F4', 'B7'])
        remaining_cards_p1 = set(['C1', 'C8', 'D7', 'A7', 'F10'])
        remaining_cards_p2 = set(['E7', 'E9', 'E4', 'A1', 'F7', 'A8', 'A9'])
        ctrl.put_cards_back(cards, 1)
        assert set(self.game1.hands[p1]) == remaining_cards_p1
        assert set(self.game1.hands[p2]) == remaining_cards_p2


    

