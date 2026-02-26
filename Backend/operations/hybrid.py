import numpy as np
import cv2
from scipy import fftpack

def create_hybrid_image(image1, image2, cutoff_low=30, cutoff_high=10):
    """
    Create hybrid image by combining low frequencies of image1 with high frequencies of image2
    """
    # Convert to grayscale if needed
    if len(image1.shape) == 3:
        img1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    else:
        img1_gray = image1.copy()
    
    if len(image2.shape) == 3:
        img2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
    else:
        img2_gray = image2.copy()
    
    # Resize image2 to match image1 if needed
    if img1_gray.shape != img2_gray.shape:
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
    
    # Get low frequency components of image1
    low_freq = get_low_frequencies(img1_gray, cutoff_low)
    
    # Get high frequency components of image2
    high_freq = get_high_frequencies(img2_gray, cutoff_high)
    
    # Combine
    hybrid = cv2.addWeighted(low_freq, 0.5, high_freq, 0.5, 0)
    
    # Prepare display images
    low_display = (low_freq - low_freq.min()) / (low_freq.max() - low_freq.min()) * 255
    high_display = (high_freq - high_freq.min()) / (high_freq.max() - high_freq.min()) * 255
    
    return {
        'hybrid': hybrid.astype(np.uint8),
        'low_freq': low_display.astype(np.uint8),
        'high_freq': high_display.astype(np.uint8)
    }

def get_low_frequencies(image, cutoff):
    """Extract low frequency components"""
    f = fftpack.fft2(image.astype(np.float32))
    fshift = fftpack.fftshift(f)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create low-pass mask
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    mask = distance <= cutoff
    
    fshift_filtered = fshift * mask
    
    # Inverse FFT
    f_ishift = fftpack.ifftshift(fshift_filtered)
    img_filtered = fftpack.ifft2(f_ishift)
    img_filtered = np.abs(img_filtered)
    
    return img_filtered

def get_high_frequencies(image, cutoff):
    """Extract high frequency components"""
    f = fftpack.fft2(image.astype(np.float32))
    fshift = fftpack.fftshift(f)
    
    rows, cols = image.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create high-pass mask
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    mask = distance > cutoff
    
    fshift_filtered = fshift * mask
    
    # Inverse FFT
    f_ishift = fftpack.ifftshift(fshift_filtered)
    img_filtered = fftpack.ifft2(f_ishift)
    img_filtered = np.abs(img_filtered)
    
    return img_filtered