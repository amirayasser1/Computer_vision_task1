<div align="center">

# <img src="Frontend/img/logo-cv.png" width="50" alt="ImagePro Logo"> ImagePro

### Real-Time Image Processing Web Application

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)](https://scipy.org)

---

**ImagePro** is a full-stack web application for interactive image processing. Built with a **FastAPI** backend and a **vanilla JavaScript** frontend, it lets users upload images, apply various processing operations in real time, and instantly visualize the results — all through a clean, modern interface.

The edge detection module (Sobel, Roberts, Prewitt) features **custom kernel-based implementations built from scratch**, while other operations leverage established libraries like OpenCV, SciPy, and Matplotlib for reliability and performance.

[Getting Started](#quick-start) · [Features](#features--demos) · [Project Structure](#project-structure)

</div>

---

## Application Preview

### Home Page

A responsive landing page with animated sections, feature overview cards, and a team carousel.

<p align="center">
  <img src="assets/home_page.png" width="900" alt="ImagePro Home Page">
</p>

---

### Operations Workspace

Split-panel workspace with original and processed images side by side. A tabbed control panel lets users switch operations, adjust parameters, and apply transformations with undo/reset support.

<p align="center">
  <img src="assets/operations_page.png" width="900" alt="Operations Page">
</p>

<p align="center">
  <img src="assets/operations_empty.png" width="900" alt="Operations Page — Empty State">
</p>

---

## Features & Demos

---

### 1. Noise Generation

Adds artificial noise to images, useful for testing denoising algorithms.

- **Gaussian** — random values from a normal distribution, controlled by `mean` and `sigma`
- **Uniform** — equally distributed random values within a range
- **Salt & Pepper** — randomly sets pixels to pure white or pure black, controlled by `ratio`

> Uses `numpy.random` for noise generation with OpenCV for image handling.

<p align="center">
  <img src="assets/salt_pepper_noise.png" width="800" alt="Salt and Pepper Noise">
</p>

---

### 2. Spatial Filters

Smooths and denoises images using windowed filtering operations.

- **Average** — replaces each pixel with the mean of its neighbors (`cv2.blur`)
- **Gaussian** — weighted mean with a bell-curve kernel (`cv2.GaussianBlur`)
- **Median** — replaces each pixel with the median of its neighbors (`cv2.medianBlur`), excellent for removing salt & pepper noise

> Adjustable **kernel size** (3×3, 5×5, 7×7, etc.) controls filter strength.

<p align="center">
  <img src="assets/median_filter.png" width="800" alt="Median Filter">
</p>

---

### 3. Edge Detection

Identifies object boundaries where brightness changes sharply.

- **Sobel** — ⚡ **from scratch** — uses hand-built 3×3 weighted kernels with custom convolution to detect horizontal and vertical edges. Returns magnitude + X/Y gradient maps.
- **Roberts** — ⚡ **from scratch** — uses hand-built 2×2 diagonal kernels with custom convolution. Fastest but most noise-sensitive.
- **Prewitt** — ⚡ **from scratch** — uses hand-built 3×3 equal-weight kernels with custom convolution. Similar to Sobel but without center emphasis.
- **Canny** — multi-stage pipeline via `cv2.Canny` with adjustable thresholds for clean, 1-pixel-wide edges.

> The custom `convolve2d_edge()` function handles the convolution for Sobel, Roberts, and Prewitt using `cv2.filter2D` with the manually defined kernels.

<p align="center">
  <img src="assets/canny_edge.png" width="800" alt="Canny Edge Detection">
</p>

---

### 4. Histogram Analysis & Visualization

Computes and displays pixel intensity distributions — essential for understanding exposure and contrast.

- **Grayscale** — histogram + CDF (Cumulative Distribution Function) curve
- **RGB** — individual R, G, B channel histograms + combined overlay

> Uses `cv2.calcHist` for computation and Matplotlib for visualization, rendered as base64 images.

<p align="center">
  <img src="assets/histogram_gray.png" width="800" alt="Grayscale Histogram">
</p>

<p align="center">
  <img src="assets/histogram_gray_eq.png" width="800" alt="Grayscale Histogram After Equalization">
</p>

<p align="center">
  <img src="assets/histogram_rgb_eq.png" width="800" alt="RGB Histogram After Equalization">
</p>

---

### 5. Image Enhancement

Improves visual quality through pixel-value transformations.

- **Histogram Equalization** — spreads pixel intensities evenly across 0–255 for better contrast (`cv2.equalizeHist`). For color images, only the Y channel in YUV space is equalized to preserve colors.
- **Normalization** — linearly scales pixel values to fill a target range (0–1 or 0–255)
- **Grayscale Conversion** — converts color images using the perceptual luminance formula: `0.299·R + 0.587·G + 0.114·B`

---

### 6. Frequency Domain Filtering

Transforms images to the frequency domain using **FFT** (via SciPy's `fftpack`), applies a circular mask, and converts back.

- **Low-pass** — keeps frequencies below `cutoff`, producing a blurred result
- **High-pass** — keeps frequencies above `cutoff`, isolating edges and textures

> Includes a 3-panel visualization showing the original spectrum, the filter mask, and the filtered spectrum. Processes all three RGB channels independently.

<p align="center">
  <img src="assets/frequency_filter.png" width="800" alt="Frequency Domain Filtering">
</p>

---

### 7. Hybrid Image Creation

Combines the **low frequencies** of one image with the **high frequencies** of another using FFT (SciPy). The result looks like one image up close and a different image from far away — exploiting how human vision prioritizes different frequency ranges at different distances.

---

## Project Structure

```
Computer_vision_task1/
│
├── Backend/
│   ├── main.py                  # FastAPI server & API routes
│   └── operations/
│       ├── noise.py             # Gaussian, Uniform, Salt & Pepper noise
│       ├── filters.py           # Average, Gaussian, Median filters (OpenCV)
│       ├── edge_detection.py    # Sobel, Roberts, Prewitt (from scratch) + Canny
│       ├── histogram.py         # Histogram & CDF computation (OpenCV + Matplotlib)
│       ├── enhancement.py       # Equalization, normalization (OpenCV)
│       ├── frequency.py         # FFT-based low/high-pass filtering (SciPy)
│       ├── hybrid.py            # Hybrid image creation (SciPy FFT)
│       └── color_space.py       # RGB/Grayscale conversions & RGB histograms
│
├── Frontend/
│   ├── index.html               # Landing page
│   ├── operation.html           # Image processing workspace
│   ├── project.html             # Project information page
│   ├── css/                     # Stylesheets
│   ├── js/
│   │   ├── main.js              # Home page animations
│   │   └── operation.js         # Core processing logic & API calls
│   └── lib/                     # Third-party libraries (Bootstrap, jQuery, etc.)
│
├── assets/                      # README screenshots
├── test_images/                 # Sample images for testing
└── requirements.txt             # Python dependencies
```

---

## Key Design Decisions

- **Session-based state** — each upload creates a unique `session_id` with the original image, working copy, and operation history stored in memory, enabling undo/reset without re-uploading.
- **Base64 transport** — processed images are encoded as base64 strings in JSON responses, eliminating the need for file serving.
- **Modular operations** — each algorithm category is in its own file under `operations/`, making it easy to add or modify operations independently.

---

## Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/Computer_vision_task1.git
cd Computer_vision_task1
```

### 2️⃣ Create & Activate a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

<details>
<summary><strong>Full dependency list</strong></summary>

| Package            | Purpose                                      |
| ------------------ | -------------------------------------------- |
| `fastapi`          | Web framework for the REST API               |
| `uvicorn`          | ASGI server to run FastAPI                   |
| `opencv-python`    | Image processing & computer vision           |
| `numpy`            | Array operations                             |
| `scipy`            | FFT for frequency domain operations          |
| `pillow`           | Image I/O utilities                          |
| `python-multipart` | Parsing multipart form uploads               |

</details>

### 4️⃣ Start the Server

```bash
cd Backend
uvicorn main:app --reload
```

### 5️⃣ Open the Application

Navigate to **http://127.0.0.1:8000** in your browser.

> **Tip:** The `--reload` flag enables hot-reloading during development.

---

## Usage Guide

1. **Open** the app and navigate to the **Operations** page
2. **Upload** an image via drag-and-drop or file browser
3. **Choose** an operation category from the tabs
4. **Adjust** parameters with sliders and inputs
5. **Apply** the operation — results appear instantly
6. **Chain** multiple operations sequentially
7. **Undo** the last operation or **Reset** to the original at any time

---

## Contributors

This project was developed as part of a **Computer Vision** university course assignment.

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

</div>
