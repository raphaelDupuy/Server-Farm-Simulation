import Requete
import Serveur

class Routeur():

    def __init__(self, nb_groupes, groupes):

        if not nb_groupes in {1, 2, 3, 6}:
            raise ValueError("Nombre de groupes incorrect")
        else:
            self.nb_groupes = nb_groupes

        self.groupes = groupes
        self.file = []
        self.nb_attente = 0
        self.perte = 0
        self.nb_total = 0

    def __str__(self):
        res_str = "===========:Routeur:===========\n"
        cnt = 1
        for grp in self.groupes:
            res_str += f"------------Groupe {cnt}-----------\n"
            cnt += 1
            for serv in grp:
                res_str += serv.__str__()
        res_str += "==============================="
        return res_str


    def ajoute_requete(self, requete):
        self.nb_total += 1

        if self.nb_attente < 100:
            self.file.append(requete)
            self.nb_attente += 1

        else:
            self.perte += 1

    def route_requete(self, requete):

        spe = requete.value
        for serveur in self.groupes[spe]:
            if serveur.status:
                serveur.traite(requete)
            