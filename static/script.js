// API Base URL
const API_BASE = '';

// DOM Elements
const inputSection = document.getElementById('input-section');
const progressSection = document.getElementById('progress-section');
const resultSection = document.getElementById('result-section');
const errorSection = document.getElementById('error-section');

const videoUrlInput = document.getElementById('video-url');
const startBtn = document.getElementById('start-btn');
const downloadBtn = document.getElementById('download-btn');
const deleteBtn = document.getElementById('delete-btn');
const newProcessBtn = document.getElementById('new-process-btn');
const retryBtn = document.getElementById('retry-btn');

const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const progressPercentage = document.getElementById('progress-percentage');
const errorMessage = document.getElementById('error-message');

const resultVideo = document.getElementById('result-video');
const videoSource = document.getElementById('video-source');

// State
let currentTaskId = null;
let currentFilename = null;
let statusCheckInterval = null;
let isProcessing = false;

// Stage mapping
const stageMapping = {
    'started': 0,
    'downloading': 1,
    'transcribing': 2,
    'translating': 3,
    'generating_subtitles': 4,
    'burning_subtitles': 5
};

// Event Listeners
startBtn.addEventListener('click', startProcessing);
downloadBtn.addEventListener('click', downloadFile);
deleteBtn.addEventListener('click', deleteFile);
newProcessBtn.addEventListener('click', resetApp);
retryBtn.addEventListener('click', resetApp);

videoUrlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        startProcessing();
    }
});

// Warn before leaving page if processing
window.addEventListener('beforeunload', (e) => {
    if (isProcessing && currentTaskId) {
        e.preventDefault();
        e.returnValue = 'پردازش ویدئو در حال انجام است. آیا مطمئن هستید؟ (Video processing in progress. Are you sure?)';
        return e.returnValue;
    }
});

// Cancel task when page is closed/hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden && isProcessing && currentTaskId) {
        // Send cancel request when hiding
        cancelTask();
    } else if (!document.hidden && !isProcessing && !currentTaskId) {
        // When coming back to page and no task active, ensure clean state
        console.log('Tab became visible - ensuring clean state');
        if (errorSection && !errorSection.classList.contains('hidden') && 
            progressSection.classList.contains('hidden') && 
            resultSection.classList.contains('hidden')) {
            // If showing error but nothing is processing, reset to input
            resetApp();
        }
    }
});

// Also cancel on page unload (as backup)
window.addEventListener('unload', () => {
    if (isProcessing && currentTaskId) {
        cancelTask();
    }
});

