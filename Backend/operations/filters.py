import numpy as np
import cv2

def apply_average_filter(image, kernel_size=3):
    """
    Apply average filter from scratch
    """
    if kernel_size % 2 == 0:
        kernel_size += 1  # Ensure odd kernel size
    
    kernel = np.ones((kernel_size, kernel_size), dtype=np.float32) / (kernel_size * kernel_size)
    return convolve2d_manual(image, kernel)

def apply_gaussian_filter(image, kernel_size=3, sigma=1.0):
    """
    Apply Gaussian filter from scratch
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    kernel = create_gaussian_kernel(kernel_size, sigma)
    return convolve2d_manual(image, kernel)

def apply_median_filter(image, kernel_size=3):
    """
    Apply median filter from scratch
    """
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    pad = kernel_size // 2
    if len(image.shape) == 3:
        h, w, c = image.shape
        result = np.zeros_like(image)
        for i in range(c):
            result[:,:,i] = median_filter_2d(image[:,:,i], kernel_size, pad)
    else:
        result = median_filter_2d(image, kernel_size, pad)
    
    return result

def median_filter_2d(image, kernel_size, pad):
    """Helper function for 2D median filter"""
    h, w = image.shape
    padded = np.pad(image, pad, mode='edge')
    result = np.zeros_like(image)
    
    for i in range(h):
        for j in range(w):
            window = padded[i:i+kernel_size, j:j+kernel_size]
            result[i, j] = np.median(window)
    
    return result

def create_gaussian_kernel(size, sigma=1.0):
    """Create Gaussian kernel"""
    kernel = np.zeros((size, size), dtype=np.float32)
    center = size // 2
    
    for i in range(size):
        for j in range(size):
            x, y = i - center, j - center
            kernel[i, j] = np.exp(-(x**2 + y**2) / (2 * sigma**2))
    
    kernel = kernel / np.sum(kernel)
    return kernel

def convolve2d_manual(image, kernel):
    """
    Manual 2D convolution
    """
    kernel_size = kernel.shape[0]
    pad = kernel_size // 2
    
    if len(image.shape) == 3:
        h, w, c = image.shape
        result = np.zeros_like(image, dtype=np.float32)
        for channel in range(c):
            result[:,:,channel] = convolve2d_single_channel(image[:,:,channel], kernel, pad)
    else:
        result = convolve2d_single_channel(image, kernel, pad)
    
    return np.clip(result, 0, 255).astype(np.uint8)

def convolve2d_single_channel(image, kernel, pad):
    """Single channel convolution"""
    h, w = image.shape
    padded = np.pad(image.astype(np.float32), pad, mode='edge')
    result = np.zeros_like(image, dtype=np.float32)
    kernel_size = kernel.shape[0]
    
    for i in range(h):
        for j in range(w):
            region = padded[i:i+kernel_size, j:j+kernel_size]
            result[i, j] = np.sum(region * kernel)
    
    return result