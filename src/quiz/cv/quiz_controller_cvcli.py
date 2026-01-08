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

    def detect_color(self, roi, n_opts, color_detectors) -> int | None:
        sign_mask = get_sign_mask(roi, self.mask_config)
        if sign_mask is None:
            return None

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        hsv_masked = cv2.bitwise_and(hsv, hsv, mask=sign_mask)

        surfaces = [
            detector(hsv_masked)
            for _, detector in color_detectors[:n_opts]
        ]

        max_surface = max(surfaces)
        if max_surface <= self.colors.min_color_area:
            return None

        return surfaces.index(max_surface)

    def update_hold_timer(
            self,
            detected_index: int | None,
            current_color_index: int | None,
            timer: Timer
    ) -> tuple[int | None, bool]:
        """
        Returns:
        (new_current_color_index, validated)
        """
        if detected_index is None:
            timer.stop()
            return None, False

        if detected_index != current_color_index:
            timer.reset()
            return detected_index, False

        if timer.expired():
            return current_color_index, True

        return current_color_index, False

    def draw_progress_bar(self, frame: Any, progress: float) -> None:
        h = frame.shape[0]
        bar_w = int(200 * progress)
        cv2.rectangle(
            frame, (20, h - 40), (220, h - 20), (255, 255, 255), 2
        )
        cv2.rectangle(
            frame, (20, h - 40), (20 + bar_w, h - 20), (0, 255, 0), -1
        )

    def draw_answer_text(self, frame: Any, text: str) -> None:
        h, w = frame.shape[:2]
        ts, _ = cv2.getTextSize(
            text,
            self.camera.text_font,
            self.camera.text_scale,
            self.camera.text_thickness
        )
        x = max(10, (w - ts[0]) // 2)
        y = min(h - 10, int(h * 0.85))
        cv2.putText(
            frame, text, (x, y),
            self.camera.text_font,
            self.camera.text_scale,
            (255, 255, 255),
            self.camera.text_thickness
        )

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

                    while True:
                        ret, frame = self.cap.read()
                        if not ret:
                            continue

                        h, w = frame.shape[:2]
                        roi_w = int(w * self.camera.roi_width_ratio)
                        roi_h = int(h * self.camera.roi_height_ratio)
                        roi = frame[:roi_h, :roi_w]

                        detected_index = self.detect_color(
                            roi, n_opts, color_detectors
                        )

                        current_color_index, validated \
                            = self.update_hold_timer(
                                detected_index,
                                current_color_index,
                                hold_timer
                            )

                        if detected_index is not None:
                            answer = self.quiz.get_options()[detected_index]
                            color_name = color_detectors[detected_index][0]
                            text = f"{color_name}: {answer}"
                            self.draw_answer_text(frame, text)

                            if hold_timer.running() and not validated:
                                self.draw_progress_bar(
                                    frame, hold_timer.progress()
                                )

                        if validated:
                            answer_index = current_color_index
                            break

                        roi_w = roi.shape[1]
                        roi_h = roi.shape[0]
                        cv2.rectangle(
                            frame, (0, 0), (roi_w, roi_h),
                            self.camera.rectangle_color,
                            self.camera.rectangle_thickness
                        )

                        cv2.imshow("Detection Raise-Your-Sign", frame)
                        cv2.waitKey(1)

                    self.quiz.record_answer(answer_index)

            self.release_resources()
            self.quiz.end([self.quiz.output_file])
            self.wait_player()

        except KeyboardInterrupt:
            self.quiz.inform_player(["\nQuiz exited with ^C"])
            if self.cap is not None:
                self.release_resources()
