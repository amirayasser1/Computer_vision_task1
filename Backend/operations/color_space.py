import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def rgb_to_grayscale(image):
    """
    Convert RGB to Grayscale using weighted sum
    """
    if len(image.shape) == 2:
        return image
    
    # Using standard weights: 0.299*R + 0.587*G + 0.114*B
    gray = np.dot(image[...,:3], [0.299, 0.587, 0.114])
    return gray.astype(np.uint8)

def plot_rgb_histograms(image):
    """
    Plot individual R, G, B histograms
    """
    if len(image.shape) == 2:
        return None
    
    colors = ('b', 'g', 'r')
    plt.figure(figsize=(12, 8))
    
    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        
        plt.subplot(2, 2, i+1)
        plt.plot(hist, color=color, linewidth=2)
        plt.title(f'{color.upper()} Channel Histogram')
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        plt.xlim([0, 256])
    
    # Combined histogram
    plt.subplot(2, 2, 4)
    for i, color in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        plt.plot(hist, color=color, linewidth=1.5, label=f'{color.upper()} channel')
    
    plt.title('Combined RGB Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 256])
    
    plt.tight_layout()
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    
    return img_base64

def plot_distribution_function(image):
    """
    Plot distribution function (CDF) for image
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()
    
    plt.figure(figsize=(10, 6))
    plt.plot(cdf_normalized, color='blue', linewidth=2)
    plt.fill_between(range(256), cdf_normalized.flatten(), alpha=0.3)
    plt.title('Cumulative Distribution Function (CDF)')
    plt.xlabel('Pixel Value')
    plt.ylabel('Cumulative Probability')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    
    return img_base64