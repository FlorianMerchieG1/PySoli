from __future__ import division
from Game.solitaire_engine import *
from IA.mcts_stocha import *

if __name__ == '__main__':
    solitaire = Solitaire_Engine()
    while not solitaire.is_over():
        solitaire.render()
        for i in solitaire.actions_dict:
            print(solitaire.actions_dict[i])
        mcts = Mcts_Stocha(solitaire)
        actions, probas = mcts.tree_search(500, 10)
        action = rd.choice(actions, p=probas)
        if (int(action)) < len(solitaire.actions_dict):
            solitaire.chance_action(int(action))
            solitaire.play(int(action))
        else:
            print("Invalid Input !")

