"""Image loading and color conversion helpers."""

import cv2
import numpy as np


def read_image_bgr(path: str) -> np.ndarray:
    # Load an image as BGR.
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Failed to read image.")
    return image


def to_gray(image_bgr: np.ndarray) -> np.ndarray:
    # Convert BGR to grayscale.
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
