from Routeur import Routeur
from Echeancier import Echeancier, Ev
from random import expovariate

default_lambda_serv = 14/20
class Serveur:
    def __init__(self, echeancier: Echeancier, lambda_serv: float, routeur, spe=None):
        self.echeancier = echeancier
        self.lambda_serv = lambda_serv
        self.spe = spe
        self.occupe = False
        self.routeur = routeur

    def traite(self, requete):
        if self.occupe:
            raise RuntimeError("Serveur occupé")
        if requete.get_value() != self.spe:
            raise RuntimeError(f"Mauvaise spécialisation: {requete.get_value()} != {self.spe}")
        self.occupe = True
        # enregistrement fin de traitement
        t_fin = self.echeancier.temps_actuel + expovariate(self.lambda_serv)
        self.echeancier.ajouter_evenement(t_fin, Ev.FT, (self, requete))
        self.echeancier.ajouter_historique(t_fin, requete.get_id(), 1)

    def fin_traitement(self):
        self.occupe = False
        # notifier routeur que ce serveur est libéré
        self.routeur.notify(self)