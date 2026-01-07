import cv2
import os

from quiz.core.quiz_controller import QuizController
from .cv_utils import (
    MaskConfig,
    ColorDetectionConfig,
    CameraConfig,
    get_sign_mask,
    compute_color_surface,
    compute_red_surface
)


class QuizControllerCVCLI(QuizController):

    """
    Le ControleurVision capture des images provenant de la caméra, identifie 
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
        self.colors = ColorDetectionConfig()
        self.camera = CameraConfig()
        self.mask_config = MaskConfig()

    def release_resources(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def run_quiz(self):
        """Fonction run_quiz. Elle capture des images de la webcam, traite celles 
        qui se trouvent dans le rectangle aux contours blancs en haut à gauche du 
        retour caméra. Attend qu'un joueur présente un panneau. Dès qu'un panneau 
        est détecté, la couleur dominante de la zone masquée par la fonction get_mask 
        est utilisée pour enregistrer la réponse.
        """
        try:
            self.quiz.begin()
            while True:
                # Ask for a JSONL file.
                self.quiz.inform_player(["Specify a quiz file (.jsonl): "])
                path = input()
                if os.path.isfile(path) \
                   and os.access(path, os.R_OK) \
                   and path.endswith('.jsonl'):
                    # The file has the a `.jsonl` extension and is readable.
                    self.quiz.set_quiz_file(path)
                    break
                # Ask for a file again.
                self.quiz.inform_player(["Invalid path or file extension"])
            self.cap = cv2.VideoCapture(0)

            while self.quiz.next_question():
                # A question is available.
                n_opts = len(self.quiz.get_options())

                while self.quiz.ask_next_player():
                    # A player is available.
                    player = self.quiz.get_player_name()
                    answer_index = -1
                    self.quiz.inform_player([
                        f"{player}, raise your sign to answer!"
                    ])
                    # Attend une détection...
                    while answer_index == -1:
                        ret, frame = self.cap.read()
                        if not ret:
                            continue

                        h, w = frame.shape[:2]
                        text, t_color = "", (255, 255, 255)
                        roi_w = int(w * self.camera.roi_width_ratio)
                        roi_h = int(h * self.camera.roi_height_ratio)

                        image = frame[0:roi_h, 0:roi_w]
                        sign_mask = get_sign_mask(image, self.mask_config)

                        if sign_mask is not None:
                            # Conversion de l'image en HSV et isolement
                            # de la couleur dans le  masque à l'aide
                            # de la fonction cv2.bitwise_and.
                            # Ici l'image source et destination sont les mêmes
                            # pour indiquer qu'on veut conserver
                            # les valeurs des pixels d'origine.
                            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                            hsv_isole = cv2.bitwise_and(hsv, hsv, mask=sign_mask)

                            # Je calcule une surface de pixels de couleur.
                            # Je crée un masque de couleur, j'applique un flou
                            # médian pour enlever le bruit, puis j'additionne
                            # avec np.sum() tous les pixels du masque.

                            # J'utilise un dictionnaire stockant les surfaces
                            # pour chaque couleur, de façon aribitraire.
                            # J'utilise un flou plus fort (15) car
                            # les pancartes sont plus petites.
                            surfaces = {
                                0: compute_color_surface(
                                    hsv_isole,
                                    self.colors.green,
                                    self.colors.blur_small_sign
                                ),
                                1: compute_red_surface(
                                    hsv_isole,
                                    self.colors.red1,
                                    self.colors.red2,
                                    self.colors.blur_small_sign
                                ),
                                2: compute_color_surface(
                                    hsv_isole, self.colors.yellow,
                                    self.colors.blur_big_sign
                                ),
                                3: compute_color_surface(
                                    hsv_isole, self.colors.green,
                                    self.colors.blur_big_sign
                                ),
                                4: compute_color_surface(
                                    hsv_isole, self.colors.blue,
                                    self.colors.blur_big_sign
                                ),
                                5: compute_color_surface(
                                    hsv_isole, self.colors.magenta,
                                    self.colors.blur_big_sign
                                ),
                            }

                            valid_surfaces = {
                                k: v for k, v in surfaces.items() if k < n_opts
                            }
                            answer_surface = max(
                                valid_surfaces, key=valid_surfaces.get
                            )
                            # Je vérifie si la plus grande surface détectée
                            # dépasse le seuil
                            if valid_surfaces[answer_surface] \
                                    > self.colors.min_color_area:
                                answer_index = answer_surface
                                text = f"REPONSE {chr(65 + answer_index)}"

                        # Interface Caméra : Dessin du rectangle image, si réponse
                        # détectée affichage  d'un texte au milieu du retour caméra.
                        cv2.rectangle(
                            frame,
                            (0, 0),
                            (roi_w, roi_h),
                            self.camera.rectangle_color,
                            self.camera.rectangle_thickness
                        )

                        if text:
                            ts = cv2.getTextSize(
                                text,
                                self.camera.text_font,
                                self.camera.text_scale,
                                self.camera.text_thickness
                            )[0]
                            cv2.putText(
                                frame,
                                text,
                                ((w - ts[0]) // 2, (h + ts[1]) // 2),
                                self.camera.text_font,
                                self.camera.text_scale,
                                t_color,
                                self.camera.text_thickness
                            )

                        cv2.imshow('Detection Raise-Your-Sign', frame)
                        cv2.waitKey(1)

                    self.quiz.record_answer(answer_index)

            self.release_resources()
            self.quiz.end([self.quiz.output_file])

        except KeyboardInterrupt:
            self.quiz.inform_player(["\nQuiz exited with ^C"])
            self.release_resources()
            return
