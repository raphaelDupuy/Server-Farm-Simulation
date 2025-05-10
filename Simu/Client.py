from Echeancier import Echeancier, Ev
from Routeur import Routeur
import random

class Client:
    def __init__(self, routeur: Routeur, lambda_client: float, echeancier: Echeancier):
        self.lambda_client = lambda_client
        self.routeur = routeur
        self.echeancier = echeancier
        self.on = True
        self.requetes_envoyees = 0
        self.planifier_prochaine_requete()

    def planifier_prochaine_requete(self):
        if self.on:
            t_next = self.echeancier.temps_actuel + random.expovariate(self.lambda_client)
            self.echeancier.ajouter_evenement(t_next, Ev.NR, None)

    def envoie_requete(self):
        from Requete import Requete as Rq, Requetes
        rq = Rq(random.randint(0, self.routeur.nb_groupes-1))
        self.routeur.ajoute_requete(rq)
        self.requetes_envoyees += 1
        self.planifier_prochaine_requete()