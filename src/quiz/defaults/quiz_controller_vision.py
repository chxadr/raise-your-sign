import cv2
import numpy as np
from quiz.core.quiz_controller import QuizController

class QuizControllerVision(QuizController):
    """
    Le ControleurVision capture des images provenant d'une caméra, identifie 
    les bordures de panneaux et analyse la couleur contenue dans ces bordures 
    fermées, soit les bordures qui forment un cadre (rond ou carré), pour 
    déterminer la réponse du joueur.
    """
    def __init__(self, quiz):
        """Initialise le contrôleur_vision avec des seuils optimisés 
        de HSV : (Teinte, Saturation, Valeur) pour chaque couleur utilisée 
        sur les pancartes. Aussi le rouge est divisé en red1 et red2 pour 
        représenter le début et la fin du cercle chromatique HSV.
        """
        super().__init__(quiz)
        self.lower_red1, self.upper_red1 = np.array([0, 170, 100]), np.array([10, 255, 255])
        self.lower_red2, self.upper_red2 = np.array([170, 170, 100]), np.array([180, 255, 255])
        self.lower_yellow, self.upper_yellow = np.array([15, 150, 150]), np.array([32, 255, 255])
        self.lower_green, self.upper_green = np.array([40, 100, 50]), np.array([80, 255, 255])
        self.lower_blue, self.upper_blue = np.array([100, 180, 60]), np.array([130, 255, 255])
        self.lower_magenta, self.upper_magenta = np.array([145, 150, 100]), np.array([170, 255, 255])
        # Nombre minimal de pixels pour valider une couleur
        self.seuil_minimum = 30000 

    def get_mask(self, image):
        """Fonction qui détecte le cadre extérieur du panneau et renvoie un 
        masque binaire en utilisant un filtre de Sobel pour calculer le 
        gradient de l'image. Aussi j'applique une fermeture morphologique 
        morphologyEx() pour s'assurer que les bordures détectés soient une
        surface fermée, ici pancarte ronde ou carré (on ne fait donc pas la 
        différence entre les formes).
        Args:
            image: Uniquement la région de l'image encadrée par un rectangle 
            aux contours blancs en haut à gauche de l'image de retour caméra.
        Returns:
            Une masque binaire où la zone du panneau détectée est blanche (255),
            ou None si aucun cadre n'est trouvé.        
        """
        gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        flou = cv2.GaussianBlur(gris, (5, 5), 0)
        # Sobel Edge Detection
        gx = cv2.Sobel(flou, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(flou, cv2.CV_32F, 0, 1)
        # Calcul maagnitude du gradiant et normalisation de 0 à 255 sur 8 bits
        mag_norm = cv2.normalize(cv2.sqrt(gx**2 + gy**2), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        # Seuillage binaire pour isoler les bords très nets comme ceux des pancartes noirs et blancs
        _, seuil = cv2.threshold(mag_norm, 50, 255, cv2.THRESH_BINARY)
        # Opération morphologique avec noyau 7*7 pour boucher les troues dans le contour du cadre
        kernel = np.ones((7,7), np.uint8)
        fermeture = cv2.morphologyEx(seuil, cv2.MORPH_CLOSE, kernel)

        # Ici j'extrait tous les contours des formes blanche de l'image binaire. La fonction
        # cv2.findContours(image, mode de récupération, méthode d'approximation) ne s'interesse 
        # qu'au contour extérieur (cv2.RETR_EXTERNAL). Puis cv2.CHAIN_APPROX_SIMPLE, c'est une 
        # méthode pour simplifier ce qu'on enregistre, en particulier pour la forme carré, j'
        # enregistre juste les 4 points des côtés au lieu de tous les points des segments du carré.
        contours, _ = cv2.findContours(fermeture, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 5000:
                # Création d'un masque noir taille image
                masque = np.zeros_like(gris)
                # La fonction cv2.drawContours(masque, liste des contours, index du contour, couleur
                # épaisseur) permet de dessiner dans notre masque, la liste des contours [c] 
                # qu'on a trouvé par une zone blanche.
                cv2.drawContours(masque, [c], -1, 255, -1)
                return masque
        return None

    def run_quiz(self):
        """Fonction run_quiz. Elle capture des images de la webcam, traite celles 
        qui se trouvent dans le rectangle aux contours blancs en haut à gauche du 
        retour caméra. Attend qu'un joueur présente un panneau. Dès qu'un panneau 
        est détecté, la couleur dominante de la zone masquée par la fonction get_mask 
        est utilisée pour enregistrer la réponse.
        """
        self.quiz.begin()
        quiz_path = "tests/quiz_data.jsonl" 
        self.quiz.set_quiz_file(quiz_path)
        # Lance le flux vidéo
        cap = cv2.VideoCapture(0)

        # Boucle sur chaque question du fichier
        while self.quiz.next_question():
            n_opts = len(self.quiz.get_options())
            # Si la question n'a que deux réponses alors c'est mode oui/non
            is_yes_no = (n_opts == 2)

            # Boucle sur chaque joueur
            while self.quiz.ask_next_player():
                reponse_index = -1
                
                # Attend une détection...
                while reponse_index == -1:
                    ret, frame = cap.read()
                    if not ret: break

                    h, w = frame.shape[:2]
                    text, t_color = "", (255, 255, 255)
                    
                    # Création de l'image qui nous intéresse soit celle dans le rectangle en
                    # haut à gauche du retour caméra
                    image = frame[0:h//2, 0:w//2]
                    # Détection d'un masque dans cette image
                    masque_cadre = self.get_mask(image)
                    
                    if masque_cadre is not None:
                        """
                        En fait, cette condition joue le rôle d'une fonction de traitement d'image.
                        """
                        # Conversion de l'image en HSV et isolement de la couleur dans le 
                        # masque à l'aide de la fonction cv2.bitwise_and(image source, image 
                        # destination, masque). Ici l'image source et destination sont les mêmes
                        # pour indiquer qu'on veut conserver les valeurs des pixels d'origine.
                        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                        hsv_isole = cv2.bitwise_and(hsv, hsv, mask=masque_cadre)

                        if is_yes_no:
                            # Je calcule une surface de pixels verts. Je crée un masque de
                            # vert, j'applique un flou médian pour enlever le bruit, 
                            # puis j'additionne avec np.sum() tous les pixels du masque.
                            surf_v = np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, 
                                                                       self.lower_green, 
                                                                       self.upper_green), 7))
                            # Comme le rouge est coupé en deux dans le spectre HS il faut 
                            # créer deux masques qu'on fusionne avec addWeighted()
                            m_r = cv2.addWeighted(cv2.inRange(hsv_isole, 
                                                              self.lower_red1, 
                                                              self.upper_red1), 1.0, 
                                                  cv2.inRange(hsv_isole, 
                                                              self.lower_red2, 
                                                              self.upper_red2), 1.0, 
                                                  0)
                            # Je calcule la surface de pixels rouges après un flou médian
                            surf_r = np.sum(cv2.medianBlur(m_r, 7))
                            
                            # Je vérifie si la plus grande surface détectée dépasse le seuil 
                            # de 30 000 pixels
                            if max(surf_v, surf_r) > self.seuil_minimum:
                                # Je donne l'index 0 si vert (OUI), sinon l'index 1 (NON)
                                reponse_index = 0 if surf_v > surf_r else 1
                                text, t_color = ("OUI", 
                                                 (0, 255, 0)) if reponse_index == 0 else ("NON", 
                                                                                          (0, 0, 255))
                        
                        else:
                            # J'utilise un dictionnaire stockant les surfaces pour chaque couleur 
                            # (de façon aribitraire : A=Jaune, B=Vert, C=Bleu, D=Magenta). Et je
                            # procède de la même façon que pour if_yes_no pour le calcul des surfaces,
                            # juste que j'utilise un flou plus fort (15) car les pancartes sont plus
                            # petites.
                            surfaces = {
                                0: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, 
                                                                     self.lower_yellow, 
                                                                     self.upper_yellow), 
                                                                     15)),
                                1: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, 
                                                                     self.lower_green, 
                                                                     self.upper_green), 
                                                                     15)),
                                2: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, 
                                                                     self.lower_blue, 
                                                                     self.upper_blue), 
                                                                     15)),
                                3: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, 
                                                                     self.lower_magenta, 
                                                                     self.upper_magenta), 
                                                                     15))
                            }
                            # Je limite aux options disponnibles (ex : si 3 options, on ignore D).
                            valid_surfaces = {k: v for k, v in surfaces.items() if k < n_opts}

                            # La réponse gagnante est la couleur à la plus grande surface et si elle
                            # dépasse le seuil, on valide la réponse, on récupère la key.
                            gagnant = max(valid_surfaces, key=valid_surfaces.get)
                            if valid_surfaces[gagnant] > self.seuil_minimum:
                                reponse_index = gagnant
                                text = f"REPONSE {chr(65 + reponse_index)}" 

                    # Interface Caméra : Dessin du rectangle image, si réponse détectée affichage
                    # d'un texte au milieu du retour caméra.
                    cv2.rectangle(frame, (0, 0), (w//2, h//2), (255, 255, 255), 2)
                    if text != "":
                        ts = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 2, 3)[0]
                        cv2.putText(frame, text, ((w - ts[0]) // 2, (h + ts[1]) // 2), 
                                    cv2.FONT_HERSHEY_DUPLEX, 2, t_color, 3)
                    
                    cv2.imshow('Detection Raise-Your-Sign', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'): return

                self.quiz.record_answer(reponse_index)

        self.quiz.end([self.quiz.output_file])
        cap.release()
        cv2.destroyAllWindows()