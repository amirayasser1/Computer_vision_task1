// Image Processing Application JavaScript

// Global variables
let sessionId = null;
let originalImage = null;
let workingImage = null;
let currentOperation = null;
let isLoading = false;

// API Base URL
const API_BASE = 'http://localhost:8000';

// DOM Elements
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeTooltips();
    initializeRadioButtons();
    initializeTabs();
    addKeyboardShortcutTooltips();
});

function initializeEventListeners() {
    // Upload area click
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (uploadArea) {
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('drop', handleDrop);
    }
    
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
    
    // Radio button change events
    document.querySelectorAll('.operation-radio').forEach(radio => {
        radio.addEventListener('change', handleRadioChange);
    });
    
    // Parameter sliders
    document.querySelectorAll('.parameter-slider').forEach(slider => {
        slider.addEventListener('input', updateSliderValue);
    });
    
    // Apply buttons
    const applyNoiseBtn = document.getElementById('applyNoise');
    if (applyNoiseBtn) applyNoiseBtn.addEventListener('click', applyNoise);
    
    const applyFilterBtn = document.getElementById('applyFilter');
    if (applyFilterBtn) applyFilterBtn.addEventListener('click', applyFilter);
    
    const applyEdgeBtn = document.getElementById('applyEdge');
    if (applyEdgeBtn) applyEdgeBtn.addEventListener('click', applyEdgeDetection);
    
    const applyHistogramBtn = document.getElementById('applyHistogram');
    if (applyHistogramBtn) applyHistogramBtn.addEventListener('click', showHistogram);
    
    const applyEnhancementBtn = document.getElementById('applyEnhancement');
    if (applyEnhancementBtn) applyEnhancementBtn.addEventListener('click', applyEnhancement);
    
    const applyFrequencyBtn = document.getElementById('applyFrequency');
    if (applyFrequencyBtn) applyFrequencyBtn.addEventListener('click', applyFrequencyFilter);
    
    const createHybridBtn = document.getElementById('createHybrid');
    if (createHybridBtn) createHybridBtn.addEventListener('click', createHybridImage);
    
    // Undo/Reset buttons
    const undoBtn = document.getElementById('undoBtn');
    if (undoBtn) undoBtn.addEventListener('click', undo);
    
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) resetBtn.addEventListener('click', reset);
}

function initializeTabs() {
    // Initialize Bootstrap tabs
    const triggerTabList = [].slice.call(document.querySelectorAll('#operationTabs button'));
    triggerTabList.forEach(function(triggerEl) {
        const tabTrigger = new bootstrap.Tab(triggerEl);
        
        triggerEl.addEventListener('click', function(event) {
            event.preventDefault();
            tabTrigger.show();
        });
    });

    // Store current active tab in session storage
    const tabs = document.querySelectorAll('#operationTabs .nav-link');
    tabs.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const targetId = event.target.getAttribute('data-bs-target');
            sessionStorage.setItem('activeOperationTab', targetId);
        });
    });

    // Restore last active tab
    const lastActiveTab = sessionStorage.getItem('activeOperationTab');
    if (lastActiveTab) {
        const tabToActivate = document.querySelector(`[data-bs-target="${lastActiveTab}"]`);
        if (tabToActivate) {
            const tab = new bootstrap.Tab(tabToActivate);
            tab.show();
        }
    }
}





function initializeRadioButtons() {
    // Set default selections
    const defaultNoise = document.querySelector('input[name="noiseType"][value="gaussian"]');
    if (defaultNoise) defaultNoise.checked = true;
    
    const defaultFilter = document.querySelector('input[name="filterType"][value="average"]');
    if (defaultFilter) defaultFilter.checked = true;
    
    const defaultEdge = document.querySelector('input[name="edgeType"][value="sobel"]');
    if (defaultEdge) defaultEdge.checked = true;
    
    const defaultHist = document.querySelector('input[name="histType"][value="grayscale"]');
    if (defaultHist) defaultHist.checked = true;
    
    const defaultEnhance = document.querySelector('input[name="enhanceType"][value="equalization"]');
    if (defaultEnhance) defaultEnhance.checked = true;
    
    const defaultFreq = document.querySelector('input[name="freqType"][value="low"]');
    if (defaultFreq) defaultFreq.checked = true;
    
    // Trigger change events to show correct parameter groups
    document.querySelectorAll('.operation-radio:checked').forEach(radio => {
        handleRadioChange({ target: radio });
    });
}