// Functions
async function startProcessing() {
    const url = videoUrlInput.value.trim();
    
    if (!url) {
        alert('لطفاً آدرس ویدئو را وارد کنید');
        return;
    }

    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        alert('آدرس ویدئو باید با http:// یا https:// شروع شود');
        return;
    }

    // Disable button and show processing state
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="btn-text">در حال پردازش...</span><span class="btn-icon">⏳</span>';

    try {
        const response = await fetch(`${API_BASE}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();

        if (data.success) {
            currentTaskId = data.task_id;
            isProcessing = true;
            
            // Hide input, show progress
            inputSection.classList.add('hidden');
            progressSection.classList.remove('hidden');
            
            // Start polling for status
            startStatusPolling();
        } else {
            showError(data.error || 'خطا در شروع پردازش');
            resetButton();
        }
    } catch (error) {
        showError(`خطای شبکه: ${error.message}`);
        resetButton();
    }
}

function startStatusPolling() {
    statusCheckInterval = setInterval(checkStatus, 2000);
    checkStatus(); // Check immediately
}

async function checkStatus() {
    if (!currentTaskId) return;

    try {
        const response = await fetch(`${API_BASE}/api/status/${currentTaskId}`);
        const data = await response.json();

        updateProgress(data);

        if (data.status === 'completed') {
            clearInterval(statusCheckInterval);
            isProcessing = false;
            handleCompletion(data);
        } else if (data.status === 'failed') {
            clearInterval(statusCheckInterval);
            isProcessing = false;
            showError(data.message || 'خطا در پردازش ویدئو');
        } else if (data.status === 'not_found') {
            clearInterval(statusCheckInterval);
            isProcessing = false;
            showError('وضعیت تسک یافت نشد. لطفاً دوباره تلاش کنید.\n(Task not found. Server may have restarted. Please try again.)');
        } else if (data.status === 'cancelled') {
            clearInterval(statusCheckInterval);
            isProcessing = false;
            showError('پردازش توسط کاربر لغو شد (Processing cancelled by user)');
        }
    } catch (error) {
        console.error('Error checking status:', error);
        // If we get repeated errors, stop polling and show error
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            isProcessing = false;
            showError(`خطای شبکه: ${error.message}\nلطفاً دوباره تلاش کنید.`);
        }
    }
}

async function cancelTask() {
    if (!currentTaskId) return;
    
    try {
        // Use sendBeacon for reliable delivery even during page unload
        const cancelUrl = `${API_BASE}/api/cancel/${currentTaskId}`;
        
        if (navigator.sendBeacon) {
            // sendBeacon is better for unload events
            const blob = new Blob(['{}'], { type: 'application/json' });
            navigator.sendBeacon(cancelUrl, blob);
        } else {
            // Fallback to fetch
            fetch(cancelUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                keepalive: true
            }).catch(err => console.error('Error cancelling task:', err));
        }
        
        isProcessing = false;
    } catch (error) {
        console.error('Error cancelling task:', error);
    }
}

function updateProgress(data) {
    const progress = data.progress || 0;
    const message = data.message || 'در حال پردازش...';
    const status = data.status;

    // Update progress bar
    progressFill.style.width = `${progress}%`;
    progressPercentage.textContent = `${progress}%`;
    progressText.textContent = message;

    // Update stages
    const currentStageIndex = stageMapping[status] || 0;
    
    for (let i = 0; i <= 5; i++) {
        const stage = document.getElementById(`stage-${i}`);
        if (!stage) continue;
        
        stage.classList.remove('active', 'completed');
        
        if (i < currentStageIndex) {
            stage.classList.add('completed');
        } else if (i === currentStageIndex) {
            stage.classList.add('active');
        }
    }
}

function handleCompletion(data) {
    // Extract filename from response
    currentFilename = data.output_file;
    
    // Hide progress, show result
    progressSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    
    // Set video source
    videoSource.src = `${API_BASE}/api/preview/${currentFilename}`;
    resultVideo.load();
}

function showError(message) {
    inputSection.classList.add('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    
    errorMessage.textContent = message;
}

async function downloadFile() {
    if (!currentFilename) return;
    
    try {
        window.location.href = `${API_BASE}/api/download/${currentFilename}`;
    } catch (error) {
        alert(`خطا در دانلود فایل: ${error.message}`);
    }
}

async function deleteFile() {
    if (!currentFilename) return;
    
    if (!confirm('آیا مطمئن هستید که می‌خواهید فایل را از سرور حذف کنید?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/delete/${currentFilename}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(data.message);
            resetApp();
        } else {
            alert(data.error);
        }
    } catch (error) {
        alert(`خطا در حذف فایل: ${error.message}`);
    }
}

function resetApp() {
    // Clear state
    currentTaskId = null;
    currentFilename = null;
    isProcessing = false;
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
        statusCheckInterval = null;
    }
    
    // Reset UI
    videoUrlInput.value = '';
    resetButton();
    
    // Hide all sections except input
    inputSection.classList.remove('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Reset progress
    progressFill.style.width = '0%';
    progressPercentage.textContent = '0%';
    progressText.textContent = 'در حال آماده‌سازی...';
    
    // Reset all stages
    for (let i = 0; i <= 5; i++) {
        const stage = document.getElementById(`stage-${i}`);
        if (stage) {
            stage.classList.remove('active', 'completed');
        }
    }
}

function resetButton() {
    startBtn.disabled = false;
    startBtn.innerHTML = '<span class="btn-text">شروع پردازش</span><span class="btn-icon">▶</span>';
}

// Initialize app on load
window.addEventListener('DOMContentLoaded', () => {
    // Force clean state immediately when DOM is ready
    console.log('Initializing app...');
    
    // Ensure all sections are in correct initial state
    inputSection.classList.remove('hidden');
    progressSection.classList.add('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Clear any state
    currentTaskId = null;
    currentFilename = null;
    isProcessing = false;
    videoUrlInput.value = '';
    
    console.log('App initialized - ready to process videos');
});

// Health check after page fully loads
window.addEventListener('load', async () => {
    try {
        // Health check
        const response = await fetch(`${API_BASE}/api/health`);
        const data = await response.json();
        console.log('Service status:', data.status);
        
    } catch (error) {
        console.error('Service health check failed:', error);
    }
});
