from Client import Client
from Routeur import Routeur
from Serveur import Serveur
from Echeancier import Echeancier, Ev
import matplotlib.pyplot as plt
import numpy as np


def initialise_ferme(nb_groupes, echeancier) -> Routeur:
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

def simulation(duree, lambda_client, nb_groupes):
    ech = Echeancier()
    rout = Routeur(nb_groupes, ech)

    # initialisation des groupes de serveurs
    groupes = []
    serv_par_grp = 12 // nb_groupes
    lambda_map = {1:4/20, 2:7/20, 3:10/20, 6:14/20}
    lambda_serv = lambda_map[nb_groupes]
    for spe in range(nb_groupes):
        grp = [Serveur(ech, lambda_serv, rout, spe) for _ in range(serv_par_grp)]
        groupes.append(grp)
    rout.add_groupes(groupes)

    # création du client
    client = Client(rout, lambda_client, ech)

    # simulation
    while ech.temps_actuel < duree and not ech.est_vide():
        ev, details = ech.prochain_evenement()
        if ev == Ev.NR:
            client.envoie_requete()
        elif ev == Ev.RAR:
            rout.route_requete(details)
        elif ev == Ev.FT:
            details[0].fin_traitement()

    return rout, ech


def calcule_delta(data):
    delta = dict()
    for temps, id, event in data:
        if not event:
            delta[id] = - temps
        else:
            delta[id] += temps

    delta = {id: dt for id, dt in delta.items() if dt >= 0}
    return delta

def calcule_moyenne(data):
    avg = 0
    lenght = 0
    for value in data.values():
        if value > 0:
            lenght += 1
            avg += value

    return (avg / lenght)

if __name__ == "__main__":

    couleurs = ['blue', 'green', 'red', 'orange']
    lambdas = [i/10 for i in range(1, 70)]
    temps_max = 10000
    groupes_list = [1, 2, 3, 6] 
    #for i, nb_groupes in enumerate([1, 2, 3, 6]):
    #    moyennes = []
    #    ic_95 = []
    #    for lb in lambdas:
    #        print(lb)
    #        rout, echeancier = simulation(temps_max, lb, nb_groupes)
    #        print(f"Fin de la simulation:\n - Requêtes traitées: {rout.nb_total}\n - Requêtes perdues: {rout.perte}")
    #        deltas = calcule_delta(echeancier.historique) # potentiellement changer calcule_delta pour retourner une liste
    #        temps_reponses = list(deltas.values())
    #        n = len(temps_reponses)
    #
    #        if n > 1:
    #            moyenne = np.mean(temps_reponses)
    #            ecart_type = np.std(temps_reponses, ddof=1)
    #            intervalle = 1.96 * (ecart_type / np.sqrt(n))
    #
    #        moyennes.append(moyenne)
    #        ic_95.append(intervalle)
    #
    #    plt.errorbar(lambdas, moyennes, yerr=ic_95, fmt='-o', color=couleurs[i], label=f"{nb_groupes} groupes")
    #
    #
    #plt.xlabel("λ (taux d’arrivée des requêtes)")
    #plt.ylabel("Temps de réponse moyen (s)")
    #plt.title("Évolution du temps de réponse moyen en fonction de λ")
    #plt.grid(True)
    #plt.legend(title="Nb Groupes")
    #plt.show()

    plt.figure()
    for i, C in enumerate(groupes_list):
        pertes_pct = []
        for lb in lambdas:
            print(lb)
            rout, ech = simulation(temps_max, lb, C)
            print(f"Fin de la simulation:\n - Requêtes traitées: {rout.nb_total}\n - Requêtes perdues: {rout.perte}")
            if rout.nb_total > 0:
                pertes_pct.append(100 * rout.perte / rout.nb_total)
            else:
                pertes_pct.append(0)
        plt.plot(lambdas, pertes_pct, '-', color=couleurs[i], label=f"C={C}")

    plt.xlabel("λ (taux d’arrivée des requêtes)")
    plt.ylabel("Pourcentage de pertes (%)")
    plt.title("Taux de perte des requêtes en fonction de λ et C")
    plt.grid(True)
    plt.legend(title="Nombre de groupes (C)")
    plt.show()