function handleRadioChange(event) {
    const radio = event.target;
    const name = radio.getAttribute('name');
    const paramGroupId = radio.getAttribute('data-param-group');
    
    // Hide all parameter groups for this radio group
    if (name) {
        document.querySelectorAll(`[id$="Params"], [id$="params"]`).forEach(group => {
            group.style.display = 'none';
        });
    }
    
    // Show the specific parameter group if it exists
    if (paramGroupId) {
        const paramGroup = document.getElementById(paramGroupId);
        if (paramGroup) {
            paramGroup.style.display = 'block';
        }
    }
}

function initializeTooltips() {
    // Add Arabic tooltips
    document.querySelectorAll('[data-arabic]').forEach(element => {
        const arabicText = element.getAttribute('data-arabic-text');
        if (arabicText) {
            element.setAttribute('title', arabicText);
        }
    });
}

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    if (!file.type.startsWith('image/')) {
        showError('Please upload an image file');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            sessionId = data.session_id;
            originalImage = data.original;
            workingImage = data.working;
            
            displayImages();
            hideLoading();
            showSuccess('Image uploaded successfully');
        } else {
            throw new Error(data.detail || 'Upload failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Display functions
function displayImages() {
    const originalImg = document.getElementById('originalImage');
    const workingImg = document.getElementById('workingImage');
    
    if (originalImg && originalImage) {
        originalImg.src = `data:image/png;base64,${originalImage}`;
    }
    
    if (workingImg && workingImage) {
        workingImg.src = `data:image/png;base64,${workingImage}`;
    }
}

function displayResult(imageBase64, elementId = 'resultImage') {
    const resultImg = document.getElementById(elementId);
    const saveBtn = document.querySelector(`[onclick*="saveImage"][onclick*="${elementId}"]`);
    
    if (resultImg) {
        resultImg.src = `data:image/png;base64,${imageBase64}`;
        resultImg.style.display = 'block';
    }
    
    if (saveBtn) {
        saveBtn.style.display = 'inline-block';
    }
}

function displayMultipleResults(results) {
    const container = document.getElementById('edgeResults');
    if (!container) return;
    
    container.innerHTML = '';
    
    if (results.type === 'multi') {
        const resultTypes = [
            { id: 'magnitude', label: 'Magnitude', img: results.magnitude },
            { id: 'grad_x', label: 'X Gradient', img: results.grad_x },
            { id: 'grad_y', label: 'Y Gradient', img: results.grad_y }
        ];
        
        resultTypes.forEach(result => {
            const col = document.createElement('div');
            col.className = 'col-12 col-lg-6';
            col.innerHTML = `
                <div class="result-item">
                    <h6>${result.label}</h6>
                    <img src="data:image/png;base64,${result.img}" class="img-fluid" onclick="saveImage(this.src, '${result.label.toLowerCase()}')">
                    <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, '${result.label.toLowerCase()}')">
                        <i class="fas fa-download"></i> Save
                    </button>
                </div>
            `;
            container.appendChild(col);
        });
    } else {
        container.innerHTML = `
            <div class="col-12">
                <div class="result-item">
                    <h6>Edges</h6>
                    <img src="data:image/png;base64,${results.edges}" class="img-fluid" onclick="saveImage(this.src, 'edges')">
                    <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'edges')">
                        <i class="fas fa-download"></i> Save
                    </button>
                </div>
            </div>
        `;
    }
}

function displayHistogramResults(histogram, cdf) {
    const container = document.getElementById('histogramResults');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-md-6">
            <div class="result-item">
                <h6>Histogram</h6>
                <img src="data:image/png;base64,${histogram}" class="img-fluid">
            </div>
        </div>
        <div class="col-md-6">
            <div class="result-item">
                <h6>CDF</h6>
                <img src="data:image/png;base64,${cdf}" class="img-fluid">
            </div>
        </div>
    `;
}

function displayRGBHistogram(rgbHist) {
    const container = document.getElementById('histogramResults');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-12">
            <div class="result-item">
                <h6>RGB Histograms</h6>
                <img src="data:image/png;base64,${rgbHist}" class="img-fluid">
            </div>
        </div>
    `;
}

function displayHybridResults(hybrid, lowFreq, highFreq) {
    const container = document.getElementById('hybridResults');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-md-4">
            <div class="result-item">
                <h6>Low Frequency</h6>
                <img src="data:image/png;base64,${lowFreq}" class="img-fluid" onclick="saveImage(this.src, 'low_freq')">
                <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'low_freq')">
                    <i class="fas fa-download"></i> Save
                </button>
            </div>
        </div>
        <div class="col-md-4">
            <div class="result-item">
                <h6>High Frequency</h6>
                <img src="data:image/png;base64,${highFreq}" class="img-fluid" onclick="saveImage(this.src, 'high_freq')">
                <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'high_freq')">
                    <i class="fas fa-download"></i> Save
                </button>
            </div>
        </div>
        <div class="col-md-4">
            <div class="result-item">
                <h6>Hybrid Result</h6>
                <img src="data:image/png;base64,${hybrid}" class="img-fluid" onclick="saveImage(this.src, 'hybrid')">
                <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'hybrid')">
                    <i class="fas fa-download"></i> Save
                </button>
            </div>
        </div>
    `;
}

function displayFrequencyResults(result, spectrum) {
    const container = document.getElementById('frequencyResults');
    if (!container) return;
    
    container.innerHTML = `
        <div class="col-md-6">
            <div class="result-item">
                <h6>Filtered Image</h6>
                <img src="data:image/png;base64,${result}" class="img-fluid" onclick="saveImage(this.src, 'filtered')">
                <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'filtered')">
                    <i class="fas fa-download"></i> Save
                </button>
            </div>
        </div>
        <div class="col-md-6">
            <div class="result-item">
                <h6>Frequency Spectrum</h6>
                <img src="data:image/png;base64,${spectrum}" class="img-fluid" onclick="saveImage(this.src, 'spectrum')">
                <button class="btn-save" onclick="saveImage(this.parentElement.querySelector('img').src, 'spectrum')">
                    <i class="fas fa-download"></i> Save
                </button>
            </div>
        </div>
    `;
}

function updateSliderValue(e) {
    const slider = e.target;
    const valueDisplay = document.getElementById(`${slider.id}Value`);
    if (valueDisplay) {
        valueDisplay.textContent = slider.value;
    }
}

// Operation functions
async function applyNoise() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const noiseRadio = document.querySelector('input[name="noiseType"]:checked');
    if (!noiseRadio) {
        showError('Please select noise type');
        return;
    }
    
    const noiseType = noiseRadio.value;
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('noise_type', noiseType);
    
    if (noiseType === 'gaussian') {
        formData.append('mean', document.getElementById('gaussianMean')?.value || 0);
        formData.append('sigma', document.getElementById('gaussianSigma')?.value || 25);
    } else if (noiseType === 'uniform') {
        formData.append('low', document.getElementById('uniformLow')?.value || -25);
        formData.append('high', document.getElementById('uniformHigh')?.value || 25);
    } else if (noiseType === 'salt_pepper') {
        formData.append('ratio', document.getElementById('spRatio')?.value || 0.05);
    }
    
    try {
        const response = await fetch(`${API_BASE}/add_noise`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.result;
            displayImages();
            displayResult(data.result);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function applyFilter() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const filterRadio = document.querySelector('input[name="filterType"]:checked');
    if (!filterRadio) {
        showError('Please select filter type');
        return;
    }
    
    const filterType = filterRadio.value;
    
    const kernelRadio = document.querySelector('input[name="kernelSize"]:checked');
    if (!kernelRadio) {
        showError('Please select kernel size');
        return;
    }
    
    const kernelSize = parseInt(kernelRadio.value);
    
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('filter_type', filterType);
    formData.append('kernel_size', kernelSize);
    
    if (filterType === 'gaussian') {
        const sigma = document.getElementById('gaussianFilterSigma')?.value || 1.0;
        formData.append('sigma', parseFloat(sigma));
    }
    
    try {
        const response = await fetch(`${API_BASE}/apply_filter`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.result;
            displayImages();
            displayResult(data.result);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function applyEdgeDetection() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const edgeRadio = document.querySelector('input[name="edgeType"]:checked');
    if (!edgeRadio) {
        showError('Please select edge detection method');
        return;
    }
    
    const edgeType = edgeRadio.value;
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('edge_type', edgeType);
    
    if (edgeType === 'canny') {
        formData.append('threshold1', document.getElementById('cannyThresh1')?.value || 100);
        formData.append('threshold2', document.getElementById('cannyThresh2')?.value || 200);
    }
    
    try {
        const response = await fetch(`${API_BASE}/edge_detection`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayMultipleResults(data.result);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function showHistogram() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const histRadio = document.querySelector('input[name="histType"]:checked');
    if (!histRadio) {
        showError('Please select histogram type');
        return;
    }
    
    const histType = histRadio.value;
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('hist_type', histType);
    
    try {
        const response = await fetch(`${API_BASE}/histogram`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            if (histType === 'grayscale') {
                displayHistogramResults(data.histogram, data.cdf);
            } else {
                displayRGBHistogram(data.rgb_histogram);
            }
            hideLoading();
            showSuccess('Histogram generated successfully');
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function applyEnhancement() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const enhanceRadio = document.querySelector('input[name="enhanceType"]:checked');
    if (!enhanceRadio) {
        showError('Please select enhancement type');
        return;
    }
    
    const enhanceType = enhanceRadio.value;
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('enhance_type', enhanceType);
    
    if (enhanceType === 'normalization') {
        const normRange = document.querySelector('input[name="normRange"]:checked')?.value || '0-1';
        formData.append('range_type', normRange);
    }
    
    try {
        const response = await fetch(`${API_BASE}/enhancement`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.result;
            displayImages();
            displayResult(data.result);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function applyFrequencyFilter() {
    if (!sessionId) {
        showError('Please upload an image first');
        return;
    }
    
    const freqRadio = document.querySelector('input[name="freqType"]:checked');
    if (!freqRadio) {
        showError('Please select filter type');
        return;
    }
    
    const filterType = freqRadio.value;
    const cutoff = document.getElementById('freqCutoff')?.value || 30;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('filter_type', filterType);
    formData.append('cutoff', parseInt(cutoff));
    
    try {
        const response = await fetch(`${API_BASE}/frequency`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.result;
            displayImages();
            displayFrequencyResults(data.result, data.spectrum);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function createHybridImage() {
    const fileInput1 = document.getElementById('hybridFile1');
    const fileInput2 = document.getElementById('hybridFile2');
    
    if (!fileInput1.files[0] || !fileInput2.files[0]) {
        showError('Please upload both images');
        return;
    }
    
    const cutoffLow = document.getElementById('hybridLowCutoff')?.value || 30;
    const cutoffHigh = document.getElementById('hybridHighCutoff')?.value || 10;
    
    showLoading();
    
    const formData = new FormData();
    formData.append('file1', fileInput1.files[0]);
    formData.append('file2', fileInput2.files[0]);
    formData.append('cutoff_low', parseInt(cutoffLow));
    formData.append('cutoff_high', parseInt(cutoffHigh));
    
    try {
        const response = await fetch(`${API_BASE}/hybrid`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayHybridResults(data.hybrid, data.low_freq, data.high_freq);
            hideLoading();
            showSuccess(data.message);
        } else {
            throw new Error(data.detail || 'Operation failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function undo() {
    if (!sessionId) {
        showError('No image to undo');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    
    try {
        const response = await fetch(`${API_BASE}/undo`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.working;
            displayImages();
            
            // Clear result displays
            const resultImg = document.getElementById('resultImage');
            if (resultImg) resultImg.style.display = 'none';
            
            document.getElementById('edgeResults').innerHTML = '';
            document.getElementById('histogramResults').innerHTML = '';
            document.getElementById('frequencyResults').innerHTML = '';
            document.getElementById('hybridResults').innerHTML = '';
            
            hideLoading();
            showSuccess('Undo successful');
        } else {
            throw new Error(data.detail || 'Undo failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

async function reset() {
    if (!sessionId) {
        showError('No image to reset');
        return;
    }
    
    showLoading();
    
    const formData = new FormData();
    formData.append('session_id', sessionId);
    
    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            workingImage = data.working;
            displayImages();
            
            // Clear result displays
            const resultImg = document.getElementById('resultImage');
            if (resultImg) resultImg.style.display = 'none';
            
            document.getElementById('edgeResults').innerHTML = '';
            document.getElementById('histogramResults').innerHTML = '';
            document.getElementById('frequencyResults').innerHTML = '';
            document.getElementById('hybridResults').innerHTML = '';
            
            hideLoading();
            showSuccess('Reset to original');
        } else {
            throw new Error(data.detail || 'Reset failed');
        }
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Utility functions
function showLoading() {
    isLoading = true;
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.classList.add('show');
    
    // Disable all operation buttons
    document.querySelectorAll('button:not(#uploadArea button)').forEach(btn => {
        btn.disabled = true;
    });
}

function hideLoading() {
    isLoading = false;
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.classList.remove('show');
    
    // Enable all operation buttons
    document.querySelectorAll('button:not(#uploadArea button)').forEach(btn => {
        btn.disabled = false;
    });
}

function showError(message) {
    // Create toast or alert
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed top-0 end-0 m-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <strong>Error!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed top-0 end-0 m-3';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <strong>Success!</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

function saveImage(src, filename) {
    const link = document.createElement('a');
    link.download = `imagepro_${filename}_${Date.now()}.png`;
    link.href = src;
    link.click();
}
// Hybrid Image Preview Functions
function previewHybridImage1(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const previewImg = document.getElementById('hybridImg1');
            const placeholder = document.getElementById('hybridPlaceholder1');
            
            previewImg.src = e.target.result;
            previewImg.style.display = 'block';
            placeholder.style.display = 'none';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

function previewHybridImage2(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const previewImg = document.getElementById('hybridImg2');
            const placeholder = document.getElementById('hybridPlaceholder2');
            
            previewImg.src = e.target.result;
            previewImg.style.display = 'block';
            placeholder.style.display = 'none';
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Reset hybrid previews (optional - call this after creating hybrid or when needed)
function resetHybridPreviews() {
    const previewImg1 = document.getElementById('hybridImg1');
    const previewImg2 = document.getElementById('hybridImg2');
    const placeholder1 = document.getElementById('hybridPlaceholder1');
    const placeholder2 = document.getElementById('hybridPlaceholder2');
    const fileInput1 = document.getElementById('hybridFile1');
    const fileInput2 = document.getElementById('hybridFile2');
    
    if (previewImg1) {
        previewImg1.src = '#';
        previewImg1.style.display = 'none';
    }
    if (placeholder1) {
        placeholder1.style.display = 'block';
    }
    
    if (previewImg2) {
        previewImg2.src = '#';
        previewImg2.style.display = 'none';
    }
    if (placeholder2) {
        placeholder2.style.display = 'block';
    }
    
    if (fileInput1) fileInput1.value = '';
    if (fileInput2) fileInput2.value = '';
}
// Export functions for global use
window.saveImage = saveImage;