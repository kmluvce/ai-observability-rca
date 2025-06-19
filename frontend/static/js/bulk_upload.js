// Bulk Upload JavaScript for RCA System
class BulkUploader {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.checkAPIHealth();
        this.selectedFiles = {};
    }

    initializeElements() {
        // Form elements
        this.uploadForm = document.getElementById('bulk-upload-form');
        this.fileInputs = {
            logs: document.getElementById('logs-file'),
            metrics: document.getElementById('metrics-file'),
            traces: document.getElementById('traces-file'),
            rca: document.getElementById('rca-file')
        };

        // Button elements
        this.uploadBtn = document.getElementById('upload-btn');
        this.clearFilesBtn = document.getElementById('clear-files-btn');
        this.viewDatabaseStatsBtn = document.getElementById('view-database-stats-btn');
        this.uploadMoreBtn = document.getElementById('upload-more-btn');

        // Status elements
        this.statusBar = document.getElementById('status-bar');
        this.statusText = document.getElementById('status-text');
        this.loadingSpinner = document.getElementById('loading-spinner');

        // Progress elements
        this.progressSection = document.getElementById('upload-progress-section');
        this.progressBarFill = document.getElementById('progress-bar-fill');
        this.progressText = document.getElementById('progress-text');

        // Results elements
        this.resultsSection = document.getElementById('upload-results-section');
        this.filesUploadedCount = document.getElementById('files-uploaded-count');
        this.recordsProcessedCount = document.getElementById('records-processed-count');
        this.uploadStatus = document.getElementById('upload-status');
        this.uploadedFilesList = document.getElementById('uploaded-files-list');

        // Database stats elements
        this.databaseStatsSection = document.getElementById('database-stats-section');
        this.databaseStatsContent = document.getElementById('database-stats-content');
    }

    attachEventListeners() {
        // Form submission
        this.uploadForm.addEventListener('submit', (e) => this.handleFormSubmit(e));

        // File input changes
        Object.entries(this.fileInputs).forEach(([type, input]) => {
            input.addEventListener('change', (e) => this.handleFileSelect(e, type));
        });

        // Button clicks
        this.clearFilesBtn.addEventListener('click', () => this.clearAllFiles());
        this.viewDatabaseStatsBtn.addEventListener('click', () => this.loadDatabaseStats());
        this.uploadMoreBtn.addEventListener('click', () => this.resetForNewUpload());

        // Custom file input styling
        this.setupCustomFileInputs();
    }

    setupCustomFileInputs() {
        Object.entries(this.fileInputs).forEach(([type, input]) => {
            const wrapper = input.closest('.file-input-wrapper');
            const display = wrapper.querySelector('.file-input-display');
            const placeholder = wrapper.querySelector('.file-placeholder');
            const browseBtn = wrapper.querySelector('.file-browse-btn');

            // Browse button click
            browseBtn.addEventListener('click', (e) => {
                e.preventDefault();
                input.click();
            });

            // Display click
            display.addEventListener('click', () => {
                input.click();
            });
        });
    }

    async checkAPIHealth() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                this.showStatus('System ready for bulk upload', 'success');
            } else {
                this.showStatus('API health check failed', 'error');
            }
        } catch (error) {
            this.showStatus('Unable to connect to API', 'error');
        }
    }

    handleFileSelect(event, fileType) {
        const file = event.target.files[0];
        const wrapper = event.target.closest('.file-input-wrapper');
        const display = wrapper.querySelector('.file-input-display');
        const placeholder = wrapper.querySelector('.file-placeholder');

        if (file) {
            // Store file reference
            this.selectedFiles[fileType] = file;

            // Update display
            placeholder.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            display.classList.add('has-file');

            // Validate file
            this.validateFile(file, fileType);
        } else {
            // Clear file reference
            delete this.selectedFiles[fileType];

            // Reset display
            placeholder.textContent = `Choose ${fileType} file...`;
            display.classList.remove('has-file');
        }

        this.updateUploadButton();
    }

    validateFile(file, fileType) {
        const maxSize = 100 * 1024 * 1024; // 100MB
        const allowedTypes = [
            'application/json',
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'text/plain'
        ];

        const allowedExtensions = ['.json', '.csv', '.xlsx', '.xls', '.txt'];
        const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));

        if (file.size > maxSize) {
            this.showStatus(`File ${file.name} is too large. Maximum size is 100MB.`, 'error');
            return false;
        }

        if (!allowedExtensions.includes(fileExtension) && !allowedTypes.includes(file.type)) {
            this.showStatus(`File ${file.name} has unsupported format. Please use JSON, CSV, XLSX, or TXT files.`, 'error');
            return false;
        }

        this.showStatus(`File ${file.name} validated successfully`, 'success');
        return true;
    }

    updateUploadButton() {
        const hasFiles = Object.keys(this.selectedFiles).length > 0;
        this.uploadBtn.disabled = !hasFiles;

        if (hasFiles) {
            const fileCount = Object.keys(this.selectedFiles).length;
            this.uploadBtn.textContent = `🚀 Upload ${fileCount} File${fileCount > 1 ? 's' : ''}`;
        } else {
            this.uploadBtn.textContent = '🚀 Upload Files';
        }
    }

    async handleFormSubmit(event) {
        event.preventDefault();

        if (Object.keys(this.selectedFiles).length === 0) {
            this.showStatus('Please select at least one file to upload', 'warning');
            return;
        }

        this.setLoading(true);
        this.showProgress(0);

        try {
            const formData = new FormData();

            // Add files to form data
            Object.entries(this.selectedFiles).forEach(([type, file]) => {
                formData.append(`${type}_file`, file);
            });

            // Simulate progress
            this.simulateProgress();

            const response = await fetch('/api/bulk-upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const result = await response.json();
            this.showProgress(100);
            this.displayUploadResults(result);
            this.showStatus('Bulk upload completed successfully!', 'success');

        } catch (error) {
            console.error('Upload error:', error);
            this.showStatus(`Upload failed: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    simulateProgress() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 20;
            if (progress >= 90) {
                clearInterval(interval);
                this.showProgress(90);
                return;
            }
            this.showProgress(Math.min(progress, 90));
        }, 200);
    }

    showProgress(percentage) {
        this.progressSection.classList.remove('hidden');
        this.progressBarFill.style.width = `${percentage}%`;
        this.progressText.textContent = `${Math.round(percentage)}% Complete`;

        if (percentage >= 100) {
            setTimeout(() => {
                this.progressSection.classList.add('hidden');
            }, 2000);
        }
    }

    displayUploadResults(result) {
        this.resultsSection.classList.remove('hidden');

        // Update summary stats
        this.filesUploadedCount.textContent = result.uploaded_files.length;
        this.recordsProcessedCount.textContent = result.total_processed;
        this.uploadStatus.textContent = result.status;

        // Display uploaded files list
        this.uploadedFilesList.innerHTML = '';

        if (result.uploaded_files.length > 0) {
            result.uploaded_files.forEach(fileInfo => {
                const fileElement = document.createElement('div');
                fileElement.className = 'uploaded-file-item';
                
                fileElement.innerHTML = `
                    <div class="file-info">
                        <span class="file-name">${fileInfo.filename}</span>
                        <span class="file-details">Type: ${fileInfo.type} | Size: ${this.formatFileSize(fileInfo.size)}</span>
                    </div>
                    <span class="text-success">✓ Uploaded</span>
                `;
                
                this.uploadedFilesList.appendChild(fileElement);
            });
        } else {
            this.uploadedFilesList.innerHTML = '<p>No files were uploaded.</p>';
        }

        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    async loadDatabaseStats() {
        this.setLoading(true);

        try {
            // Since we don't have a direct stats endpoint, we'll create one or simulate it
            const response = await fetch('/api/health'); // We'll need to add a stats endpoint
            
            if (response.ok) {
                // For now, display mock stats - in real implementation, add /api/stats endpoint
                this.displayDatabaseStats({
                    observability_logs: { document_count: 'Loading...' },
                    observability_metrics: { document_count: 'Loading...' },
                    observability_traces: { document_count: 'Loading...' },
                    rca_results: { document_count: 'Loading...' },
                    historical_cases: { document_count: 'Loading...' }
                });
                
                this.showStatus('Database statistics loaded', 'success');
            } else {
                throw new Error('Failed to load database statistics');
            }

        } catch (error) {
            console.error('Stats error:', error);
            this.showStatus(`Failed to load stats: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    displayDatabaseStats(stats) {
        this.databaseStatsSection.classList.remove('hidden');

        const statsHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>📝 Logs Collection</h4>
                    <div class="stat-item">
                        <span>Documents:</span>
                        <span>${stats.observability_logs?.document_count || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h4>📊 Metrics Collection</h4>
                    <div class="stat-item">
                        <span>Documents:</span>
                        <span>${stats.observability_metrics?.document_count || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h4>🔗 Traces Collection</h4>
                    <div class="stat-item">
                        <span>Documents:</span>
                        <span>${stats.observability_traces?.document_count || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h4>📋 RCA Results</h4>
                    <div class="stat-item">
                        <span>Documents:</span>
                        <span>${stats.rca_results?.document_count || 0}</span>
                    </div>
                </div>
                
                <div class="stat-card">
                    <h4>🗂️ Historical Cases</h4>
                    <div class="stat-item">
                        <span>Documents:</span>
                        <span>${stats.historical_cases?.document_count || 0}</span>
                    </div>
                </div>
            </div>
        `;

        this.databaseStatsContent.innerHTML = statsHTML;
        this.databaseStatsSection.scrollIntoView({ behavior: 'smooth' });
    }

    clearAllFiles() {
        // Clear file inputs
        Object.values(this.fileInputs).forEach(input => {
            input.value = '';
        });

        // Clear file references
        this.selectedFiles = {};

        // Reset displays
        document.querySelectorAll('.file-input-display').forEach(display => {
            display.classList.remove('has-file');
        });

        document.querySelectorAll('.file-placeholder').forEach(placeholder => {
            const type = placeholder.closest('.upload-group').querySelector('input').name.replace('_file', '');
            placeholder.textContent = `Choose ${type} file...`;
        });

        // Hide sections
        this.resultsSection.classList.add('hidden');
        this.progressSection.classList.add('hidden');
        this.databaseStatsSection.classList.add('hidden');

        this.updateUploadButton();
        this.showStatus('All files cleared', 'success');
    }

    resetForNewUpload() {
        this.clearAllFiles();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    setLoading(loading) {
        if (loading) {
            this.uploadBtn.disabled = true;
            this.loadingSpinner.classList.remove('hidden');
        } else {
            this.updateUploadButton();
            this.loadingSpinner.classList.add('hidden');
        }
    }

    showStatus(message, type = 'info') {
        this.statusBar.className = `status-bar ${type}`;
        this.statusText.textContent = message;
        this.statusBar.classList.remove('hidden');

        // Auto-hide after 5 seconds for success messages
        if (type === 'success') {
            setTimeout(() => {
                this.statusBar.classList.add('hidden');
            }, 5000);
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// File validation utilities
class FileValidator {
    static validateJSON(content) {
        try {
            JSON.parse(content);
            return { valid: true };
        } catch (error) {
            return { valid: false, error: 'Invalid JSON format' };
        }
    }

    static validateCSV(content) {
        const lines = content.split('\n');
        if (lines.length < 2) {
            return { valid: false, error: 'CSV must have at least header and one data row' };
        }
        
        const headers = lines[0].split(',');
        if (headers.length < 1) {
            return { valid: false, error: 'CSV must have at least one column' };
        }
        
        return { valid: true };
    }

    static getFilePreview(file, type) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (e) => {
                const content = e.target.result;
                let preview = '';
                
                if (type === 'json') {
                    try {
                        const data = JSON.parse(content);
                        preview = JSON.stringify(data, null, 2).substring(0, 500);
                    } catch (error) {
                        preview = content.substring(0, 500);
                    }
                } else {
                    preview = content.substring(0, 500);
                }
                
                resolve(preview);
            };
            
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }
}

// Sample data generator for testing
class SampleDataGenerator {
    static generateSampleLogs() {
        const logs = [
            '2025-06-19 10:30:15 ERROR [ApplicationService] Database connection failed: timeout after 30s',
            '2025-06-19 10:30:16 WARN [ConnectionPool] Retrying connection attempt 1/3',
            '2025-06-19 10:30:18 ERROR [ConnectionPool] Connection attempt failed: Connection refused',
            '2025-06-19 10:30:20 WARN [ConnectionPool] Retrying connection attempt 2/3',
            '2025-06-19 10:30:22 ERROR [ConnectionPool] Connection attempt failed: Connection refused',
            '2025-06-19 10:30:24 FATAL [ApplicationService] Max retries exceeded, service unavailable'
        ];
        return logs.join('\n');
    }

    static generateSampleMetrics() {
        return `timestamp,cpu_usage,memory_usage,disk_io,network_io
2025-06-19T10:30:00Z,85.2,78.5,120.3,45.7
2025-06-19T10:30:30Z,92.1,82.1,134.7,52.3
2025-06-19T10:31:00Z,88.9,79.8,98.2,38.9
2025-06-19T10:31:30Z,95.3,85.2,156.4,61.2`;
    }

    static generateSampleTraces() {
        return JSON.stringify({
            "trace_id": "abc123def456",
            "spans": [
                {
                    "span_id": "span001",
                    "operation": "http_request",
                    "duration_ms": 1250,
                    "status": "error",
                    "tags": {
                        "http.method": "GET",
                        "http.url": "/api/users",
                        "error": true
                    }
                },
                {
                    "span_id": "span002", 
                    "parent_id": "span001",
                    "operation": "database_query",
                    "duration_ms": 1100,
                    "status": "timeout",
                    "tags": {
                        "db.statement": "SELECT * FROM users WHERE active = 1",
                        "db.type": "postgresql"
                    }
                }
            ]
        }, null, 2);
    }
}

// Initialize the bulk uploader when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BulkUploader();
    console.log('Bulk Upload System initialized');
});
