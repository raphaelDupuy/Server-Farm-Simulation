from Client import Client
from Requete import Requete
from Routeur import Routeur
from Serveur import Serveur
from Echeancier import Echeancier, Evenement as Ev

param_lambda = 1/2
echeancier = Echeancier()

def initialise_ferme(nb_groupes) -> Routeur:
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
            spe.append(Serveur(echeancier , lambda_serv, i + 1))

        groupes.append(spe)

    return Routeur(nb_groupes, groupes, echeancier)


def simulation(duree):
    rout = initialise_ferme(6)
    client = Client(rout, param_lambda, echeancier)
    while echeancier.temps_actuel < duree: 
        print(echeancier.echeancier)
        type_evenement, details = echeancier.prochain_evenement()

        match type_evenement:
            case Ev.NR:
                client.envoie_requete()
                print("Evenement : Nouvelle requête")
            case Ev.RAR:
                rout.route_requete(details[1])
                print("Evenement : Requête à traîter")
            case Ev.FT:
                print("Evenement : Fin de traîtement")

simulation(100)