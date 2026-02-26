from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import os
import uuid
from typing import Optional
import base64
from io import BytesIO
from PIL import Image

# Import operations explicitly
from operations.noise import add_noise
from operations.filters import apply_average_filter, apply_gaussian_filter, apply_median_filter
from operations.edge_detection import sobel_edge, roberts_edge, prewitt_edge, canny_edge
from operations.histogram import draw_histogram
from operations.enhancement import histogram_equalization, normalize_image
from operations.color_space import rgb_to_grayscale, plot_rgb_histograms, plot_distribution_function as color_plot_distribution
from operations.frequency import apply_frequency_filter
from operations.hybrid import create_hybrid_image

app = FastAPI(title="Image Processing API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories
UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)

# In-memory storage for images
image_states = {}

def read_image(file: UploadFile):
    """Read uploaded image and return as numpy array"""
    contents = file.file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def image_to_base64(image):
    """Convert numpy image to base64 string"""
    if len(image.shape) == 2:
        img_pil = Image.fromarray(image)
    else:
        img_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    buffered = BytesIO()
    img_pil.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload image and store in memory"""
    try:
        img = read_image(file)
        session_id = str(uuid.uuid4())
        
        # Store both original and working copy
        image_states[session_id] = {
            'original': img.copy(),
            'working': img.copy(),
            'history': [img.copy()]  # For undo functionality
        }
        
        return JSONResponse({
            'session_id': session_id,
            'original': image_to_base64(img),
            'working': image_to_base64(img),
            'message': 'Image uploaded successfully'
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/undo")
async def undo_image(session_id: str = Form(...)):
    """Undo last operation"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    if len(state['history']) > 1:
        # Remove current state
        state['history'].pop()
        # Restore previous state
        state['working'] = state['history'][-1].copy()
    
    return JSONResponse({
        'working': image_to_base64(state['working']),
        'message': 'Undo successful'
    })

@app.post("/reset")
async def reset_image(session_id: str = Form(...)):
    """Reset to original image"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    state['working'] = state['original'].copy()
    state['history'] = [state['original'].copy()]
    
    return JSONResponse({
        'working': image_to_base64(state['working']),
        'message': 'Reset to original'
    })

@app.post("/add_noise")
async def add_noise_endpoint(
    session_id: str = Form(...),
    noise_type: str = Form(...),
    mean: Optional[float] = Form(0),
    sigma: Optional[float] = Form(25),
    ratio: Optional[float] = Form(0.05)
):
    """Add noise to image"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    params = {}
    if noise_type == 'gaussian':
        params = {'mean': mean, 'sigma': sigma}
    elif noise_type == 'uniform':
        params = {'low': -25, 'high': 25}
    elif noise_type == 'salt_pepper':
        params = {'ratio': ratio, 'salt_vs_pepper': 0.5}
    
    result = add_noise(img, noise_type, params)
    
    # Update state
    state['working'] = result.copy()
    state['history'].append(result.copy())
    
    return JSONResponse({
        'result': image_to_base64(result),
        'message': f'{noise_type} noise added successfully'
    })

