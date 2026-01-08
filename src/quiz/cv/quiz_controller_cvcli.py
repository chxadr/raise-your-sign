import cv2
import os
from typing import Any

from quiz.core.quiz_controller import QuizController
from .cv_utils import (
    MaskConfig,
    ColorDetectionConfig,
    CameraConfig,
    get_sign_mask,
    compute_color_surface,
    compute_red_surface
)
from quiz.utils.timer_utils import Timer


class QuizControllerCVCLI(QuizController):

    HOLD_TIME = 2.0

    def __init__(self, quiz):
        super().__init__(quiz)
        self.colors = ColorDetectionConfig()
        self.color_names = [
            "Green", "Red", "Yellow", "Blue", "Magenta"
        ]
        self.camera = CameraConfig()
        self.mask_config = MaskConfig()
        self.cap: Any | None = None

    def release_resources(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def wait_player(self):
        """Pause the quiz until the player presses ENTER."""
        self.quiz.inform_player(["\nPress ENTER to continue"])
        input()

    def run_quiz(self):
        hold_timer = Timer(duration=QuizControllerCVCLI.HOLD_TIME)
        color_detectors = [
            ("Green", lambda img: compute_color_surface(
                img,
                self.colors.green,
                self.colors.blur_big_sign
            )),
            ("Red", lambda img: compute_red_surface(
                img,
                self.colors.red1,
                self.colors.red2,
                self.colors.blur_big_sign
            )),
            ("Yellow", lambda img: compute_color_surface(
                img,
                self.colors.yellow,
                self.colors.blur_big_sign
            )),
            ("Blue", lambda img: compute_color_surface(
                img,
                self.colors.blue,
                self.colors.blur_big_sign
            )),
            ("Magenta", lambda img: compute_color_surface(
                img,
                self.colors.magenta,
                self.colors.blur_big_sign
            )),
        ]

        try:
            self.quiz.begin()

            while True:
                self.quiz.inform_player(["Specify a quiz file (.jsonl): "])
                path = input().strip()
                if path.endswith(".jsonl") \
                        and os.path.isfile(path) \
                        and os.access(path, os.R_OK):
                    self.quiz.set_quiz_file(path)
                    break
                self.quiz.inform_player(["Invalid path or file extension"])

            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.quiz.inform_player(["Cannot open camera"])
                return

            self.wait_player()

            while self.quiz.next_question():
                n_opts = len(self.quiz.get_options())

                while self.quiz.ask_next_player():
                    player = self.quiz.get_player_name()
                    self.quiz.inform_player([
                        f"{player}, raise your sign to answer!"
                    ])
                    answer_index = -1
                    current_color_index: int | None = None
                    detected_index: int | None = None

                    while True:
                        ret, frame = self.cap.read()
                        if not ret:
                            continue

                        h, w = frame.shape[:2]
                        roi_w = int(w * self.camera.roi_width_ratio)
                        roi_h = int(h * self.camera.roi_height_ratio)
                        roi = frame[:roi_h, :roi_w]

                        sign_mask = get_sign_mask(roi, self.mask_config)
                        text = ""

                        if sign_mask is not None:
                            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                            hsv_masked = cv2.bitwise_and(
                                hsv, hsv, mask=sign_mask
                            )

                            surfaces = [
                                detector(hsv_masked)
                                for _, detector in color_detectors[:n_opts]
                            ]

                            max_surface = max(surfaces)

                            if max_surface > self.colors.min_color_area:
                                detected_index = surfaces.index(max_surface)
                                answer = self.quiz.get_options()[detected_index]
                                color_name = color_detectors[detected_index][0]
                                text = f"{color_name}: {answer}"

                                if detected_index is not None:

                                    if detected_index != current_color_index:
                                        current_color_index = detected_index
                                        hold_timer.reset()

                                    elif hold_timer.expired():
                                        answer_index = current_color_index
                                        break

                                    else:
                                        progress = hold_timer.progress()
                                        bar_w = int(200 * progress)
                                        cv2.rectangle(
                                            frame, (20, h - 40), (220, h - 20), (255, 255, 255), 2
                                        )
                                        cv2.rectangle(
                                            frame, (20, h - 40), (20 + bar_w, h - 20), (0, 255, 0), -1
                                        )

                        else:
                            current_color_index = None
                            hold_timer.stop()

                        cv2.rectangle(
                            frame, (0, 0), (roi_w, roi_h),
                            self.camera.rectangle_color,
                            self.camera.rectangle_thickness
                        )

                        if text:
                            ts, _ = cv2.getTextSize(
                                text,
                                self.camera.text_font,
                                self.camera.text_scale,
                                self.camera.text_thickness
                            )
                            x = max(10, (w - ts[0]) // 2)
                            y = min(h - 10, int(h * 0.85))
                            cv2.putText(
                                frame, text,
                                (x, y),
                                self.camera.text_font,
                                self.camera.text_scale,
                                (255, 255, 255),
                                self.camera.text_thickness
                            )

                        cv2.imshow("Detection Raise-Your-Sign", frame)
                        cv2.waitKey(1)

                    self.quiz.record_answer(answer_index)
                    current_color_index = None

            self.release_resources()
            self.quiz.end([self.quiz.output_file])
            self.wait_player()

        except KeyboardInterrupt:
            self.quiz.inform_player(["\nQuiz exited with ^C"])
            if self.cap is not None:
                self.release_resources()
