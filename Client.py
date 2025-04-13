from Requete import Requete
from Echeancier import Echeancier, Evenement as Ev
from Routeur import Routeur
import random

class Client():

    def __init__(self, routeur : Routeur, lambda_client, echeancier : Echeancier):
        self.lambda_client = lambda_client
        self.routeur = routeur
        self.echeancier = echeancier
        self.on = True
        self.requetes_envoyees = 0
        self.planifier_prochaine_requete()
    
    def planifier_prochaine_requete(self):
        if self.on:
            temps_prochaine_requete = self.echeancier.temps_actuel + random.expovariate(self.lambda_client)
            self.echeancier.ajouter_evenement(temps_prochaine_requete, Ev.NR, self)
    
    def envoie_requete(self):
        requete = random.choice(list(Requete))
        self.routeur.ajoute_requete(requete)
        self.requetes_envoyees += 1
        self.planifier_prochaine_requete()
