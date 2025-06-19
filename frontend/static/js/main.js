// Main JavaScript for RCA Analysis Page
class RCAAnalyzer {
    constructor() {
        this.initializeElements();
        this.attachEventListeners();
        this.checkAPIHealth();
    }

    initializeElements() {
        // Form elements
        this.form = document.getElementById('rca-form');
        this.logsInput = document.getElementById('logs');
        this.metricsInput = document.getElementById('metrics');
        this.tracesInput = document.getElementById('traces');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.clearBtn = document.getElementById('clear-btn');

        // Status elements
        this.statusBar = document.getElementById('status-bar');
        this.statusText = document.getElementById('status-text');
        this.loadingSpinner = document.getElementById('loading-spinner');

        // Results elements
        this.resultsSection = document.getElementById('results-section');
        this.analysisId = document.getElementById('analysis-id');
        this.analysisTimestamp = document.getElementById('analysis-timestamp');
        this.rcaResult = document.getElementById('rca-result');
        this.copyResultBtn = document.getElementById('copy-result-btn');
        this.downloadResultBtn = document.getElementById('download-result-btn');

        // Similar cases elements
        this.similarCasesSection = document.getElementById('similar-cases-section');
        this.similarCasesList = document.getElementById('similar-cases-list');

        // Search elements
        this.searchInput = document.getElementById('search-input');
        this.searchBtn = document.getElementById('search-btn');
        this.searchResults = document.getElementById('search-results');
    }

    attachEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        
        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearForm());
        
        // Result actions
        this.copyResultBtn.addEventListener('click', () => this.copyResults());
        this.downloadResultBtn.addEventListener('click', () => this.downloadResults());
        
        // Search functionality
        this.searchBtn.addEventListener('click', () => this.performSearch());
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Auto-resize textareas
        [this.logsInput, this.metricsInput, this.tracesInput].forEach(textarea => {
            textarea.addEventListener('input', () => this.autoResizeTextarea(textarea));
        });
    }

    async checkAPIHealth() {
        try {
            const response = await fetch('/api/health');
            if (response.ok) {
                this.showStatus('API is healthy and ready', 'success');
            } else {
                this.showStatus('API health check failed', 'error');
            }
        } catch (error) {
            this.showStatus('Unable to connect to API', 'error');
        }
    }

    async handleFormSubmit(event) {
        event.preventDefault();

        const logs = this.logsInput.value.trim();
        const metrics = this.metricsInput.value.trim();
        const traces = this.tracesInput.value.trim();

        if (!logs || !metrics || !traces) {
            this.showStatus('Please fill in all three fields', 'error');
            return;
        }

        this.setLoading(true);
        this.hideResults();

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    logs: logs,
                    metrics: metrics,
                    traces: traces,
                    timestamp: new Date().toISOString(),
                    environment: 'production'
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const result = await response.json();
            this.displayResults(result);
            this.showStatus('Analysis completed successfully!', 'success');

        } catch (error) {
            console.error('Analysis error:', error);
            this.showStatus(`Analysis failed: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    displayResults(result) {
        // Show results section
        this.resultsSection.classList.remove('hidden');

        // Set analysis info
        this.analysisId.textContent = `Analysis ID: ${result.analysis_id}`;
        this.analysisTimestamp.textContent = `Generated: ${new Date().toLocaleString()}`;

        // Display RCA result with markdown-like formatting
        this.rcaResult.innerHTML = this.formatRCAResult(result.rca_result);

        // Display similar cases if available
        if (result.similar_cases && result.similar_cases.length > 0) {
            this.displaySimilarCases(result.similar_cases);
        }

        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });

        // Store current result for copy/download
        this.currentResult = result;
    }

    formatRCAResult(text) {
        // Convert markdown-like text to HTML
        let formatted = text
            // Headers
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            
            // Bold text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            
            // Lists
            .replace(/^\d+\.\s+(.*$)/gm, '<li>$1</li>')
            .replace(/^-\s+(.*$)/gm, '<li>$1</li>')
            
            // Line breaks
            .replace(/\n/g, '<br>');

        // Wrap consecutive <li> elements in <ol> or <ul>
        formatted = formatted.replace(/(<li>.*?<\/li>)(?:\s*<br>\s*<li>.*?<\/li>)*/g, (match) => {
            if (match.includes('<li>')) {
                return '<ul>' + match.replace(/<br>/g, '') + '</ul>';
            }
            return match;
        });

        return formatted;
    }

    displaySimilarCases(cases) {
        this.similarCasesSection.classList.remove('hidden');
        this.similarCasesList.innerHTML = '';

        cases.forEach((caseData, index) => {
            const caseElement = document.createElement('div');
            caseElement.className = 'similar-case-item';
            
            const similarity = caseData.similarity_score || 0;
            const document = caseData.document || 'No details available';
            
            caseElement.innerHTML = `
                <div class="similar-case-header">
                    <h4>Similar Case ${index + 1}</h4>
                    <span class="similarity-score">Similarity: ${(similarity * 100).toFixed(1)}%</span>
                </div>
                <p>${document.substring(0, 300)}${document.length > 300 ? '...' : ''}</p>
            `;
            
            this.similarCasesList.appendChild(caseElement);
        });
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        if (!query) {
            this.showStatus('Please enter a search query', 'warning');
            return;
        }

        this.setLoading(true);

        try {
            const response = await fetch(`/api/search-similar?query=${encodeURIComponent(query)}&limit=5`);
            
            if (!response.ok) {
                throw new Error('Search failed');
            }

            const result = await response.json();
            this.displaySearchResults(result.similar_cases);

        } catch (error) {
            console.error('Search error:', error);
            this.showStatus(`Search failed: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    displaySearchResults(cases) {
        this.searchResults.classList.remove('hidden');
        this.searchResults.innerHTML = '';

        if (!cases || cases.length === 0) {
            this.searchResults.innerHTML = '<p>No similar cases found.</p>';
            return;
        }

        cases.forEach((caseData, index) => {
            const resultElement = document.createElement('div');
            resultElement.className = 'search-result-item';
            
            const similarity = caseData.similarity_score || 0;
            const document = caseData.document || 'No details available';
            const metadata = caseData.metadata || {};
            
            resultElement.innerHTML = `
                <div class="search-result-header">
                    <h4>Result ${index + 1}</h4>
                    <span class="similarity-score">Similarity: ${(similarity * 100).toFixed(1)}%</span>
                </div>
                <p>${document.substring(0, 250)}${document.length > 250 ? '...' : ''}</p>
                <small>Timestamp: ${metadata.timestamp || 'Unknown'}</small>
            `;
            
            this.searchResults.appendChild(resultElement);
        });
    }

    clearForm() {
        this.logsInput.value = '';
        this.metricsInput.value = '';
        this.tracesInput.value = '';
        this.hideResults();
        this.hideSearchResults();
        this.showStatus('Form cleared', 'success');
    }

    hideResults() {
        this.resultsSection.classList.add('hidden');
        this.similarCasesSection.classList.add('hidden');
    }

    hideSearchResults() {
        this.searchResults.classList.add('hidden');
        this.searchInput.value = '';
    }

    async copyResults() {
        if (!this.currentResult) {
            this.showStatus('No results to copy', 'warning');
            return;
        }

        try {
            const textToCopy = `Analysis ID: ${this.currentResult.analysis_id}\n\n${this.currentResult.rca_result}`;
            await navigator.clipboard.writeText(textToCopy);
            this.showStatus('Results copied to clipboard!', 'success');
        } catch (error) {
            console.error('Copy error:', error);
            this.showStatus('Failed to copy results', 'error');
        }
    }

    downloadResults() {
        if (!this.currentResult) {
            this.showStatus('No results to download', 'warning');
            return;
        }

        const content = `RCA Analysis Report
Generated: ${new Date().toISOString()}
Analysis ID: ${this.currentResult.analysis_id}

${this.currentResult.rca_result}`;

        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `RCA_Analysis_${this.currentResult.analysis_id}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showStatus('Results downloaded!', 'success');
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.max(150, textarea.scrollHeight) + 'px';
    }

    setLoading(loading) {
        if (loading) {
            this.analyzeBtn.disabled = true;
            this.analyzeBtn.textContent = '🔄 Analyzing...';
            this.loadingSpinner.classList.remove('hidden');
        } else {
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.textContent = '🚀 Generate RCA Analysis';
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
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatTimestamp(timestamp) {
    try {
        return new Date(timestamp).toLocaleString();
    } catch (error) {
        return timestamp || 'Unknown';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RCAAnalyzer();
    console.log('AI Observability RCA System initialized');
});
