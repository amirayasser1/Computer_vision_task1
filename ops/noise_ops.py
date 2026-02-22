import cv2
import numpy as np


def add_uniform_noise(image: np.ndarray, low: int, high: int) -> np.ndarray:
    base = image.astype(np.int16)
    noise = np.empty(image.shape, dtype=np.int16)
    cv2.randu(noise, low, high + 1)
    noisy = base + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def add_gaussian_noise(image: np.ndarray, mean: float, sigma: float) -> np.ndarray:
    base = image.astype(np.float32)
    noise = np.empty(image.shape, dtype=np.float32)
    cv2.randn(noise, mean, sigma)
    noisy = base + noise
    return np.clip(noisy, 0, 255).astype(np.uint8)


def add_salt_pepper_noise(image: np.ndarray, amount: float, salt_vs_pepper: float) -> np.ndarray:
    noisy = image.copy()
    if amount <= 0.0:
        return noisy

    height, width = image.shape[:2]
    rnd = np.empty((height, width), dtype=np.float32)
    cv2.randu(rnd, 0.0, 1.0)

    salt_thresh = amount * salt_vs_pepper
    salt_mask = cv2.compare(rnd, salt_thresh, cv2.CMP_LT)
    pepper_mask = cv2.compare(rnd, amount, cv2.CMP_LT)
    pepper_mask = cv2.bitwise_and(pepper_mask, cv2.bitwise_not(salt_mask))

    salt_src = np.full_like(image, 255)
    pepper_src = np.zeros_like(image)
    cv2.copyTo(salt_src, salt_mask, noisy)
    cv2.copyTo(pepper_src, pepper_mask, noisy)
    return noisy
