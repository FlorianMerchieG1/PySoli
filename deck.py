import random as rd
from card import *

class Deck:

    def __init__(self):
        self.cards = []
        for color in COLORS:
            for rank in CARDS:
                self.cards.append(Card(color, rank))
        rd.shuffle(self.cards)

    def draw(self, shuffle=False):
        if shuffle:
            rd.shuffle(self.cards)
        return self.cards.pop()