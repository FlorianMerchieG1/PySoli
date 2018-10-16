from IA.node_stocha import *
import random as rd
import math
import copy

GAMMA = 0.9
FACTOR_THRESHOLD = 0.01

class Mcts_Stocha:
    """
    Class defining a stochastic Monte Carlo Tree Search
    """

    def __init__(self, game, c=0.1, d=10000):
        """
        Creates a new MCTS object for stochastic games
        :param game: (Game) the game to solve
        :param c: (float) first UCB constant
        :param d: (float) second UCB constant
        """
        self.root = Node_Stocha(game)
        self.c = c
        self.d = d

    def compute_ucb(self, node, action):
        """
        Computes the UCB score of single-player games.
        :param node: (Node_Stocha) node for which the score is required
        :param action: (int) action for which the score is required
        """
        reward, sqr_reward, total_visits = 0.0, 0.0, 0
        nodes_list = node.children[action]
        for child in nodes_list:
            reward += child.total_reward
            sqr_reward += child.total_sqr_reward
            total_visits += child.n_visits

        return (reward / total_visits) + \
               self.c * np.sqrt(np.log2(node.n_visits) / total_visits) + \
               np.sqrt((sqr_reward - total_visits * ((reward/total_visits) ** 2) + self.d) / total_visits)

    def select(self, node, sampling_width):
        """
        Performs selection step of a MCTS iteration
        :param node: (Node_Stocha) node at which selection is performed
        :param sampling_width: (int) sampling width of the MCTS
        :return: A tuple (Node_Stocha, action) corresponding to the selection
        """
        next_action, next_child, index = -1, -1, -1
        unsampled_actions = []

        # If at least one action has not been sampled yet, randomly select one of them
        if len(node.children.keys()) < len(node.legal_actions):
            for action in node.legal_actions:
                if action not in node.children:
                    unsampled_actions.append(action)

            index = rd.randint(0, len(unsampled_actions)-1)
            next_action = unsampled_actions[index]

            return node, next_action

        max_ucb, cur_ucb = -math.inf, 0
        # If terminal node, notice it
        if not node.legal_actions: return (node, next_action)

        # If all actions have been sampled, select the best one according to their score
        for action in node.legal_actions:
            cur_ucb = self.compute_ucb(node, action)
            if cur_ucb > max_ucb:
                max_ucb = cur_ucb
                next_action = action

        # If the sampling width for the action is reached, randomly select one of the children.
        if len(node.children[next_action]) == node.max_children(next_action, sampling_width):
            next_child = rd.randint(0, node.max_children(next_action, sampling_width)-1)
            return self.select(node.children[next_action][next_child], sampling_width)
        # If at least one more child can be created, performs a transition according to the action.
        else:
            return node, next_action

    def expand(self, node, action):
        """
        Performs the expansion step of a MCTS iteration
        :param node: (Node_Stocha) node at which expansion is performed
        :param action: (int) action with which expansion is performed
        :return: the child node created for expansion
        """
        game_copy = copy.deepcopy(node.game)
        game_copy.play(action)
        child = node.add_child(Node_Stocha(game_copy, node, action), action)
        return child

    def simulation(self, game):
        """
        Performs a playout for a given game
        :param game: (Game) game to play
        :return: the reward associated to the playout
        """
        reward = 0
        time = 0
        while not game.is_over() and GAMMA ** time > FACTOR_THRESHOLD:
            actions = game.legal_actions()
            next_action = rd.choice(actions)
            game.play(next_action)
            reward += (GAMMA ** time) * game.get_reward()
            time += 1

        return reward

    def backpropagate(self, node, reward):
        """
        Performs backpropagation step of a MCTS iteration
        :param node: (Node_Stocha) node at which backpropagation is performed
        :param reward: (float) reward of the backpropagation
        """

        node.update_node(reward)
        if node.parent is not None: self.backpropagate(node.parent, reward)

    def tree_search(self, nb_trajectories, sampling_width):
        """
        Performs a MCTS
        :param nb_trajectories: (int) number of simulations to perform in the MCTS
        :param sampling_width: (int) sampling width of the MCTS
        :return: the policy derived by the MCTS for the current game
        """
        policy_actions = []
        policy_probabs = []
        ucb_scores = []

        # Build search tree
        for i in range(nb_trajectories):
            node, action = self.select(self.root, sampling_width)
            if action == -1: break
            child = self.expand(node, action)
            reward = self.simulation(copy.deepcopy(child.game))
            self.backpropagate(child, reward)

        # Retrieving of the policy
        ucb_scores.clear()
        max_ucb = 0
        for action in self.root.legal_actions:
            cur_ucb = self.compute_ucb(self.root, action)
            max_ucb += cur_ucb
            ucb_scores.append(cur_ucb)

        for i in range(len(self.root.legal_actions)):
            policy_actions.append(self.root.legal_actions[i])
            policy_probabs.append(ucb_scores[i] / max_ucb)

        return policy_actions, np.array(policy_probabs)