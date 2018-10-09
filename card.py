ACE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6
SEVEN = 7
EIGHT = 8
NINE = 9
TEN = 10
JACK = 11
QUEEN = 12
KING = 13

CARDS = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]

CLUBS = 'C'
DIAMONDS = 'D'
HEARTS = 'H'
SPLADES = 'S'

COLORS = [CLUBS, DIAMONDS, HEARTS, SPLADES]
REDS = [DIAMONDS, HEARTS]
BLACKS = [CLUBS, SPLADES]

class Card:

    def __init__(self, color, rank):
        self.color = color
        self.rank = rank