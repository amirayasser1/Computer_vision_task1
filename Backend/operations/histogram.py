import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def calculate_histogram(image, bins=256):
    """Calculate histogram for grayscale image"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    hist = cv2.calcHist([gray], [0], None, [bins], [0, 256])
    return hist.flatten()

def calculate_cdf(hist):
    """Calculate Cumulative Distribution Function from histogram"""
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()
    return cdf_normalized

def draw_histogram(image, title="Histogram", bins=256):
    """Draw histogram and CDF for image"""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    hist = cv2.calcHist([gray], [0], None, [bins], [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf.max()
    
    plt.figure(figsize=(10, 5))
    
    # Histogram
    plt.subplot(1, 2, 1)
    plt.hist(gray.ravel(), bins, [0, 256], color='blue', alpha=0.7)
    plt.title(f'{title} - Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.grid(True, alpha=0.3)
    
    # CDF
    plt.subplot(1, 2, 2)
    plt.plot(cdf_normalized, color='red', linewidth=2)
    plt.title(f'{title} - Cumulative Distribution Function')
    plt.xlabel('Pixel Value')
    plt.ylabel('CDF')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1.05)
    
    plt.tight_layout()
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    
    return img_base64