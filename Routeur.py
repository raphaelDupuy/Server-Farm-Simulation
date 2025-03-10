import Requete
import Serveur

class Routeur():

    def __init__(self, nb_groupes, groupes):
        self.nb_groupes = nb_groupes
        self.groupes = groupes
        self.file = []
        self.nb_attente = 0
        self.perte = 0

    def route_requete(self, requete):

        spe = requete.value
        for serveur in self.groupes[spe]:
            if serveur.status:
                serveur.traite(requete)
            