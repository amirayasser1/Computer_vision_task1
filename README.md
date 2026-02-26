# Image Processing Web Application

###  Overview
ImagePro is a comprehensive web-based image processing application built with FastAPI backend and vanilla JavaScript frontend. It implements various image processing operations from scratch, including noise addition, spatial filtering, edge detection, histogram analysis, frequency domain filtering, and hybrid image creation.

---
###  Home Page  

<p align="center">
  <img src="Home_page_UI.png" width="800">
</p>

---

###  Operations UI  

<p align="center">
  <img src="operation_UI.png" width="800">
</p>

---


##  Quick Start Guide

### Prerequisites
- Python 3.8 or higher  
- pip (Python package installer)  
- Modern web browser (Chrome, Firefox, Edge, etc.)

---

##  Setup Instructions

###  Windows

```bash
# Navigate to project root
cd ImageProcessingApp

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies (if requirements.txt exists)
pip install -r requirements.txt
```

---

##  Run the Application

After activating the virtual environment, start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

###  Command Explanation
- `main` → Name of the backend file (main.py)
- `app` → FastAPI instance inside main.py
- `--reload` → Automatically reloads the server when code changes (development mode)

If the server starts successfully, you will see:

```
Uvicorn running on http://127.0.0.1:8000
```

Now open your browser and visit:

```
http://127.0.0.1:8000
```

---

##  If Uvicorn Is Not Installed

Install it manually:

```bash
pip install uvicorn
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

---

✅ Your application should now be running successfully.
