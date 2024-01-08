import operator
from .line import Line


class Game:

    def __init__(self, p1, p2, game_id=None, current_player=None,
                 p1_hand=[], p2_hand=[],
                 claim=dict(), unresolved_scout=False,
                 winner=None, public_cards=[],
                 lines = []):
        self.game_id = game_id
        self.p1 = p1
        self.p2 = p2
        self.current_player = current_player or p1
        self.hands = {self.p1: p1_hand, self.p2 : p2_hand}
        self.claim = claim
        self.unresolved_scout = unresolved_scout
        self.lines = lines or [Line(sides={p1:[], p2:[]}) for x in range(9)]
        self.public_cards = public_cards
        self.winner = winner


    def get_hand(self, player_id):
        return self.hands[player_id]
    

    def __repr__(self) -> str:
        clsname = self.__class__.__name__
        return '{classname}({p1}, {p2}, {game_id}, {current_player}, {p1_hand}, {p2_hand}, \
            {claim}, {scout}, {winner}, {public_cards}, {lines})'.format(\
                classname=clsname, p1=self.p1, p2=self.p2, game_id= self.game_id, current_player=self.current_player,
                     p1_hand=self.hands[self.p1], p2_hand=self.hands[self.p2],
                     claim=self.claim, scout=self.unresolved_scout,
                     public_cards=self.public_cards,
                     winner=self.winner,
                     lines=repr(self.lines))
    
    def __eq__(self, other) -> bool:
        fetcher = operator.attrgetter("p1", "p2", "game_id", "current_player", "hands", "claim", "unresolved_scout", "public_cards", "winner", "lines")
        try:
            return self is other or fetcher(self) == fetcher(other)
        except AttributeError:
            return False
    