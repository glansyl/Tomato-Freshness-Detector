// Mode switching
const modeBtns = document.querySelectorAll('.mode-btn');
const modeContents = document.querySelectorAll('.mode-content');

modeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const mode = btn.dataset.mode;
        
        // Update active button
        modeBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active content
        modeContents.forEach(content => content.classList.remove('active'));
        document.getElementById(`${mode}-mode`).classList.add('active');
    });
});

// Upload functionality
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const previewContainer = document.getElementById('preview-container');
const previewImage = document.getElementById('preview-image');
const analyzeBtn = document.getElementById('analyze-btn');
const clearBtn = document.getElementById('clear-btn');
const resultsContainer = document.getElementById('results-container');
const processedImage = document.getElementById('processed-image');
const detectionsList = document.getElementById('detections-list');
const loadingOverlay = document.getElementById('loading-overlay');

let currentFile = null;

// Click to upload
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File input change
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        handleFile(file);
    }
});

function handleFile(file) {
    currentFile = file;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        previewContainer.style.display = 'block';
        resultsContainer.style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Clear button
clearBtn.addEventListener('click', () => {
    currentFile = null;
    fileInput.value = '';
    previewImage.src = '';
    processedImage.src = '';
    uploadArea.style.display = 'block';
    previewContainer.style.display = 'none';
    resultsContainer.style.display = 'none';
});

// Analyze button
analyzeBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    
    loadingOverlay.classList.add('active');
    
    const formData = new FormData();
    formData.append('image', currentFile);
    
    try {
        const response = await fetch('/analyze_image', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to analyze image. Please try again.');
    } finally {
        loadingOverlay.classList.remove('active');
    }
});

function displayResults(data) {
    // Show processed image
    processedImage.src = `data:image/jpeg;base64,${data.processed_image}`;
    
    // Display detections
    detectionsList.innerHTML = '';
    
    if (data.detections.length === 0) {
        detectionsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No tomatoes detected in the image.</p>';
    } else {
        data.detections.forEach((detection, index) => {
            const card = document.createElement('div');
            card.className = `detection-card ${detection.label}`;
            
            const confidence = (detection.confidence * 100).toFixed(1);
            
            card.innerHTML = `
                <div class="detection-label">🍅 Tomato #${index + 1}</div>
                <div style="margin: 10px 0;">
                    <strong>Status:</strong> ${detection.label}
                </div>
                <div class="detection-confidence">
                    <strong>Confidence:</strong> ${confidence}%
                </div>
                <div style="margin-top: 10px; font-size: 0.85rem; color: var(--text-secondary);">
                    Position: (${detection.bbox[0]}, ${detection.bbox[1]})
                </div>
            `;
            
            detectionsList.appendChild(card);
        });
    }
    
    resultsContainer.style.display = 'block';
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Check camera status on load
async function checkCameraStatus() {
    try {
        const response = await fetch('/camera_status');
        const data = await response.json();
        
        if (!data.available) {
            const statusIndicator = document.querySelector('.camera-status');
            if (statusIndicator) {
                statusIndicator.innerHTML = `
                    <div class="status-indicator" style="background: rgba(239, 68, 68, 0.2);">
                        <span class="status-dot" style="background: var(--danger);"></span>
                        <span class="status-text">Camera Unavailable</span>
                    </div>
                `;
            }
        }
    } catch (error) {
        console.error('Failed to check camera status:', error);
    }
}

// Initialize
checkCameraStatus();

// Reload video stream on error
const videoStream = document.getElementById('video-stream');
videoStream.addEventListener('error', () => {
    setTimeout(() => {
        videoStream.src = videoStream.src;
    }, 5000);
});
