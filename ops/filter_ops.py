"""Low-pass filtering helpers."""

import cv2
import numpy as np


def apply_average_filter(image: np.ndarray, ksize: int) -> np.ndarray:
    # Apply mean (box) filter.
    return cv2.blur(image, (ksize, ksize))


def apply_gaussian_filter(image: np.ndarray, ksize: int, sigma: float) -> np.ndarray:
    # Apply Gaussian smoothing.
    return cv2.GaussianBlur(image, (ksize, ksize), sigma)


def apply_median_filter(image: np.ndarray, ksize: int) -> np.ndarray:
    # Apply median filtering.
    return cv2.medianBlur(image, ksize)