@app.post("/apply_filter")
async def apply_filter_endpoint(
    session_id: str = Form(...),
    filter_type: str = Form(...),
    kernel_size: int = Form(3),
    sigma: Optional[float] = Form(1.0)
):
    """Apply spatial filter"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    if filter_type == 'average':
        result = apply_average_filter(img, kernel_size)
    elif filter_type == 'gaussian':
        result = apply_gaussian_filter(img, kernel_size, sigma)
    elif filter_type == 'median':
        result = apply_median_filter(img, kernel_size)
    else:
        raise HTTPException(status_code=400, detail="Invalid filter type")
    
    # Update state
    state['working'] = result.copy()
    state['history'].append(result.copy())
    
    return JSONResponse({
        'result': image_to_base64(result),
        'message': f'{filter_type} filter applied'
    })

@app.post("/edge_detection")
async def edge_detection_endpoint(
    session_id: str = Form(...),
    edge_type: str = Form(...),
    threshold1: Optional[float] = Form(100),
    threshold2: Optional[float] = Form(200)
):
    """Apply edge detection"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    if edge_type == 'sobel':
        magnitude, grad_x, grad_y = sobel_edge(img)
        result = {
            'magnitude': image_to_base64(magnitude),
            'grad_x': image_to_base64(grad_x),
            'grad_y': image_to_base64(grad_y),
            'type': 'multi'
        }
    elif edge_type == 'roberts':
        magnitude, grad_x, grad_y = roberts_edge(img)
        result = {
            'magnitude': image_to_base64(magnitude),
            'grad_x': image_to_base64(grad_x),
            'grad_y': image_to_base64(grad_y),
            'type': 'multi'
        }
    elif edge_type == 'prewitt':
        magnitude, grad_x, grad_y = prewitt_edge(img)
        result = {
            'magnitude': image_to_base64(magnitude),
            'grad_x': image_to_base64(grad_x),
            'grad_y': image_to_base64(grad_y),
            'type': 'multi'
        }
    elif edge_type == 'canny':
        edges = canny_edge(img, threshold1, threshold2)
        result = {
            'edges': image_to_base64(edges),
            'type': 'single'
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid edge type")
    
    return JSONResponse({
        'result': result,
        'message': f'{edge_type} edge detection applied'
    })

@app.post("/histogram")
async def histogram_endpoint(
    session_id: str = Form(...),
    hist_type: str = Form('grayscale')
):
    """Generate histogram visualizations"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    if hist_type == 'grayscale':
        hist_img = draw_histogram(img, "Image Histogram")
        cdf_img = color_plot_distribution(img)
        return JSONResponse({
            'histogram': hist_img,
            'cdf': cdf_img
        })
    elif hist_type == 'rgb':
        rgb_hist = plot_rgb_histograms(img)
        return JSONResponse({
            'rgb_histogram': rgb_hist
        })
    else:
        raise HTTPException(status_code=400, detail="Invalid histogram type")

@app.post("/enhancement")
async def enhancement_endpoint(
    session_id: str = Form(...),
    enhance_type: str = Form(...),
    range_type: Optional[str] = Form('0-1')
):
    """Apply image enhancement"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    if enhance_type == 'equalization':
        result = histogram_equalization(img)
    elif enhance_type == 'normalization':
        result = normalize_image(img, range_type)
    elif enhance_type == 'grayscale':
        result = rgb_to_grayscale(img)
    else:
        raise HTTPException(status_code=400, detail="Invalid enhancement type")
    
    # Update state
    state['working'] = result.copy()
    state['history'].append(result.copy())
    
    return JSONResponse({
        'result': image_to_base64(result),
        'message': f'{enhance_type} applied successfully'
    })

@app.post("/frequency")
async def frequency_endpoint(
    session_id: str = Form(...),
    filter_type: str = Form('low'),
    cutoff: int = Form(30)
):
    """Apply frequency domain filter"""
    if session_id not in image_states:
        raise HTTPException(status_code=404, detail="Session not found")
    
    state = image_states[session_id]
    img = state['working'].copy()
    
    result, spectrum = apply_frequency_filter(img, filter_type, cutoff)
    
    # Update state
    state['working'] = result.copy()
    state['history'].append(result.copy())
    
    return JSONResponse({
        'result': image_to_base64(result),
        'spectrum': spectrum,
        'message': f'{filter_type}-pass filter applied'
    })

@app.post("/hybrid")
async def hybrid_endpoint(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    cutoff_low: int = Form(30),
    cutoff_high: int = Form(10)
):
    """Create hybrid image from two uploaded images"""
    try:
        img1 = read_image(file1)
        img2 = read_image(file2)
        
        result = create_hybrid_image(img1, img2, cutoff_low, cutoff_high)
        
        return JSONResponse({
            'hybrid': image_to_base64(result['hybrid']),
            'low_freq': image_to_base64(result['low_freq']),
            'high_freq': image_to_base64(result['high_freq']),
            'message': 'Hybrid image created successfully'
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)