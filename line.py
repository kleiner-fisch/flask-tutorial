

class Line:

    def __init__(self, p0, p1, id=None, won_by=None):
        self.sides = {p0:[], p1:[]}
        self.won_by = won_by
        self.id=id

    def remove_card(self, card):
        for side in self.sides.values():
            if card in side:
                side.remove(card)
                return True
        return False
    
    def get_all_cards(self):
        return sum(self.sides.values(), [])
    
    def contains(self, card):
        '''checks if the given card has been played somewhere in this line'''
        return card in self.get_all_cards()
    
    def is_open(self):
        return self.won_by == None
    
    def __repr__(self) -> str:
        return repr({'won_by':self.won_by, 'sides': repr(self.sides)})
    