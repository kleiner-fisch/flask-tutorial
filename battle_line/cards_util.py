
import itertools as iter


ALL_TACTICS = ["ALEXANDER", "DARIUS", "CAVALRY",  "SHIELD_BEARER", "FOG", "MUD", "SCOUT", "REDEPLOY", "DESERTER", "TRAITOR"]
GUILE_TACTICS= ["SCOUT", "REDEPLOY", "DESERTER", "TRAITOR"]
NUMBERS_CARDS = list(map(''.join, \
                    iter.product(["A", "B", "C", "D", "E", "F"], \
                    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])))

JOKERS = ["ALEXANDER", "CAVALRY", "DARIUS", "SHIELD_BEARER"]

def get_type(c):
    return c[0]

def get_number(c):
    return int(c[1:])

def _is_flush(cards):
    return len(set([get_type(c) for c in cards])) == 1

def _is_straight(cards):
    cards = sorted(cards, key=lambda c: get_number(c))
    result = True
    for i in range(len(cards) -1):
        result = result and get_number(cards[i]) +1 == get_number(cards[i+1])
    return result


def _all_same_number(cards):
    return len(set([get_number(c) for c in cards])) == 1


def _instantiate_jokers(cards, has_fog=False):
    '''returns a new list of cards, where all jokers have been instantiated to the best number cards possible'''
    possible_cards = _get_possible_hands(cards)
    return max(possible_cards, key=lambda cards: _convert(cards, has_fog)) 

def is_stronger(cards1, cards2, has_fog=False):
    '''returns whether cards1 is stronger than cards2
    - cards1 and cards2 do not contain any tactics, except possible jokers (FOG, MUD etc. have been filtered out)'''
    _cards1 = _instantiate_jokers(cards1, has_fog)
    _cards2 = _instantiate_jokers(cards2, has_fog)
    return _convert(_cards1, has_fog) > _convert(_cards2, has_fog)


def _get_possible_cards(joker):
    '''returns the cards the given joker can be instantiated to'''
    if joker in [ 'ALEXANDER', 'DARIUS']:
        return NUMBERS_CARDS
    elif joker == "CAVALRY":
        return list(map(''.join, \
                    iter.product(["A", "B", "C", "D", "E", "F"], ["8"])))
    elif joker == "SHIELD_BEARER":
        return list(map(''.join, \
            iter.product(["A", "B", "C", "D", "E", "F"], ["1", "2", "3"])))
    else:
        raise ValueError('unexpected jopker card: ' + joker)


def _get_possible_hands(cards):
    '''returns all possible hands for the given input. Depending on how many jokers <cards> has, this may be many 
        (in regular games up to ~6500, tests may cause more)'''
    jokers = [c for c in cards if c in JOKERS]
    partial_hand = [c for c in cards if c not in jokers]
    partial_hands = [partial_hand]
    for joker in jokers:
        partial_hands = iter.product(partial_hands, _get_possible_cards(joker))
        partial_hands = [l + [tail] for (l, tail) in partial_hands]
    return list(partial_hands)


def _convert(cards, has_fog=False):
    '''converts the given cards to an int value representing the strength'''
    if has_fog:
        return _sum_numbers(cards)
    is_flush = _is_flush(cards)
    is_straight = _is_straight(cards)
    all_same_number = _all_same_number(cards)
    if is_flush and is_straight:
        return 400 + _sum_numbers(cards)
    elif all_same_number:
        return 300 + _sum_numbers(cards)
    elif is_flush:
        return 200 + _sum_numbers(cards)
    elif is_straight:
        return 100 + _sum_numbers(cards)
    else:
        return _sum_numbers(cards)


def _sum_numbers(cards):
    return sum([get_number(c) for c in cards])


