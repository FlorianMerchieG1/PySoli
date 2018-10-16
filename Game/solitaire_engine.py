from __future__ import division
import copy
from Game.deck import *
from Game.column import *
from Game.heap import *

NB_CARDS_SUBDECK = 24
NB_HEAPS = 4
NB_COLUMNS = 7

IN_HEAP = 'heap'
IN_DECK = 'deck'
IN_COL = 'col'
UNDRAWN = 'undraw'

ACTIONS = ['draw', 'deck-heap', 'deck-col', 'col-heap', 'heap-col', 'col-col']

class Solitaire_Engine:

    def __init__(self):
        # State values dictionary
        self.state_dict = dict()
        for i in range(33):
            if i <= 6:
                self.state_dict[IN_COL + str(i)] = i
            elif i == 7:
                self.state_dict[IN_HEAP] = i
            elif i == 8:
                self.state_dict[UNDRAWN] = i
            else:
                self.state_dict[IN_DECK + str(i-9)] = i
        # State information for each card
        self.cards_state = dict()
        # Main deck where all cards are drawn
        self.main_deck = Deck()
        # Upper-left sub-deck
        self.sub_deck = []
        self.sub_deck_index = []
        for i in range(NB_CARDS_SUBDECK):
            card = self.main_deck.draw()
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_DECK + str(i)]
            self.sub_deck.append(card)
        # Heaps init
        self.heaps = []
        for i in range(NB_HEAPS):
            self.heaps.append(Heap())
        # Columns init
        self.columns = []
        for i in range(NB_COLUMNS):
            self.columns.append(Column(i))
            card = self.main_deck.draw()
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(i)]
            self.columns[i].reveal_card(card)
        # Reward for scoring
        self.reward = 0
        self.time = 0
        self.score = 0
        # States stack for avoiding cycles
        _, state = self.get_state()
        self.states_stack = [state]
        # Actions dictionary
        self.actions_dict = dict()
        self.legal_actions()
        self.action_index_name = dict()
        self.index_action_to_name()

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
        if len(self.actions_dict) == 0: return True

        else: return False

    def get_reward(self):
        """
        Retrieves the result of the game
        """
        return self.reward

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
            self.sub_deck_index = [i for i in range(min(3, len(self.sub_deck)))]
        else:
            start = self.sub_deck_index[-1] + 1
            if start >= len(self.sub_deck):
                self.sub_deck_index = [i for i in range(min(3, len(self.sub_deck)))]
            else:
                end = min(start+3, len(self.sub_deck))
                self.sub_deck_index = [i for i in range(start, end)]

        self.reward = 0

    def can_deck_to_heap(self, heap, nb_draw):
        """
        Checks if the card from the deck can be added to a heap
        :param heap: (int) Number of the heap where to move the card
        :param nb_draw: (int) Number of times to draw before actually playing
        """
        game_copy = copy.deepcopy(self)
        if not game_copy.can_draw(): return False
        for i in range(nb_draw):
            game_copy.draw()

        if not game_copy.sub_deck_index: return False

        index = game_copy.sub_deck_index[-1]
        card = game_copy.sub_deck[index]

        if not game_copy.heaps[heap].can_add(card): return False

        return True

    def deck_to_heap(self, heap, nb_draw):
        """
        Moves the top drawn of the deck to a given heap
        :param heap: (int) number of the heap where to move the card
        :param nb_draw: (int) Number of times to draw before actually playing
        """
        if not self.can_deck_to_heap(heap, nb_draw): return False

        for i in range(nb_draw):
            self.draw()

        index_heap = self.sub_deck_index.pop()
        card = self.sub_deck.pop(index_heap)
        self.heaps[heap].add_card(card)

        # State update for moved card
        self.cards_state[(card.rank, card.color)] = self.state_dict[IN_HEAP]
        while index_heap < len(self.sub_deck):
            card = self.sub_deck[index_heap]
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_DECK + str(index_heap)]
            index_heap += 1

        # Reward update
        self.reward = 10

    def can_deck_to_column(self, col, nb_draw):
        """
        Checks if the card from the deck can be added to a column
        :param heap: (int) Number of the column where to move the card
        :param nb_draw: (int) Number of times to draw before actually playing
        """
        game_copy = copy.deepcopy(self)
        if not game_copy.can_draw(): return False
        for i in range(nb_draw):
            game_copy.draw()

        if not game_copy.sub_deck_index: return False

        index = game_copy.sub_deck_index[-1]
        card = game_copy.sub_deck[index]

        if not game_copy.columns[col].can_add(card): return False

        return True

    def deck_to_column(self, col, nb_draw):
        """
        Moves the top drawn of the deck to a given column
        :param col: (int) index of the column where to move the card
        :param nb_draw: (int) Number of times to draw before actually playing
        """
        if not self.can_deck_to_column(col, nb_draw): return
        for i in range(nb_draw):
            self.draw()

        index_heap = self.sub_deck_index.pop()
        card = self.sub_deck.pop(index_heap)
        self.columns[col].add_cards([card])

        # State update for moved card
        self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(col)]
        while index_heap < len(self.sub_deck):
            card = self.sub_deck[index_heap]
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_DECK + str(index_heap)]
            index_heap += 1

        # Reward update
        self.reward = 5

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
        # State update for moved card
        self.cards_state[(cards[0].rank, cards[0].color)] = self.state_dict[IN_HEAP]

        # Reward update
        self.reward = 10

        # Check if a new card has to be revealed
        if column.need_reveal():
            card = self.main_deck.draw(True)
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(col)]
            column.reveal_card(card)
            self.reward += 5

    def can_heap_to_column(self, heap, col):
        """
        Checks if a card can be moved from a heap to a column
        :param heap: (int) index of the heap
        :param col: (int) index of the column
        """
        if not self.heaps[heap].can_remove(): return False

        card = self.heaps[heap].cards[-1]
        # Useless to remove an Ace from the heap
        if card.rank == ACE: return False
        if not self.columns[col].can_add(card): return False

        return True

    def heap_to_column(self, heap, col):
        """
        Moves a card from a heap to a column
        :param heap: (int) index of the heap
        :param col: (int) index of the column
        """
        card = self.heaps[heap].remove_card()
        self.columns[col].add_cards([card])
        # State update for moved card
        self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(col)]

        # Reward update
        self.reward = -15

    def can_column_to_column(self, col1, col2, nb_cards):

        if not self.columns[col1].can_remove(nb_cards): return False

        column_copy = copy.deepcopy(self.columns[col1])
        cards = column_copy.remove_cards(nb_cards)
        if not self.columns[col2].can_add(cards[0]): return False

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
        # State update for moved cards
        for card in cards:
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(col2)]

        self.reward = 0

        # Check if a new card has to be revealed
        if column.need_reveal():
            card = self.main_deck.draw(True)
            self.cards_state[(card.rank, card.color)] = self.state_dict[IN_COL + str(col1)]
            column.reveal_card(card)
            self.reward += 5

    def legal_actions(self):
        """
        Retrieves all the legal actions of the current states.
        """
        index_action = 0
        self.actions_dict.clear()
        table = self.actions_dict

        cards_list = []
        nb_draw = 0
        game_copy = copy.deepcopy(self)
        if game_copy.sub_deck_index:
            card = game_copy.sub_deck[game_copy.sub_deck_index[-1]]
            cards_list.append(card)
        # For each configuration of the sub-deck, check possible actions
        if game_copy.sub_deck:
            while True:
                # Check deck-heap
                for heap in range(NB_HEAPS):
                    if game_copy.can_deck_to_heap(heap, 0):
                        table[index_action] = (ACTIONS[1], [heap, nb_draw])
                    index_action += 1

                # Check deck-column
                for col in range(NB_COLUMNS):
                    if game_copy.can_deck_to_column(col, 0):
                        table[index_action] = (ACTIONS[2], [col, nb_draw])
                    index_action += 1

                # Update sub-deck
                game_copy.draw()
                card = game_copy.sub_deck[game_copy.sub_deck_index[-1]]
                if card in cards_list: break
                cards_list.append(card)
                nb_draw += 1

        index_action = int(NB_CARDS_SUBDECK/3 +1) * NB_HEAPS + int(NB_CARDS_SUBDECK/3 +1) * NB_COLUMNS
        # Check col-heap
        for heap in range(NB_HEAPS):
            for col1 in range(NB_COLUMNS):
                if self.can_column_to_heap(col1, heap):
                    table[index_action] = (ACTIONS[3], [col1, heap])
                index_action += 1

        # Check heap-col
        for heap in range(NB_HEAPS):
            for col1 in range(NB_COLUMNS):
                if self.can_heap_to_column(heap, col1):
                    game_copy = copy.deepcopy(self)
                    game_copy.heap_to_column(heap, col1)
                    _, state = game_copy.get_state()
                    if state not in self.states_stack:
                        table[index_action] = (ACTIONS[4], [heap, col1])
                index_action += 1

        # Check col-col
        for col1 in range(NB_COLUMNS):
                for col2 in range(NB_COLUMNS):
                    if col1 != col2:
                        max_cards = len(self.columns[col1].cards)
                        max_nb_cards = -1
                        # Choose action with the most cards
                        for nb_cards in range(1, max_cards+1):
                            if self.can_column_to_column(col1, col2, nb_cards):
                                game_copy = copy.deepcopy(self)
                                game_copy.column_to_column(col1, col2, nb_cards)
                                _, state = game_copy.get_state()
                                if state not in self.states_stack:
                                    max_nb_cards = nb_cards
                        if max_nb_cards > -1:
                            table[index_action] = (ACTIONS[5],
                                                   [col1, col2, max_nb_cards])
                        index_action += 1

        return list(self.actions_dict.keys())

    def index_action_to_name(self):
        """
        Set the dictionary for the action names
        """
        index = 0
        for nb_draw in range(int(NB_CARDS_SUBDECK/3)+1):
            for i in range(NB_HEAPS):
                self.action_index_name[index] = 'deck-to-heap'+ str(i) + "-"+ str(nb_draw) + "draws"
                index += 1
            for i in range(NB_COLUMNS):
                self.action_index_name[index] = 'deck-to-col' + str(i) + "-"+ str(nb_draw) + "draws"
                index += 1
        for i in range(NB_HEAPS):
            for j in range(NB_COLUMNS):
                self.action_index_name[index] = 'col'+ str(j) + '-to-heap' + str(i)
                index += 1
        for i in range(NB_HEAPS):
            for j in range(NB_COLUMNS):
                self.action_index_name[index] = 'heap' + str(i) + '-to-col' + str(j)
                index += 1
        for i in range(NB_COLUMNS):
            for j in range(NB_COLUMNS):
                if i != j:
                    self.action_index_name[index] = 'col' + str(i) +\
                                                    '-to-col' + str(j)
                    index += 1

    def get_header(self):
        """
        Retrieves the header of the data file of a Solitaire game
        """
        header = []
        for color in COLORS:
            for rank in CARDS:
                header.append(str(rank)+color)
        for action in list(self.action_index_name.values()):
            header.append(action)
        header.append('reward')
        return header


    def play(self, action):
        """
        Plays an action
        :param action: (int) key of the action to play
        """
        value = self.actions_dict[action]
        name = value[0]
        args = value[1]
        if name == ACTIONS[0]:
            self.draw()
        elif name == ACTIONS[1]:
            self.deck_to_heap(args[0], args[1])
        elif name == ACTIONS[2]:
            self.deck_to_column(args[0], args[1])
        elif name == ACTIONS[3]:
            self.column_to_heap(args[0], args[1])
        elif name == ACTIONS[4]:
            self.heap_to_column(args[0], args[1])
        else:
            self.column_to_column(args[0], args[1], args[2])
        self.legal_actions()

        # Score updates
        self.score += self.reward
        self.time += 1
        # Stack update
        if name != ACTIONS[0]:
            _, state = self.get_state()
            self.states_stack.append(state)

    def chance_action(self, action):
        """
        Checks if an action involves randomness.
        :param action: The action to perform
        """
        game = copy.deepcopy(self)
        cards_before = len(game.main_deck.cards)
        game.play(action)
        cards_after = len(game.main_deck.cards)
        if cards_after >= cards_before: return False
        return True

    def get_state(self):
        """
        Provides an aggregation of the state of the game.
        """
        state = []
        for color in COLORS:
            for rank in CARDS:
                if (rank, color) in self.cards_state:
                    state.append(self.cards_state[(rank, color)])
                else:
                    state.append(self.state_dict[UNDRAWN])
        return state, ''.join(str(x) for x in state)

    def render(self):
        """
        Renders game in the console
        """
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
        print("Score")
        print(str(self.score))

