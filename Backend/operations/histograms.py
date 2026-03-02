import numpy as np
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


def plot_rgb_histograms(image):
    """
    Plot individual R, G, B histograms.
    Returns a base64-encoded PNG string, or None if the image is grayscale.
    """
    if len(image.shape) == 2:
        return None

    colors = ('b', 'g', 'r')
    color_names = ('Blue', 'Green', 'Red')
    plt.figure(figsize=(18, 5))

    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        
        plt.subplot(1, 3, i + 1)
        plt.plot(hist, color=color, linewidth=2)
        plt.title(f'{color_names[i]} Channel Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 256])

    plt.tight_layout()
    return fig_to_base64()


def plot_rgb_cdfs(image):
    """
    Plot individual R, G, B Cumulative Distribution Functions (CDFs).
    Returns a base64-encoded PNG string, or None if the image is grayscale.
    """
    if len(image.shape) == 2:
        return None

    colors = ('b', 'g', 'r')
    color_names = ('Blue', 'Green', 'Red')
    plt.figure(figsize=(18, 5))

    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        cdf = hist.cumsum()
        cdf_normalized = cdf / cdf.max()

        plt.subplot(1, 3, i + 1)
        plt.plot(cdf_normalized, color=color, linewidth=2)
        plt.fill_between(range(256), cdf_normalized.flatten(), color=color, alpha=0.2)
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
