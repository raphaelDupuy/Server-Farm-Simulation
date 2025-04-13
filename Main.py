from Client import Client
from Routeur import Routeur
from Serveur import Serveur
from Echeancier import Echeancier, Evenement as Ev

param_lambda = 40/20
nb_groupes = 3
temps_max = 10000
echeancier = Echeancier()

def initialise_ferme(nb_groupes) -> Routeur:
    rout = Routeur(nb_groupes, echeancier)
    groupes = []
    serv_par_grp = 12//nb_groupes
    for i in range(nb_groupes):
        spe = []

        match nb_groupes:
            case 1:
                lambda_serv = 4/20
            case 2:
                lambda_serv = 7/20
            case 3:
                lambda_serv = 10/20
            case 6:
                lambda_serv = 14/20

        for _ in range (serv_par_grp):
            spe.append(Serveur(echeancier , lambda_serv, rout, i))

        groupes.append(spe)

    rout.add_groupes(groupes)

    return rout


def simulation(duree):
    client = Client(rout, param_lambda, echeancier, nb_groupes)
    while echeancier.temps_actuel < duree: 
        type_evenement, details = echeancier.prochain_evenement()
        match type_evenement:
            case Ev.NR:
                print(f"Evenement : Nouvelle requête")
                client.envoie_requete()
            case Ev.RAR:
                print(f"Evenement : Requête à router - {details[1]}")
                rout.route_requete(details[1])
            case Ev.FT:
                print(f"Evenement : Fin de traîtement - {details[1]}")
                details[0].fin_traitement()

rout = initialise_ferme(nb_groupes)
simulation(temps_max)
print(f"Fin de la simulation:\n - Requêtes traitées: {rout.nb_total}\n - Requêtes perdues: {rout.perte}")