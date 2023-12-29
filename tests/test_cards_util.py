import unittest
import cards_util
from parameterized import parameterized
import pdb

sf_mid_j=  ['DARIUS', 'A5', 'A4']

sf_w = ["A4", "A5", "A3"]
sf_s = ["B8", "B10", "B9"]

nothing_w_j = ["A4", "D1", "SHIELD_BEARER"]
nothing_w = ["A4", "D1", "A3"]
nothing_s = ["A9", "D10", "A10"]

straight_w = ['A1', 'C2', 'D3']
straight_s = ['A6', 'E8', 'D7']
straight_s_j = ['ALEXANDER', 'E8', 'D7']

flush_w_j = ["A1", "A3", "CAVALRY"]
flush_w = ["A1", "A3", "A6"]
flush_s = ["A10", "A9", "A6"]

triple_w = ["A2", "C2", "E2"]
triple_s = ["A8", "CAVALRY", "E8"]

four_w = ["A2", "C2", "E2", "B2"]
four_s = ["A8", "CAVALRY", "E8", "DARIUS"]
nothing_w_4 = ["A4", "D1", "A3", "A1"]
sf_mid_j_4=  ['DARIUS', 'A5', 'A4', 'ALEXANDER']
flush_s_4 = ["A10", "A9", "A6", 'A8']


# For three cards we follow the following sums
# mid has sum 15 - 20
# strong has sum > 21
# weak has sum < 15
# 
# The notation is:
# (cards1, cards2, has_fog, is_stronger) 
paras = [(sf_w, sf_mid_j, True, False), 
        (sf_w, sf_mid_j, False, False), 
        (sf_s, sf_mid_j, False, True), 
        (sf_s, sf_mid_j, True, True), 
        (sf_s, sf_w, False, True), 
        (sf_mid_j, nothing_w_j, False, True),
        (sf_s, nothing_s, True, False),
        (nothing_w, straight_w, False, False),
        (straight_w, nothing_s, False, True),
        (straight_s, straight_w, False, True),
        (straight_s, straight_s_j, False, False),
        (nothing_s, flush_s, True, True),
        (sf_w, flush_s, False, True),
        (sf_w, flush_s, True, False),
        (flush_s, flush_w, False, True),
        (triple_w, flush_s, False, True),
        (straight_s_j, flush_s, False, False),
        (triple_s, triple_w, False, True),
        (triple_s, nothing_s, False, True),
        (triple_s, sf_s, False, False),
        (four_w, four_s, False, False),
        (four_w, nothing_w_4, False, True),
        (sf_mid_j_4, four_s, False, True),
        (sf_mid_j_4, four_s, True, False),
        (sf_mid_j_4, flush_s_4, True, False),
        (sf_mid_j_4, flush_s_4, False, True),
        (nothing_w_4, flush_s_4, False, False),
        (nothing_w_4, flush_s_4, True, False),
        (four_w, flush_s_4, False, True),
        (four_w, flush_s_4, True, False)]
    


class TestCards_Util(unittest.TestCase):



    @parameterized.expand(paras)
    def test_is_stronger(self, cards1, cards2, foggy, expected):
        self.assertEqual(cards_util.is_stronger(cards1, cards2, foggy), expected)

    @parameterized.expand(paras)
    def test_is_stronger_anti_symmetric(self, cards1, cards2, foggy, expected):
        '''if cards1 is expected to be stronger than cards2, 
        than cards2 is not expected to be stronger than cards1'''
        self.assertEqual(cards_util.is_stronger(cards2, cards1, foggy), not expected)

    @parameterized.expand(paras)
    def test_is_stronger_irreflexive(self, cards1, cards2, foggy, expected):
        '''is_stronger is irreflexive, that is 
            cards > cards 
        should never hold for any set of cards.'''
        self.assertEqual(cards_util.is_stronger(cards1, cards1, True), False)
        self.assertEqual(cards_util.is_stronger(cards1, cards1, False), False)
        self.assertEqual(cards_util.is_stronger(cards2, cards2, True), False)
        self.assertEqual(cards_util.is_stronger(cards2, cards2, False), False)        

#if __name__ == '__name__':
 #   unittest.main()