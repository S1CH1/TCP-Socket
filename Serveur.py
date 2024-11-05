import socket
import threading
from cryptography.fernet import Fernet

#génération de la clé de chiffrement symétrique
key = Fernet.generate_key()
chiffrement = Fernet(key)

#on définit nos jeux de login mot de passe
login_mdp = [("admin", "tprzo.40"), ("1", "password"), ("user2", "password2")]

#on définit promotion comme dictionnaire qui va nous permettre de stocker les promotions
#les étudiants les notes et etc
promotions = {}

#on créé les messages login et mdp 
message_login = f"login :"
message_mdp = f"mdp :"

#on crée le serveur tcp ipv4 et on le lie avec bind à localhost et au port 65400
serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur_socket.bind(("localhost", 65401))
#on met le serveur sur écoute
serveur_socket.listen()

#on défini une fonction verification_connexion, comme son nom l'indique, va nous permettre de verifier la connexion (login et mdp)
def verification_connexion(login, mdp):
    #on va tester tt les logins et mdp du tab
    for login_s, mdp_s in login_mdp:
        #on verifie que la paire login mot de passe, correspond avec une paire du tab
        if login_s == login and mdp_s == mdp:
            #si la conexion est juste et établie on return True, et connexion réussi
            return True, f"400;Connexion réussie"
    #on return False et le message si la connexion n'est pas bonne
    return False, f"444;Login ou mot de passe incorrect"

