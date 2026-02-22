"""Edge detection kernels and helpers.

Sobel, Roberts, and Prewitt are implemented with custom kernels and filter2D.
"""

import cv2
import numpy as np


def _apply_kernel(gray: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    # Convolve grayscale image with a kernel.
    return cv2.filter2D(gray, cv2.CV_16S, kernel)


def edge_sobel(gray: np.ndarray, ksize: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Compute Sobel gradients and magnitude.
    if ksize % 2 == 0:
        ksize += 1
    gx = cv2.getDerivKernels(1, 0, ksize)
    gy = cv2.getDerivKernels(0, 1, ksize)
    kx = np.outer(gx[0], gx[1]).astype(np.float32)
    ky = np.outer(gy[0], gy[1]).astype(np.float32)

    # Convolve with custom kernels to obtain x/y gradients.
    grad_x = _apply_kernel(gray, kx)
    grad_y = _apply_kernel(gray, ky)
    mag = cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32))
    mag = np.clip(mag, 0, 255).astype(np.uint8)
    return (cv2.convertScaleAbs(grad_x), cv2.convertScaleAbs(grad_y), mag)


def edge_roberts(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Compute Roberts gradients and magnitude.
    kx = np.array([[1, 0], [0, -1]], dtype=np.float32)
    ky = np.array([[0, 1], [-1, 0]], dtype=np.float32)
    grad_x = _apply_kernel(gray, kx)
    grad_y = _apply_kernel(gray, ky)
    mag = cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32))
    mag = np.clip(mag, 0, 255).astype(np.uint8)
    return (cv2.convertScaleAbs(grad_x), cv2.convertScaleAbs(grad_y), mag)


def edge_prewitt(gray: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Compute Prewitt gradients and magnitude.
    kx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], dtype=np.float32)
    ky = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]], dtype=np.float32)
    grad_x = _apply_kernel(gray, kx)
    grad_y = _apply_kernel(gray, ky)
    mag = cv2.magnitude(grad_x.astype(np.float32), grad_y.astype(np.float32))
    mag = np.clip(mag, 0, 255).astype(np.uint8)
    return (cv2.convertScaleAbs(grad_x), cv2.convertScaleAbs(grad_y), mag)


def edge_canny(gray: np.ndarray, low: int, high: int) -> np.ndarray:
    # Run OpenCV Canny.
    return cv2.Canny(gray, low, high)
