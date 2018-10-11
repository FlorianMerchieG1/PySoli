from solitaire_engine import *

if __name__ == '__main__':
    solitaire = Solitaire_Engine()
    solitaire.render()
    for i in solitaire.actions_dict:
        print(solitaire.actions_dict[i])
    solitaire.play(rd.randint(0, len(solitaire.actions_dict)-1))
    solitaire.render()
    for i in solitaire.actions_dict:
        print(solitaire.actions_dict[i])