import numpy as np
import cv2

def apply_average_filter(image, kernel_size=3):
    """
    Apply average (mean) filter using OpenCV
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure odd kernel size
    return cv2.blur(image, (kernel_size, kernel_size))


def apply_gaussian_filter(image, kernel_size=3, sigma=1.0):
    """
    Apply Gaussian filter using OpenCV
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigmaX=sigma, sigmaY=sigma)


def apply_median_filter(image, kernel_size=3):
    """
    Apply median filter using OpenCV
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(image, kernel_size)