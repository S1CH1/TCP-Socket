import socket
from cryptography.fernet import Fernet

#on crée le serveur tcp ipv4 et on le li a localhost et au port 65401
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 65401))

#on reçoit la clé de chiffrement du serveur, chiffrement symétrique
clé = client_socket.recv(1024)
#on print la clé
print(f"clé reçue: {clé}")
#création du chiffrement avec la clé du serveur
chiffrement = Fernet(clé)

#reçoit la demande de connexion
message_login = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
print(message_login)

#on input le login à la main pour se connecter et les mots de passes sont directements stocker sur le serveur
login = input("Please enter login: ")
#on envoie le login en pensant à chiffrer
client_socket.sendall(chiffrement.encrypt(login.encode('utf-8')))

#pareil que pour le login on recoit la demande de password, puis on l'envoie
message_mdp = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
print(message_mdp)
password = input("Please enter password: ")
client_socket.sendall(chiffrement.encrypt(password.encode('utf-8')))

#on reçoit le message de validation de la connexion ou de déconexion
resultat_connexion = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
print(resultat_connexion)

#Si la connexion réussi, on print le menu pour que le client ait accès aux commandes, le menu est envoyer depuis le serveur
if "Connexion réussie" in resultat_connexion:
    menu = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
    print(menu)

#ici on définit des jeux de tests pour l'évaluations, chaque tests peut être lancé sur un thread différent, si on les passe en commentaire
     # premier jeu de tests
    tests = [
        "1;rt1",  #création d'une nouvelle promotion rt1
        "2;rt1;1;Ascoet;Kylian",  #ajout de l'étudiant kylian
        "2;rt1;2;Patao;Isaac",  #ajout de l'étudiant Isaac
        "3;rt1;1;15;1",  #ajout d'une note pour l'élève kylian
        "3;rt1;1;18;2",  #ajout d'une note pour l'élève kylian
        "3;rt1;2;12;1",  #ajout d'une note pour l'élève isaac
        "4;rt1;1",  #calcul de la moyenen de kylian
        "5;rt1",  #calcul de la moyenne de la promo rt1
        "6;rt1;1",  #recup des données de l'étudiant kylian
        "7;rt1",  #voir tous les étudiant de la promotion et leur notes respectives 

    ]
    
    #deuxième jeu de tests
    tests2 = [
        "1;rt2",  #création d'une nouvelle promotion rt2
        "2;rt2;1;Bour;Coralie",  #ajout de l'étudiante Coralie
        "2;rt2;2;Laboudigue;Zoé",  #ajout de l'étudiante Zoé
        "3;rt2;1;14;1",  #ajout d'une note pour l'élève Coralie
        "3;rt2;1;17;2",  #""
        "3;rt2;2;13;1",  #ajout d'une note pour l'élève Zoé
        "4;rt2;1",  #calcul de la moyenne de Coralie
        "5;rt2",  #calcul de la moyenne de la promo rt2
        "6;rt2;1",  #recup des données de l'étudiant Coralie
        "7;rt2",  #voir tous les étudiant de la promotion et leur notes respectives
    ]
    
    #troisième jeu de tests
    tests3 = [
        "1;rt3",  #création d'une nouvelle promotion rt3
        "2;rt3;1;Bouyssou;Clément",  #ajout de l'étudiante Clément
        "2;rt3;2;Laboudigue;Thomas",  #ajout de l'étudiante Thomas
        "3;rt3;1;14;1",  #ajout d'une note pour l'élève Clément
        "3;rt3;2;17;2",  #ajout d'une note pour l'élève Thomas
        "3;rt3;1;13;1",  #ajout d'une note pour l'élève Clément
        "4;rt3;1",  #calcul de la moyenne de Clément
        "5;rt3",  #calcul de la moyenne de la promo rt3
        "6;rt3;1",  #recup des données de l'étudiant Clément
        "7;rt3",  #voir tous les étudiant de la promotion et leur notes respectives
    ]

    
 #boucles pour lancer les différents tests   
 
    for test in tests:
        #on print la commande avant de l'envoyer
        print(f"Envoi de la commande: {test}")
        #on envoie la commande
        client_socket.sendall(chiffrement.encrypt(test.encode('utf-8')))
        #on reçoit la réponse du serveur
        reponse = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
        #on print la réponse
        print(f"Réponse: {reponse}")
        #on check pour voir si une commande 8, donc quitter a été taper
        if test == '8':
            break
    
    """for test in tests2:
        print(f"Envoi de la commande: {test}")
        client_socket.sendall(chiffrement.encrypt(test.encode('utf-8')))
        reponse = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
        print(f"Réponse: {reponse}")
        if test == '8':
            break"""
    
    """for test in tests3:
        print(f"Envoi de la commande: {test}")
        client_socket.sendall(chiffrement.encrypt(test.encode('utf-8')))
        reponse = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
        print(f"Réponse: {reponse}")
        if test == '8':
            break"""
        
 #code pour executer du code à la main
    while True:
        #on demande la commande au user
        commande = input("Entrez une commande: ")
        #on l'envoie
        client_socket.sendall(chiffrement.encrypt(commande.encode('utf-8')))
        #on attend la réponse du serveur
        reponse = chiffrement.decrypt(client_socket.recv(1024)).decode('utf-8')
        #on print la réponse du serveur pour savoir la commande à été executer ou savoir si il y a eu un problème
        print(reponse)
        #si on tape 8 le client se coupe proprement
        if test == '8':
            break
#on fermet le socket client
client_socket.close()