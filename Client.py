import Requete
import time

class client():

    def __init__(self):
        self.on = False

    def envoie_requetes(self):
        while self.on:
            print("envoie des requêtes")
            time.sleep(0.5)