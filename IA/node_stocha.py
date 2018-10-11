from __future__ import division
import numpy as np

class Node_Stocha:
    """
    Class defining a Node for a stochastic Monte Carlo Tree Search.
    """

    def __init__(self, game, parent=None, action=-1):
        """
        Creates a new Node_Stocha object
        :param game: (Game) Instance of a stochastic game
        :param parent: (Node_Stocha) Parent node
        :param action: (int) Previous action
        """
        # Parent node
        self.parent = parent
        # Children table
        self.children = dict()
        # Game interface
        self.game = game
        # Total number of visits
        self.n_visits = 0
        # Total reward
        self.total_reward = 0
        # Total squared reward
        self.total_sqr_reward = 0
        # Action leading from parent to the node
        self.action = action
        # List of legal actions
        self.legal_actions = game.legal_actions()

    def add_child(self, child, action):
        """
        Adds a new child to the list of children of a given action
        :param child: (Node_Stocha) child to add
        :param action: (int) action that lead to the child
        :return: the added child
        """
        if action not in self.children:
            self.children[action] = []
        self.children[action].append(child)
        return child

    def nb_children(self, action):
        """
        Retrieves the number of children of a given action
        :param action: (int) the action for which the number of children is required
        """
        if action in self.children: return len(self.children[action])
        else: return 0

    def update_node(self, reward):
        """
        Updates the variables of a node after a playout
        :param reward: (float) the reward of the playout
        """
        self.total_reward += reward
        self.total_sqr_reward += reward ** 2
        self.n_visits += 1

    def max_children(self, action, sampling_width):
        """
        Retrieves the maximum number of children for a given action and sampling width
        :param action: (int) action for which the information is required
        :param sampling_width: (int) sampling width of the MCTS
        """
        if self.game.chance_action(action): return sampling_width
        else: return 1

    def depth(self):
        """
        Retrieves the depth of a node
        """
        if self.parent is None: return 1 + self.parent.depth()
        else: return 0