import Requete
import Serveur
import Routeur

def initialise_ferme(nb_groupes) -> Routeur:
    groupes = []
    serv_par_grp = 12/nb_groupes
    for i in range(nb_groupes):
        spe = []
        for _ in range (serv_par_grp):
            spe.append(Serveur(i))

        groupes.append(spe)

    return Routeur(nb_groupes, groupes)


