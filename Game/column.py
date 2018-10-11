from Game.card import *

class Column:

    def __init__(self, number):
        # Number of remaining cards to draw
        self.nb_todraw = number+1
        # List of cards of the column
        self.cards = []

    def need_reveal(self):
        """
        Checks if a new card needs to be revealed
        """
        return (not self.cards) and (self.nb_todraw > 0)

    def is_empty(self):
        """
        Checks if a column is fully empty.
        """
        return (not self.cards) and (self.nb_todraw == 0)

    def same_color(self, card1, card2):
        """
        Checks if two cards have the same color
        :param card1: (Card) first card
        :param card2: (Card) second card
        """
        if (card1.color in REDS and card2.color in REDS): return True
        if (card1.color in BLACKS and card2.color in BLACKS): return True

        return False

    def can_add(self, card):
        """
        Checks if a given card can be added to the column
        :param card: (Card) card to add
        """
        if not self.cards:
            if card.rank == KING: return True
            else : return False

        top_card = self.cards[-1]
        if card.rank != top_card.rank-1: return False
        if self.same_color(top_card, card): return False

        return True

    def can_remove(self, number):
        """
        Checks if a given number of cards can be removed from the column
        :param number: (int) the number of cards to remove
        """
        return len(self.cards) >= number

    def add_cards(self, cards):
        """
        Add a list of cards to the column
        :param cards: (list (Card)) the list of cards to add
        """
        for card in cards:
            self.cards.append(card)

    def reveal_card(self, card):
        """
        Reveals a new card in the column
        :param card: (Card) the card to reveal
        """
        self.nb_todraw -= 1
        self.add_cards([card])

    def remove_cards(self, number):
        """
        Removes a given number of cards from the column
        :param number: (int) the number of cards to remove
        """
        cards = []
        for i in range(number):
            cards.append(self.cards.pop())
        cards.reverse()

        return cards
