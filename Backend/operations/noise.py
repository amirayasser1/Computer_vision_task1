import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image

def add_noise(image, noise_type, params=None):
    """
    Add noise to image using OpenCV
    
    Parameters:
    - image: numpy array (RGB or Grayscale)
    - noise_type: 'gaussian', 'uniform', 'salt_pepper'
    - params: dictionary with parameters
    """
    if params is None:
        params = {}
    
    # Convert to float for processing
    img_float = image.astype(np.float32)
    noisy = img_float.copy()
    
    if noise_type == 'gaussian':
        mean = params.get('mean', 0)
        sigma = params.get('sigma', 25)
        # Validate range (0-50 for sigma)
        sigma = max(0, min(50, sigma))
        gauss = np.random.normal(mean, sigma, img_float.shape)
        noisy = img_float + gauss
        
    elif noise_type == 'uniform':
        low = params.get('low', -25)
        high = params.get('high', 25)
        uniform = np.random.uniform(low, high, img_float.shape)
        noisy = img_float + uniform
        
    elif noise_type == 'salt_pepper':
        ratio = params.get('ratio', 0.05)
        # Validate range (0-0.1)
        ratio = max(0, min(0.1, ratio))
        salt_vs_pepper = params.get('salt_vs_pepper', 0.5)
        
        # Create salt & pepper noise
        salt_pepper = np.random.random(img_float.shape[:2])
        if len(img_float.shape) == 3:
            salt_pepper = np.expand_dims(salt_pepper, axis=2)
            salt_pepper = np.repeat(salt_pepper, 3, axis=2)
        
        noisy = img_float.copy()
        # Salt (white)
        noisy[salt_pepper < ratio * salt_vs_pepper] = 255
        # Pepper (black)
        noisy[salt_pepper > 1 - ratio * (1 - salt_vs_pepper)] = 0
    
    # Clip values to valid range
    noisy = np.clip(noisy, 0, 255).astype(np.uint8)
    return noisy

def image_to_base64(image):
    """Convert numpy image to base64 string"""
    if len(image.shape) == 2:
        img_pil = Image.fromarray(image)
    else:
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    buffered = BytesIO()
    img_pil.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()