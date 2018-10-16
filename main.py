from __future__ import division
from Game.solitaire_engine import *
from IA.mcts_stocha import *
import threading
import time
import numpy as np
import pandas as pd
import os.path
from multiprocessing import Process, Queue, Pipe

NB_THREAD = 1
NB_TRAJECTORIES = 50
SAMPLING_WIDTH = 10
NB_GAMES = 10

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
        mcts = Mcts_Stocha(self.solitaire)
        self.actions, self.probas = mcts.tree_search(NB_TRAJECTORIES, SAMPLING_WIDTH)

def process_function(queue, solitaire):
    mcts = Mcts_Stocha(solitaire)
    actions, probas = mcts.tree_search(int(NB_TRAJECTORIES/NB_THREAD), SAMPLING_WIDTH)
    queue.put([actions, probas])


def write_csv(file, dataframe):
    """
    Write data collected from simulations into a csv file
    :param file: (string) path of the file
    :param dataframe: (Dataframe) collected data
    """
    print(dataframe)
    dataframe.to_csv(file, sep=';')

def agent():
    """
    Generate data for an AI to learn how to play solitaire
    """
    data = []
    for i in range(NB_GAMES):
        solitaire = Solitaire_Engine()
        samples = []
        while not solitaire.is_over():
            print("Game "+ str(i+1)+ " - Turn "+str(solitaire.time+1))

            if len(solitaire.actions_dict):
                processes = []
                queues = []
                elems = []
                #solitaire.render()
                #for i in solitaire.actions_dict:
                #    print(solitaire.actions_dict[i])
                for j in range(NB_THREAD):
                    # Add threads to thread list
                    #threads.append(myThread(1, "Thread-" + str(i), 1, copy.deepcopy(solitaire)))
                    queues.append(Queue())
                    processes.append(Process(target=process_function, args=(queues[j], copy.deepcopy(solitaire))))
                    #threads[i].start()
                    processes[j].start()

                # Wait for all threads to complete
                for j in range(NB_THREAD):
                    processes[j].join()
                    elems.append(queues[j].get())
                actions = elems[0][0]
                probas = np.zeros(len(actions))
                for j in range(NB_THREAD):
                    probas += elems[j][1]
                probas /= NB_THREAD
            else:
                actions = list(solitaire.actions_dict.keys())
                probas = [1]

            full_proba = []
            for j in range(len(solitaire.action_index_name.keys())):
                if j in actions:
                    full_proba.append(probas[actions.index(j)])
                else:
                    full_proba.append(0)
            state, _ = solitaire.get_state()
            samples.append(state + full_proba)

            action = np.random.choice(actions, p=probas)
            if (int(action)) < len(solitaire.action_index_name):
                solitaire.chance_action(int(action))
                solitaire.play(int(action))
            else:
                print("Invalid Input !")

        if (solitaire.is_won()): print("Won !")
        else: print("Lost")

        for j in range(len(samples)):
            samples[j].append(solitaire.score)
            data.append(samples[j])

    solitaire = Solitaire_Engine()
    data = pd.DataFrame(data, columns=solitaire.get_header())
    write_csv("data.csv", data)

def human():
    """
    Play a solitaire in the prompt with human input
    """
    solitaire = Solitaire_Engine()
    while not solitaire.is_over():
        print(solitaire.states_stack)
        solitaire.render()
        for i in solitaire.actions_dict:
            print(str(solitaire.actions_dict[i]) + " - " + str(i))
        action = input("Enter an action number: ")
        if (int(action)) < len(solitaire.action_index_name):
            start = time.time()
            solitaire.play(int(action))
            print(str(time.time()-start))
        else:
            print("Invalid Input !")


if __name__ == '__main__':
    agent()

