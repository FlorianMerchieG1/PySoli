from __future__ import division
from Game.solitaire_engine import *
from IA.mcts_stocha import *
import threading
import time
import numpy as np
import pandas as pd

NB_THREAD = 2

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter, solitaire):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.solitaire = solitaire
        self.actions = None
        self.probas = None
    def run(self):
        print ("Starting " + self.name)
        # Get lock to synchronize threads
        mcts = Mcts_Stocha(self.solitaire)
        self.actions, self.probas = mcts.tree_search(30, 10)


def write_csv(file, dataframe):
    return 0


if __name__ == '__main__':

    solitaire = Solitaire_Engine()
    header = solitaire.get_header()
    samples = []
    data = pd.DataFrame(columns=header)
    while not solitaire.is_over():

        threads = []
        solitaire.render()
        for i in solitaire.actions_dict:
            print(solitaire.actions_dict[i])
        for i in range(NB_THREAD):
            # Add threads to thread list
            threads.append(myThread(1, "Thread-"+str(i), 1, solitaire))
            threads[i].start()

        # Wait for all threads to complete
        for t in threads:
            t.join()
        print("Exiting Threads")
        actions = threads[0].actions
        probas = np.zeros(len(actions))
        for thread in threads:
            probas += thread.probas
        probas /= 2

        full_proba = []
        for i in range(list(solitaire.action_index_name.keys())[-1]):
            if i in actions: full_proba[i] = probas[actions.index(i)]
            else: full_proba[i] = 0
        samples.append(solitaire.get_state() + full_proba)

        action = np.random.choice(actions, p=probas)
        if (int(action)) < len(solitaire.actions_dict):
            solitaire.chance_action(int(action))
            solitaire.play(int(action))
        else:
            print("Invalid Input !")

    for i in range(len(samples)):
        samples[i].append(solitaire.score)
        data.append(samples[i])
    write_csv("data.csv", data)
