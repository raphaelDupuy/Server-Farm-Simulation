from Serveur import Serveur
from Routeur import Routeur

def initialise_ferme(nb_groupes) -> Routeur:
    groupes = []
    serv_par_grp = 12//nb_groupes
    for i in range(nb_groupes):
        spe = []
        for _ in range (serv_par_grp):
            spe.append(Serveur(i + 1))

        groupes.append(spe)

    return Routeur(nb_groupes, groupes)