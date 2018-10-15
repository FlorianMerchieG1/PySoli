from __future__ import division
from Game.solitaire_engine import *
from IA.mcts_stocha import *
import threading
import time
import numpy as np
import pandas as pd
import os.path

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
        mcts = Mcts_Stocha(self.solitaire)
        self.actions, self.probas = mcts.tree_search(10, 10)


def write_csv(file, dataframe):
    """
    Write data collected from simulations into a csv file
    :param file: (string) path of the file
    :param dataframe: (Dataframe) collected data
    """
    print(dataframe)
    dataframe.to_csv(file, sep=';')


if __name__ == '__main__':

    solitaire = Solitaire_Engine()
    samples = []
    for t in range(2):
    #while not solitaire.is_over():

        threads = []
        #solitaire.render()
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
        for i in range(len(solitaire.action_index_name.keys())):
            if i in actions: full_proba.append(probas[actions.index(i)])
            else: full_proba.append(0)
        samples.append(solitaire.get_state() + full_proba)
        print(samples)

        action = np.random.choice(actions, p=probas)
        if (int(action)) < len(solitaire.action_index_name):
            solitaire.chance_action(int(action))
            solitaire.play(int(action))
        else:
            print("Invalid Input !")

    for i in range(len(samples)):
        samples[i].append(solitaire.score)

    data = pd.DataFrame(samples, columns=solitaire.get_header())
    write_csv("data.csv", data)
