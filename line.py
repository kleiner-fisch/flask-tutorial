

class Line:

    def __init__(self, p0, p1):
        self.sides = {p0:[], p1:[]}
        self.won_by = None

    def remove_card(self, card):
        for side in self.sides.values():
            if card in side:
                side.remove(card)
                return True
        return False