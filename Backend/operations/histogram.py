import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .utils import fig_to_base64


def draw_histogram(image, title="Histogram", bins=256):
    """
    Draw a grayscale histogram for the given image.
    Returns a base64-encoded PNG string.
    """
    # Convert to grayscale if color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Create figure
    plt.figure(figsize=(10, 6))

    # Histogram
    plt.hist(gray.ravel(), bins, [0, 256], color='blue', alpha=0.7)
    plt.title(f'{title}')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 256])

    plt.tight_layout()
    return fig_to_base64()
