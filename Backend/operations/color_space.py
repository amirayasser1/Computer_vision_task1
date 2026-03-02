import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .utils import fig_to_base64


def rgb_to_grayscale(image):
    """
    Convert RGB to Grayscale using the perceptual luminance formula.
    Weights: 0.299*R + 0.587*G + 0.114*B
    """
    if len(image.shape) == 2:
        return image

    gray = np.dot(image[..., :3], [0.299, 0.587, 0.114])
    return gray.astype(np.uint8)


def plot_rgb_histograms(image):
    """
    Plot individual R, G, B histograms and their Cumulative Distribution Functions (CDFs).
    Returns a base64-encoded PNG string, or None if the image is grayscale.
    """
    if len(image.shape) == 2:
        return None

    colors = ('b', 'g', 'r')
    color_names = ('Blue', 'Green', 'Red')
    plt.figure(figsize=(18, 10))

    # Compute histograms and CDFs
    histograms = []
    cdfs = []
    for i in range(3):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        histograms.append(hist)
        
        cdf = hist.cumsum()
        cdfs.append(cdf / cdf.max())

    for i, color in enumerate(colors):
        # Top Row: Histogram
        plt.subplot(2, 3, i + 1)
        plt.plot(histograms[i], color=color, linewidth=2)
        plt.title(f'{color_names[i]} Channel Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 256])

        # Bottom Row: CDF
        plt.subplot(2, 3, i + 4)
        plt.plot(cdfs[i], color=color, linewidth=2)
        plt.fill_between(range(256), cdfs[i].flatten(), color=color, alpha=0.2)
        plt.title(f'{color_names[i]} Channel CDF')
        plt.xlabel('Pixel Value')
        plt.ylabel('Cumulative Probability')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 256])
        plt.ylim([0, 1.05])

    plt.tight_layout()
    return fig_to_base64()


def plot_distribution_function(image):
    """
    Plot the Cumulative Distribution Function (CDF) for the image.
    Returns a base64-encoded PNG string.
    """
    # Convert to grayscale if color
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Compute histogram and CDF
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()

    # Plot CDF with filled area
    plt.figure(figsize=(10, 6))
    plt.plot(cdf_normalized, color='blue', linewidth=2)
    plt.fill_between(range(256), cdf_normalized.flatten(), alpha=0.3)
    plt.title('Cumulative Distribution Function (CDF)')
    plt.xlabel('Pixel Value')
    plt.ylabel('Cumulative Probability')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)

    return fig_to_base64()