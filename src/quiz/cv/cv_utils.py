"""Computer vision utility helpers for the CV quiz controllers.

This module provides configuration dataclasses and low-level image-processing
functions used for sign detection, masking and color surface computation
within the computer vision (CV) layer of the quiz controllers.
"""

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaskConfig:
    """Configuration parameters for sign mask extraction.

    This class groups all tunable parameters used in the edge-based
    detection pipeline that extracts the outer shape of a sign.

    Attributes:
        gaussian_kernel_size: Kernel size used for Gaussian blur.
        gaussian_sigma: Standard deviation for Gaussian blur.
        sobel_ddepth: Desired depth of the Sobel derivative images.
        edge_threshold: Threshold value used for gradient binarization.
        max_binary_value: Maximum binary value for thresholded images.
        morph_kernel_size: Kernel size for morphological operations.
        morph_operation: Morphological operation applied (e.g. closing).
        min_contour_area: Minimum contour area to be considered valid.
    """

    # Gaussian blur
    gaussian_kernel_size: tuple = (5, 5)
    gaussian_sigma: float = 0.0

    # Sobel operator
    sobel_ddepth: int = cv2.CV_32F

    # Gradient thresholding
    edge_threshold: int = 50
    max_binary_value: int = 255

    # Morphological closing
    morph_kernel_size: tuple = (7, 7)
    morph_operation: int = cv2.MORPH_CLOSE

    # Contour filtering
    min_contour_area: int = 5000


@dataclass(frozen=True)
class ColorRange:
    """HSV color range definition.

    Represents a lower and upper HSV boundary used for color segmentation.

    Attributes:
        lower: Lower HSV bound.
        upper: Upper HSV bound.
    """
    lower: np.ndarray
    upper: np.ndarray


@dataclass(frozen=True)
class ColorDetectionConfig:
    """Configuration parameters for color-based detection.

    This class defines HSV ranges for multiple colors as well as
    validation and filtering parameters used when detecting colored
    regions on signs.

    Attributes:
        red1: First HSV range for red color.
        red2: Second HSV range for red color (wrap-around).
        yellow: HSV range for yellow color.
        green: HSV range for green color.
        blue: HSV range for blue color.
        magenta: HSV range for magenta color.
        min_color_area: Minimum pixel surface for valid color detection.
        blur_big_sign: Median blur kernel size for large signs.
        blur_small_sign: Median blur kernel size for small signs.
    """

    # HSV color ranges
    red1: ColorRange = ColorRange(
        # np.array([0, 170, 100]), np.array([10, 255, 255])
        np.array([0, 170, 100]), np.array([6, 255, 255])
    )
    red2: ColorRange = ColorRange(
        # np.array([170, 170, 100]), np.array([180, 255, 255])
        np.array([170, 170, 100]), np.array([180, 255, 255])
    )
    yellow: ColorRange = ColorRange(
        # np.array([15, 150, 150]), np.array([32, 255, 255])
        np.array([12, 90, 70]), np.array([30, 255, 255])
    )
    green: ColorRange = ColorRange(
        # np.array([40, 100, 50]), np.array([80, 255, 255])
        np.array([40, 100, 50]), np.array([80, 255, 255])
    )
    blue: ColorRange = ColorRange(
        # np.array([100, 180, 60]), np.array([130, 255, 255])
        # np.array([100, 180, 50]), np.array([140, 255, 255])
        np.array([95, 150, 125]), np.array([115, 255, 255])
    )
    magenta: ColorRange = ColorRange(
        # np.array([145, 150, 100]), np.array([170, 255, 255])
        # np.array([145, 150, 120]), np.array([165, 255, 255])
        np.array([150, 135, 120]), np.array([170, 255, 255])
    )

    # Pixel area validation
    min_color_area: int = 30_000

    # Median blur sizes
    blur_big_sign: int = 7
    blur_small_sign: int = 15


@dataclass(frozen=True)
class CameraConfig:
    """Configuration parameters for camera visualization and ROI handling.

    This class stores constants related to region-of-interest (ROI)
    definition and overlay rendering on camera frames.

    Attributes:
        roi_width_ratio: Width ratio of the ROI relative to frame width.
        roi_height_ratio: Height ratio of the ROI relative to frame height.
        rectangle_color: BGR color of the ROI rectangle.
        rectangle_thickness: Thickness of the ROI rectangle border.
        text_font: OpenCV font used for overlay text.
        text_scale: Scale factor for overlay text.
        text_thickness: Thickness of overlay text strokes.
    """
    roi_width_ratio: float = 0.5
    roi_height_ratio: float = 0.5

    rectangle_color: tuple = (255, 255, 255)
    rectangle_thickness: int = 2

    text_font = cv2.FONT_HERSHEY_DUPLEX
    text_scale: float = 1.0
    text_thickness: int = 1


