import numpy as np
import cv2


def histogram_equalization(image):
    """
    Apply histogram equalization to improve contrast.
    For color images, only the Y (brightness) channel in YUV space is equalized
    to preserve the original colors.
    """
    if len(image.shape) == 3:
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
        return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    else:
        return cv2.equalizeHist(image)


def normalize_image(image, range_type='0-1'):
    """
    Normalize pixel values to a target range.
    Supported range_type: '0-1' or '0-255'.
    """
    img_float = image.astype(np.float32)

    # Guard against all-zero images (avoid division by zero)
    value_range = img_float.max() - img_float.min()
    if value_range == 0:
        return image.copy()

    # Normalize to [0, 1]
    normalized = (img_float - img_float.min()) / value_range

    # Scale to [0, 255] if requested
    if range_type != '0-1':
        normalized = normalized * 255

    return normalized.astype(np.uint8)