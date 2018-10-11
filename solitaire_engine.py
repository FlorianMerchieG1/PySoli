import copy
from deck import *
from column import *
from heap import *

NB_CARDS_SUBDECK = 24
NB_HEAPS = 4
NB_COLUMNS = 7

ACTIONS = ['draw', 'deck-heap', 'deck-col', 'col-heap', 'heap-col', 'col-col']

"""
Actions:
- draw sud-deck
- column to heap
    - X nb heaps
    - X nb cols
- heap to column
    - X nb heaps
    - X nb cols
- sub-deck to column
    - X nb cols
- sub-deck to heap 
    - X nb heaps
- column to column 
    - X nb cols
    - X nb other cols
    - X nb cards col
"""

class Solitaire_Engine:

    def __init__(self):
        # Main deck where all cards are drawn
        self.main_deck = Deck()
        # Upper-left sub-deck
        self.sub_deck = []
        self.sub_deck_index = []
        for i in range(NB_CARDS_SUBDECK):
            self.sub_deck.append(self.main_deck.draw())
        # Heaps init
        self.heaps = []
        for i in range(NB_HEAPS):
            self.heaps.append(Heap())
        # Columns init
        self.columns = []
        for i in range(NB_COLUMNS):
            self.columns.append(Column(i))
            self.columns[i].reveal_card(self.main_deck.draw())
        # Actions dictionary
        self.actions_dict = dict()
        self.legal_actions()

    def is_over(self):
        return self.is_won() or self.is_lost()

    def is_won(self):
        """
        Checks if the game is won.
        """
        for heap in self.heaps:
            if not heap.is_complete(): return False

        return True

    def is_lost(self):
        """
        Checks if a game is lost.
        """
        # Copy current state of sub-deck draw
        sub_index_copy = copy.deepcopy(self.sub_deck_index)
        sub_index_list = []

        # Game over only if draw is the only possible action
        if len(self.actions_dict) == 1 and self.can_draw():
            # For each draw of the sub-deck, check if a card can be moved
            while self.sub_deck_index not in sub_index_list:
                self.draw()
                sub_index_list.append(self.sub_deck_index)
                for heap in range(NB_HEAPS):
                    if self.can_deck_to_heap(heap):
                        self.sub_deck_index = sub_index_copy
                        return False
                for col in range(NB_COLUMNS):
                    if self.can_deck_to_column(col):
                        self.sub_deck_index = sub_index_copy
                        return False

        self.sub_deck_index = sub_index_copy
        return True

    def can_draw(self):
        """
        Checks a if a draw can be performed
        """
        return len(self.sub_deck) > 0

    def draw(self):
        """
        Draw cards from the sub-deck
        """
        if not self.can_draw(): return False

        if not self.sub_deck_index:
            start = 0
        else:
            start = self.sub_deck_index[-1] + 1

        if start > len(self.sub_deck):
            self.sub_deck_index = [i for i in range(3)]
        else:
            end = min(start+3, len(self.sub_deck))
            self.sub_deck_index = [i for i in range(start, end)]

    def can_deck_to_heap(self, heap):
        """
        Checks if the card from the deck can be added to a heap
        :param heap: (int) Number of the heap where to move the card
        """
        if not self.can_draw(): return False
        if not self.sub_deck_index: return False

        index = self.sub_deck_index[-1]
        card = self.sub_deck[index]

        if not self.heaps[heap].can_add(card): return False

        return True

    def deck_to_heap(self, heap):
        """
        Moves the top drawn of the deck to a given heap
        :param heap: (int) number of the heap where to move the card
        """
        if not self.can_deck_to_heap(heap): return False

        index_heap = self.sub_deck_index.pop()
        card = self.sub_deck.pop(index_heap)
        self.heaps[heap].add_card(card)

    def can_deck_to_column(self, col):
        """
        Checks if the card from the deck can be added to a column
        :param heap: (int) Number of the column where to move the card
        """
        if not self.can_draw(): return False
        if not self.sub_deck_index: return False

        index = self.sub_deck_index[-1]
        card = self.sub_deck[index]

        if not self.columns[col].can_add(card): return False

        return True

    def deck_to_column(self, col):
        """
        Moves the top drawn of the deck to a given column
        :param col: (int) index of the column where to move the card
        """
        if not self.can_deck_to_column(col): return

        index_heap = self.sub_deck_index.pop()
        card = self.sub_deck.pop(index_heap)
        self.columns[col].add_cards(list(card))

    def can_column_to_heap(self, col, heap):
        """
        Checks if the top card of a column can be added to a heap
        :param col: (int) index of the column
        :param heap: (int) index of the heap
        """
        if not self.columns[col].can_remove(1): return False

        card = self.columns[col].cards[-1]
        if not self.heaps[heap].can_add(card): return False

        return True

    def column_to_heap(self, col, heap):
        """
        Moves the top card of a column to a heap
        :param col: (int) index of the column
        :param heap: (int) index of the heap
        """
        column = self.columns[col]
        if not self.can_column_to_heap(col, heap): return

        cards = column.remove_cards(1)
        self.heaps[heap].add_card(cards[0])

        # Check if a new card has to be revealed
        if column.need_reveal and (not column.is_empty()):
            column.reveal_card(self.main_deck.draw(True))

    def can_heap_to_column(self, heap, col):
        """
        Checks if a card can be moved from a heap to a column
        :param heap: (int) index of the heap
        :param col: (int) index of the column
        """
        if not self.heaps[heap].can_remove(): return False

        card = self.heaps[heap].cards[-1]
        if not self.columns[col].can_add(card): return False

        return True

    def heap_to_column(self, heap, col):
        """
        Moves a card from a heap to a column
        :param heap: (int) index of the heap
        :param col: (int) index of the column
        """
        card = self.heaps[heap].remove_card()
        self.columns[col].add_cards(list(card))

    def can_column_to_column(self, col1, col2, nb_cards):

        if not self.columns[col1].can_remove(nb_cards): return False

        column_copy = copy.deepcopy(self.columns[col1])
        cards = column_copy.remove_cards(nb_cards)
        if not self.columns[col2].can_add(cards[-1]): return False

        return True

    def column_to_column(self, col1, col2, nb_cards):
        """
        Moves a number of card from a column to another
        :param col1: (int) index of the first column
        :param col2: (int) index of the second column
        :param nb_cards: (int) number of cards to move
        """
        column = self.columns[col1]
        cards = column.remove_cards(nb_cards)
        self.columns[col2].add_cards(cards)

        # Check if a new card has to be revealed
        if column.need_reveal and (not column.is_empty()):
            column.reveal_card(self.main_deck.draw(True))

    def legal_actions(self):
        actions = []
        index_action = 0
        self.actions_dict.clear()
        table = self.actions_dict

        # Check draw
        if self.can_draw():
            table[index_action] = (ACTIONS[0],[])
            actions.append(index_action)
            index_action += 1
        # Check deck-heap
        for heap in range(NB_HEAPS):
            if self.can_deck_to_heap(heap):
                table[index_action] = (ACTIONS[1], [heap])
                actions.append(index_action)
                index_action += 1
        # Check deck-column
        for col in range(NB_COLUMNS):
            if self.can_deck_to_column(col):
                table[index_action] = (ACTIONS[2], [col])
                actions.append(index_action)
                index_action += 1

        for heap in range(NB_HEAPS):
            for col1 in range(NB_COLUMNS):
                # Check col-heap
                if self.can_column_to_heap(col1, heap):
                    table[index_action] = (ACTIONS[3], [col1, heap])
                    actions.append(index_action)
                    index_action += 1
                # Check heap-col
                if self.can_heap_to_column(heap, col1):
                    table[index_action] = (ACTIONS[4], [heap, col1])
                    actions.append(index_action)
                    index_action += 1
                if heap == 0:
                    for col2 in range(NB_COLUMNS):
                        # Check col-col
                        if col1 != col2:
                            max_cards = len(self.columns[col1].cards)
                            for nb_cards in range(1, max_cards+1):
                                if self.can_column_to_column(col1, col2,
                                                             nb_cards):
                                    table[index_action] = (ACTIONS[5],
                                                           [col1, col2,
                                                            nb_cards])
                                    actions.append(index_action)
                                    index_action += 1
        return actions

    def play(self, action):
        value = self.actions_dict[action]
        name = value[0]
        args = value[1]
        if name == ACTIONS[0]:
            self.draw()
        elif name == ACTIONS[1]:
            self.deck_to_heap(args[0])
        elif name == ACTIONS[2]:
            self.deck_to_column(args[0])
        elif name == ACTIONS[3]:
            self.column_to_heap(args[0], args[1])
        elif name == ACTIONS[4]:
            self.heap_to_column(args[0], args[1])
        else:
            self.column_to_column(args[0], args[1], args[2])
        self.legal_actions()

    def render(self):

        print("State:")
        print("Draw deck:")
        string = str(len(self.sub_deck))+" cards - "+\
                 " ".join(str(x) for x in self.sub_deck_index)
        if self.sub_deck_index:
            card = self.sub_deck[self.sub_deck_index[-1]]
            string += " - "+str(card.rank)+card.color
        print(string)
        print("Heaps:")
        string = ""
        for heap in self.heaps:
            if heap.cards:
                card = heap.cards[-1]
                string += str(card.rank)+card.color+" "
            else:
                string += "-1 "
        print(string)
        print("Columns:")
        for column in self.columns:
            string = ""
            string += ("? " * column.nb_todraw)
            for card in column.cards:
                string += str(card.rank)+card.color+" "
            print(string)