def get_sign_mask(image: np.ndarray, config: MaskConfig) -> np.ndarray | None:
    """Create the binary mask of a sign showing on the picture.

    Detects the outer border of a sign and returns a binary mask
    (white shape on black background).

    Args:
        image: Cropped BGR image where the sign is expected.
        config: MaskConfig containing all algorithm parameters.

    Returns:
        Binary mask (uint8) with the detected sign filled in white (255),
        None if no valid contour is found.
    """
    # Convert to grayscale and smooth
    gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_gray_img = cv2.GaussianBlur(
        gray_img,
        config.gaussian_kernel_size,
        config.gaussian_sigma
    )
    # Sobel gradients
    gx = cv2.Sobel(
        blurred_gray_img,
        config.sobel_ddepth,
        1, 0
    )
    gy = cv2.Sobel(
        blurred_gray_img,
        config.sobel_ddepth,
        0, 1
    )
    # Gradient magnitude and normalization
    gradient_magnitude = cv2.sqrt(gx ** 2 + gy ** 2)
    mag_norm = cv2.normalize(
        gradient_magnitude,
        None,
        0,
        config.max_binary_value,
        cv2.NORM_MINMAX,
        cv2.CV_8U
    )
    # Binary thresholding
    _, threshold = cv2.threshold(
        mag_norm,
        config.edge_threshold,
        config.max_binary_value,
        cv2.THRESH_BINARY
    )
    # Fill noisy gaps inside the sign's border using morphological closing
    kernel = np.ones(config.morph_kernel_size, np.uint8)
    closing = cv2.morphologyEx(
        threshold,
        config.morph_operation,
        kernel
    )
    # Contours extraction from the sign shape obtained
    # with moprhological closing.
    #
    # Uses `cv2.RETR_EXTERNAL` to only retrive external countours
    # and `cv2.CHAIN_APPROX_SIMPLE` to reduce the amount of pixels
    # used to represent the contours (eg. only store the 4 corners
    # if the sign is rectangular).
    contours, _ = cv2.findContours(
        closing,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None

    # Select the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_contour) <= config.min_contour_area:
        return None

    # Create the sign's binary mask with the largest countour
    mask = np.zeros_like(gray_img)
    cv2.drawContours(
        mask,
        [largest_contour],
        -1,
        config.max_binary_value,
        thickness=-1
    )
    return mask


def compute_color_surface(
        hsv_img: Any,
        color: ColorRange,
        blur_ksize: int
) -> int:
    """Compute the pixel surface of a given color range.

    This function thresholds an HSV image using the provided color range,
    applies median blurring and returns the summed pixel intensity.

    Args:
        hsv_img: HSV image used for color segmentation.
        color: ColorRange defining the HSV boundaries.
        blur_ksize: Kernel size for median blur.

    Returns:
        The summed pixel surface of the detected color region.
    """
    mask = cv2.inRange(hsv_img, color.lower, color.upper)
    mask = cv2.medianBlur(mask, blur_ksize)
    return int(np.sum(mask))


def compute_red_surface(
        hsv_img: Any,
        red1: ColorRange,
        red2: ColorRange,
        blur_ksize: int
) -> int:
    """Compute the pixel surface of red color using dual HSV ranges.

    This function handles the HSV wrap-around of red by combining two
    separate red masks before blurring and surface computation.

    Args:
        hsv_img: HSV image used for color segmentation.
        red1: First red HSV range.
        red2: Second red HSV range.
        blur_ksize: Kernel size for median blur.

    Returns:
        The summed pixel surface of the detected red regions.
    """
    mask1 = cv2.inRange(hsv_img, red1.lower, red1.upper)
    mask2 = cv2.inRange(hsv_img, red2.lower, red2.upper)
    merged = cv2.addWeighted(mask1, 1.0, mask2, 1.0, 0)
    merged = cv2.medianBlur(merged, blur_ksize)
    return int(np.sum(merged))
