from Game.card import *

class Heap:

    def __init__(self):
        # List of cards of the heap
        self.cards = []

    def is_complete(self):
        """
        Checks if the heap is complete
        """
        return self.cards[-1] == KING if self.cards else False

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
        Checks if a card can be added to the heap
        :param card: (Card) card to add
        """

        if not self.cards:
            if card.rank == ACE: return True
            else: return False

        top_card = self.cards[-1]
        if card.rank != top_card.rank+1: return False
        if card.color != top_card.color: return False

        return True

    def can_remove(self):
        """
        Checks if a card can be removed from the heap
        """
        return len(self.cards) > 0

    def add_card(self, card):
        """
        Adds a new card to the heap
        :param card: (Card) card to add
        """
        self.cards.append(card)

    def remove_card(self):
        """
        Removes a card from the heap
        """
        return self.cards.pop()