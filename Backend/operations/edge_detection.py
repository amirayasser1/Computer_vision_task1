import numpy as np
import cv2

def sobel_edge(image):
    """
    Sobel edge detection from scratch
    Returns: magnitude, gradient_x, gradient_y
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    gray = gray.astype(np.float32)
    
    # Sobel kernels
    kernel_x = np.array([[-1, 0, 1],
                         [-2, 0, 2],
                         [-1, 0, 1]], dtype=np.float32)
    
    kernel_y = np.array([[-1, -2, -1],
                         [0, 0, 0],
                         [1, 2, 1]], dtype=np.float32)
    
    # Apply convolution
    grad_x = convolve2d_edge(gray, kernel_x)
    grad_y = convolve2d_edge(gray, kernel_y)
    
    # Calculate magnitude
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    
    # Normalize gradients
    grad_x = np.abs(grad_x)
    grad_x = (grad_x / grad_x.max() * 255).astype(np.uint8)
    grad_y = (grad_y / grad_y.max() * 255).astype(np.uint8)
    
    return magnitude, grad_x, grad_y

def roberts_edge(image):
    """
    Roberts cross edge detection from scratch
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    gray = gray.astype(np.float32)
    
    # Roberts kernels
    kernel_x = np.array([[1, 0],
                         [0, -1]], dtype=np.float32)
    
    kernel_y = np.array([[0, 1],
                         [-1, 0]], dtype=np.float32)
    
    # Apply convolution
    grad_x = convolve2d_edge(gray, kernel_x, pad=0)
    grad_y = convolve2d_edge(gray, kernel_y, pad=0)
    
    # Calculate magnitude
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    
    grad_x = np.abs(grad_x)
    grad_x = (grad_x / grad_x.max() * 255).astype(np.uint8) if grad_x.max() > 0 else grad_x
    grad_y = (grad_y / grad_y.max() * 255).astype(np.uint8) if grad_y.max() > 0 else grad_y
    
    return magnitude, grad_x, grad_y

def prewitt_edge(image):
    """
    Prewitt edge detection from scratch
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    gray = gray.astype(np.float32)
    
    # Prewitt kernels
    kernel_x = np.array([[-1, 0, 1],
                         [-1, 0, 1],
                         [-1, 0, 1]], dtype=np.float32)
    
    kernel_y = np.array([[-1, -1, -1],
                         [0, 0, 0],
                         [1, 1, 1]], dtype=np.float32)
    
    # Apply convolution
    grad_x = convolve2d_edge(gray, kernel_x)
    grad_y = convolve2d_edge(gray, kernel_y)
    
    # Calculate magnitude
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    magnitude = (magnitude / magnitude.max() * 255).astype(np.uint8)
    
    grad_x = np.abs(grad_x)
    grad_x = (grad_x / grad_x.max() * 255).astype(np.uint8)
    grad_y = (grad_y / grad_y.max() * 255).astype(np.uint8)
    
    return magnitude, grad_x, grad_y

def canny_edge(image, threshold1=100, threshold2=200):
    """
    Canny edge detection using OpenCV
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    edges = cv2.Canny(gray, threshold1, threshold2)
    return edges

def convolve2d_edge(image, kernel, pad=1):
    """Helper function for edge detection convolution"""
    h, w = image.shape
    kernel_size = kernel.shape[0]
    pad_size = pad
    
    padded = np.pad(image, pad_size, mode='edge')
    result = np.zeros_like(image, dtype=np.float32)
    
    for i in range(h):
        for j in range(w):
            region = padded[i:i+kernel_size, j:j+kernel_size]
            result[i, j] = np.sum(region * kernel)
    
    return result