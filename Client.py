import Requete
import time

class client():

    def __init__(self):
        self.on = False
        self.requetes = 0

    def envoie_requetes(self):
        while self.on:
            print("envoie des requêtes")
            self.requetes += 1
            time.sleep(0.5)