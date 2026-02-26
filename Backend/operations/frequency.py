import numpy as np
import cv2
from scipy import fftpack
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def frequency_filter(image, filter_type='low', cutoff=30, filter_order=2):
    """
    Apply frequency domain filter
    filter_type: 'low' or 'high'
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Compute FFT
    f = fftpack.fft2(gray)
    fshift = fftpack.fftshift(f)
    
    # Create filter mask
    rows, cols = gray.shape
    crow, ccol = rows // 2, cols // 2
    
    # Create meshgrid for distance calculation
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    
    if filter_type == 'low':
        # Ideal low-pass filter
        mask = distance <= cutoff
    else:
        # Ideal high-pass filter
        mask = distance > cutoff
    
    # Apply filter
    fshift_filtered = fshift * mask
    
    # Inverse FFT
    f_ishift = fftpack.ifftshift(fshift_filtered)
    img_filtered = fftpack.ifft2(f_ishift)
    img_filtered = np.abs(img_filtered)
    
    # Normalize
    img_filtered = (img_filtered - img_filtered.min()) / (img_filtered.max() - img_filtered.min()) * 255
    img_filtered = img_filtered.astype(np.uint8)
    
    return img_filtered

def apply_frequency_filter(image, filter_type='low', cutoff=30):
    """
    Apply frequency filter and return visualization of frequency spectrum
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Compute FFT
    f = fftpack.fft2(gray)
    fshift = fftpack.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
    
    # Create filter
    rows, cols = gray.shape
    crow, ccol = rows // 2, cols // 2
    y, x = np.ogrid[:rows, :cols]
    distance = np.sqrt((x - ccol)**2 + (y - crow)**2)
    
    if filter_type == 'low':
        mask = distance <= cutoff
    else:
        mask = distance > cutoff
    
    # Apply filter
    fshift_filtered = fshift * mask
    magnitude_filtered = 20 * np.log(np.abs(fshift_filtered) + 1)
    
    # Inverse FFT
    f_ishift = fftpack.ifftshift(fshift_filtered)
    img_filtered = fftpack.ifft2(f_ishift)
    img_filtered = np.abs(img_filtered)
    
    # Normalize
    img_filtered = (img_filtered - img_filtered.min()) / (img_filtered.max() - img_filtered.min()) * 255
    img_filtered = img_filtered.astype(np.uint8)
    
    # Create visualization
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title('Original Frequency Spectrum')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.imshow(mask, cmap='gray')
    plt.title(f'{filter_type.capitalize()}-pass Filter Mask')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.imshow(magnitude_filtered, cmap='gray')
    plt.title('Filtered Frequency Spectrum')
    plt.axis('off')
    
    plt.tight_layout()
    
    # Convert to base64
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    spectrum_base64 = base64.b64encode(buf.getvalue()).decode()
    plt.close()
    
    return img_filtered, spectrum_base64