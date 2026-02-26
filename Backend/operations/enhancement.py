import numpy as np
import cv2

def histogram_equalization(image):
    """
    Apply histogram equalization
    """
    if len(image.shape) == 3:
        # Convert to YUV and equalize Y channel
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
        result = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
    else:
        result = cv2.equalizeHist(image)
    
    return result

def normalize_image(image, range_type='0-1'):
    """
    Normalize image to 0-1 or 0-255 range
    """
    img_float = image.astype(np.float32)
    
    if range_type == '0-1':
        # Normalize to [0, 1]
        if img_float.max() > 0:
            normalized = (img_float - img_float.min()) / (img_float.max() - img_float.min())
        else:
            normalized = img_float
    else:
        # Normalize to [0, 255]
        if img_float.max() > 0:
            normalized = (img_float - img_float.min()) / (img_float.max() - img_float.min()) * 255
        else:
            normalized = img_float
    
    return normalized.astype(np.uint8)