#on créer une fonction gerer_client pour lui envoyé tt les infos, mais aussi les recevoir
def gerer_client(connexion):
    try:
        #on print d'abord la clé de chiffrement sur le serveur pourqu'on puisse voir si le client reçoit exactement la même
        print("400;Envoi de la clé de chiffrement au client...")
        #envoie de la clé de chiffrement au client
        connexion.sendall(key)
        #on print que la clé a bien été envoyé
        print("400; clé envoyé avec succès.")
        
        #encoye de la demande de login
        connexion.sendall(chiffrement.encrypt(message_login.encode("utf-8")))
        print("400;Demande de login envoyée.")
        
        #recevoir le login
        login = chiffrement.decrypt(connexion.recv(1024)).decode("utf-8")
        print(f"400;Login reçu: {login}")
        
        #envoye de la demande de mot de passe
        connexion.sendall(chiffrement.encrypt(message_mdp.encode("utf-8")))
        print("400;Demande de mot de passe envoyée.")
        
        #recevoir le mot de passe
        mdp = chiffrement.decrypt(connexion.recv(1024)).decode("utf-8")
        print(f"400;Mot de passe reçu: {mdp}")
        
        #vérif des informations de connexion
        #succes prendra soit la valeur True si la connexion est juste, sinon False
        #et message contiendra le message de la vérification
        success, message = verification_connexion(login, mdp)
        #on envoie le message de vétification
        connexion.sendall(chiffrement.encrypt(message.encode("utf-8")))
        #si la connexion est pas bonne, le serveur affichera : 
        if message == "444;Login ou mot de passe incorrect" :
            print(f"444;Résultat de la connexion: {message}")
         
        #si la connexion est bien établie, le serveur nous renverra ceci   
        else :
            print(f"400;Résultat de la connexion: {message}")
        
        #if succes == True
        if success:
            #Envoye du menu explicatif après la connexion réussie
            menu = (
            "\nOptions:\n"
            "1. Créer une nouvelle promotion: 1;nom_promo"
            "2. Ajouter un nouvel étudiant dans une promotion: 2;nom_promo;id_etu;nom_etu;prenom_etu\n"
            "3. Ajouter une note à un étudiant dans une promotion: 3;nom_promo;id_etu;note;coef\n"
            "4. Calculer la moyenne d'un étudiant dans une promotion: 4;nom_promo;id_etu\n"
            "5. Calculer la moyenne d'une promotion: 5;nom_promo\n"
            "6. Récupérer les détails d'un étudiant dans une promotion: 6;nom_promo;id_etu\n"
            "7. Voir tous les étudiants d'une promotion avec leurs notes: 7;nom_promo\n"
            "8. Quitter: 8\n"
        )
            connexion.sendall(chiffrement.encrypt(menu.encode("utf-8")))
            print("400;Menu envoyé.")
        
        #on lance la boucle pour recevoir les commandes du client
        while True:
            #on attend un commande du client 
            print("200;En attente de commande du client")
            #on récupère la commande
            commande = chiffrement.decrypt(connexion.recv(1024)).decode("utf-8")
            
            print(f"200;Commande reçue: {commande}")
            
            #les commandes arrive avec des ; on sépare les catégories nos commandes avec split et en paramètre ; pour avoir une liste de nos dufférents argurments
            parts = commande.split(";")
            #on récupère le nombre de la commande
            commande = parts[0]
            
            #si commande est égale a 1, on va créer une new promotion
            if commande == "1":
                #on récupère le nom
                promotion_name = parts[1]
                #on check si la promotions n'existe pas déja
                if promotion_name in promotions:
                    #préparation du message
                    reponse = f"444;Promotion déjà existante"
                
                #si la promo n'existe pas on la créé, et cette key promo aura comment item un dictionnaire
                else:
                    promotions[promotion_name] = {}
                    #création de la réponse
                    reponse = f"400;Promotion créée"

            #si commande est égale a 2, on va créer une new etudiant
            elif commande == "2":
                #on récupère ttes les infos que l'on souhaite
                promotion_name, student_id, student_nom, student_prenom = parts[1:5]
                #on check si promo existe
                if promotion_name in promotions:
                    #on check si l'id existe déja ou pas
                    if student_id in promotions[promotion_name]:
                        #préparation de la réponse
                        reponse = f"444;ID de l'étudiant déjà existant"
                    #si l'id n'existe pas on créer l'étudiant
                    else:
                        #dans l'item de la promo on place la key id, et on donne comme item a id, le dictionnaire suivant :
                        #{'nom': student_nom, 'prénom': student_prenom, 'notes': []}
                        promotions[promotion_name][student_id] = {'nom': student_nom, 'prénom': student_prenom, 'notes': []}
                        reponse = f"400;Étudiant ajouté"
                else:
                    reponse = f"444;Promotion non trouvée"
            
            #si commande est égale a 3, on va ajouter une note a un étudiant
            elif commande == "3":
                #on récupère ttes les infos que l'on souhaite
                promotion_name, student_id, note, coefficient = parts[1:5]
                #on convertit la note et le coeff en float
                note = float(note)
                coefficient = float(coefficient)
                #on check si la promo existe et que l'id de l'étudiant existe 
                if promotion_name in promotions and student_id in promotions[promotion_name]:
                    #on ajoute dans le tab notes, un dictionnaire avec key note et coefficient, et leur item respective, donc leur note et coef
                    promotions[promotion_name][student_id]["notes"].append({'note': note, "coefficient": coefficient})
                    #preparation de la reponse
                    reponse = "400;Note ajoutée"
                #si la promo et l'id n'a pas été trouvé 
                else:
                    reponse = "444;Promotion ou étudiant non trouvé"

            #si commande est égale a 4, on va calculer la moyenne d'un étudiant
            elif commande == "4":
                #on récupère la promo et l'id
                promotion_name, student_id = parts[1:3]
                #on verifie si la promo existe et si l'id de l'élève existe 
                if promotion_name in promotions and student_id in promotions[promotion_name]:
                    #si oui, notes prend le tab notes de la promo
                    notes = promotions[promotion_name][student_id]["notes"]
                    #on calcul le total, g est une variables temporaire pour représenter notes
                    #on fait la somme des (items note * items coefficient) qui y a dans notes
                    total = sum(g["note"] * g["coefficient"] for g in notes)
                    #on fait pareil avec les coefficient
                    coefficients = sum(g["coefficient"] for g in notes)
                    #on fait la moyenne, et on fait un ternaire pour simplifier le résultat si la somme des coef est différent de 0
                    # alors moyenne sera égal a total/coefficient sinon à 0 car on ne peut pas diviser par 0
                    moyenne = total / coefficients if coefficients != 0 else 0
                    #preparation de la réponse
                    reponse = f"400;Moyenne de l'étudiant: {moyenne}"
               #la promotion n'est pas trouvé ou si l'id n'existe pas  
                else:
                    #alors on prepare la réponse
                    reponse = "444;Promotion ou étudiant non trouvé"

            #si commande est égale a 5, on va calculer la moyenne d'une promo
            elif commande == "5":
                #on recup le nom de la promo
                promotion_name = parts[1]
                #si promo existe 
                if promotion_name in promotions:
                    #on définit un tab, tte les notes
                    ts_notes = []
                    #pour tt les étudiant, on va prendre leur ID
                    for Id in promotions[promotion_name].values():
                        #extend permet d'ajouter les éléments de la liste notes dans ts_notes
                        ts_notes.extend(Id["notes"])
                    #on fait la moyenne comme vu au dessus    
                    total = sum(g["note"] * g["coefficient"] for g in ts_notes)
                    coefficients = sum(g["coefficient"] for g in ts_notes)
                    moyenne = total / coefficients if coefficients != 0 else 0
                    reponse = f"400;Moyenne de la promotion: {moyenne}"
                
                #si promo existe pas 
                else:
                    #preparation de la reponse 
                    reponse = "444;Promotion non trouvée"

            #si la commande est égale a 6, on récupère les détails d'un etudiant d'une promo
            elif commande == "6":
                #on récupère les données de 1 a 3-1
                promotion_name, student_id = parts[1:3]
                #on check si promotion et id exxiste dans la promo
                if promotion_name in promotions and student_id in promotions[promotion_name]:
                    #eleve = au dictionnaire key de id 
                    eleve = promotions[promotion_name][student_id]
                    #on prepare la réponse
                    reponse = f"400;Détails de l'étudiant: {eleve}"
                #on prépre la réponse si promo ou id non trouvé
                else:
                    reponse = 'Promotion ou étudiant non trouvé'
            #si commande == 7, on va afficher les données de tt les élèves d'une promo
            elif commande == '7':
                #on récup le nom de la promo
                promotion_name = parts[1]
                #si promo existant
                if promotion_name in promotions :
                    #etudiant notes récupère le dictionnaire key de la promo
                    etudiants_notes = promotions[promotion_name]
                    #on prépare la réponse 
                    reponse = f"400;Étudiants et notes pour {promotion_name}:\n"
                    #etudiant est le nom de l'étudiant et details est l'id
                    for etudiant, details in etudiants_notes.items():
                        #on ajoute a réponse le nom l'id et notes  
                        reponse += f"{details['nom']} ({etudiant}): {details['notes']}\n"
                
                #preparation de réponse et envoye
                else:
                    reponse = f"444;Promotion n'existe pas."
                    connexion.sendall(chiffrement.encrypt(reponse.encode("utf-8")))
                    print(f"400;Réponse envoyée: {reponse}")
                    
            #si commande est égale a 8 on coupe proprement la connection du client
            elif commande == '8':
                reponse = "444;déconexion"
                connexion.sendall(chiffrement.encrypt(reponse.encode("utf-8")))
                break
            
            #preparation de réponses si la commande est invalid
            else:
                reponse = "444;Commande invalide. Veuillez réessayer."

            #on envoir la réponse
            connexion.sendall(chiffrement.encrypt(reponse.encode("utf-8")))
            print(reponse)

#captute tte les exception de la classe Exception, quasiment tte les ereurs python
    except Exception as erreur:
        print(f"444;Erreur: {erreur}")
#si 8 est pressé, on break et on passe a finally
    finally:
        connexion.close()

#on créer une fonction accepter_connexions
def accepter_connexions():
    while True:    
        try:
            #accept attend une nouvelle conexion au serveur
            #connexion est un objet de socket qui représente la connexion avec le client
            #et comme son nom l'indique adresse, on recup l'adresse du client
            connexion, adresse = serveur_socket.accept()
            print(f"400;Connexion acceptée de {adresse}")
            #création d'un nouveau thread a chaque connexion qui va lancer gerer_client avec comme argument connexion
            thread = threading.Thread(target=gerer_client, args=(connexion,))
            #on lance le thread
            thread.start()
        
        #on gère l'arrêt du serveur  
        except KeyboardInterrupt:
            print("444;Arrêt du serveur")
            serveur_socket.close()
            break
#on appel la fonction accepter_connexions pour tt démarer
accepter_connexions()