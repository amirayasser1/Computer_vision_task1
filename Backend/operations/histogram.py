import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .utils import fig_to_base64


def draw_histogram(image, title="Histogram", bins=256):
    """
    Draw a grayscale histogram and CDF plot for the given image.
    Returns a base64-encoded PNG string.
    """
    # Convert to grayscale if color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Compute histogram and CDF
    hist = cv2.calcHist([gray], [0], None, [bins], [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()

    # Create figure with two subplots
    plt.figure(figsize=(10, 5))

    # Left: Histogram
    plt.subplot(1, 2, 1)
    plt.hist(gray.ravel(), bins, [0, 256], color='blue', alpha=0.7)
    plt.title(f'{title} - Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)

    # Right: CDF
    plt.subplot(1, 2, 2)
    plt.plot(cdf_normalized, color='red', linewidth=2)
    plt.title(f'{title} - Cumulative Distribution Function')
    plt.xlabel('Pixel Value')
    plt.ylabel('CDF')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)

    plt.tight_layout()
    return fig_to_base64()
