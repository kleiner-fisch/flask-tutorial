

class Line:

    def __init__(self, sides, id=None, won_by=None):
        self.sides = sides
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
    
    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            result = self.id == other.id and self.won_by == other.won_by 
            return result and self.sides == other.sides
        else:
            return False
    
    def __repr__(self) -> str:
        clsname = self.__class__.__name__
        return '{}({}, {}, {})'.format(clsname, self.sides, self.id, self.won_by)
    