import cv2
import numpy as np
from quiz.core.quiz_controller import QuizController

class QuizControllerVision(QuizController):
    def __init__(self, quiz):
        super().__init__(quiz)
        self.lower_red1, self.upper_red1 = np.array([0, 170, 100]), np.array([10, 255, 255])
        self.lower_red2, self.upper_red2 = np.array([170, 170, 100]), np.array([180, 255, 255])
        self.lower_yellow, self.upper_yellow = np.array([15, 150, 150]), np.array([32, 255, 255])
        self.lower_green, self.upper_green = np.array([40, 100, 50]), np.array([80, 255, 255])
        self.lower_blue, self.upper_blue = np.array([100, 180, 60]), np.array([130, 255, 255])
        self.lower_magenta, self.upper_magenta = np.array([145, 150, 100]), np.array([170, 255, 255])
        self.seuil_minimum = 30000 

    def get_mask(self, image):
        # Détecte le cadre et renvoie le masque (Sobel)
        gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        flou = cv2.GaussianBlur(gris, (5, 5), 0)
        gx = cv2.Sobel(flou, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(flou, cv2.CV_32F, 0, 1)
        mag_norm = cv2.normalize(cv2.sqrt(gx**2 + gy**2), None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        _, seuil = cv2.threshold(mag_norm, 50, 255, cv2.THRESH_BINARY)
        kernel = np.ones((7,7), np.uint8)
        fermeture = cv2.morphologyEx(seuil, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(fermeture, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 5000:
                masque = np.zeros_like(gris)
                cv2.drawContours(masque, [c], -1, 255, -1)
                return masque
        return None

    def run_quiz(self):
        self.quiz.begin()
        quiz_path = "tests/quiz_data.jsonl" 
        self.quiz.set_quiz_file(quiz_path)
        cap = cv2.VideoCapture(0)

        while self.quiz.next_question():
            n_opts = len(self.quiz.get_options())
            is_yes_no = (n_opts == 2)

            while self.quiz.ask_next_player():
                reponse_index = -1
                
                while reponse_index == -1:
                    ret, frame = cap.read()
                    if not ret: break

                    h, w = frame.shape[:2]
                    image = frame[0:h//2, 0:w//2]
                    masque_cadre = self.get_mask(image)
                    
                    text, t_color = "", (255, 255, 255)

                    if masque_cadre is not None:
                        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
                        hsv_isole = cv2.bitwise_and(hsv, hsv, mask=masque_cadre)

                        if is_yes_no:
                            surf_v = np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, self.lower_green, self.upper_green), 7))
                            m_r = cv2.addWeighted(cv2.inRange(hsv_isole, self.lower_red1, self.upper_red1), 1.0, 
                                                 cv2.inRange(hsv_isole, self.lower_red2, self.upper_red2), 1.0, 0)
                            surf_r = np.sum(cv2.medianBlur(m_r, 7))
                            
                            if max(surf_v, surf_r) > self.seuil_minimum:
                                reponse_index = 0 if surf_v > surf_r else 1
                                text, t_color = ("OUI", (0, 255, 0)) if reponse_index == 0 else ("NON", (0, 0, 255))
                        else:
                            surfaces = {
                                0: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, self.lower_yellow, self.upper_yellow), 15)),
                                1: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, self.lower_green, self.upper_green), 15)),
                                2: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, self.lower_blue, self.upper_blue), 15)),
                                3: np.sum(cv2.medianBlur(cv2.inRange(hsv_isole, self.lower_magenta, self.upper_magenta), 15))
                            }
                            # On limite aux options disponibles pour la question
                            valid_surfaces = {k: v for k, v in surfaces.items() if k < n_opts}
                            gagnant = max(valid_surfaces, key=valid_surfaces.get)
                            
                            if valid_surfaces[gagnant] > self.seuil_minimum:
                                reponse_index = gagnant
                                text = f"REPONSE {chr(65 + reponse_index)}" # Convertit 0 en 'A', 1 en 'B'...

                    # Interface Caméra : todo
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