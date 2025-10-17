/**
 * Dashboard Metrics Updater
 * Phase 3.2 P1 - Dashboard Metrics Cards Integration
 * 
 * Fetches metrics from /api/metrics and updates dashboard cards
 */

/**
 * DOM Helper Utilities
 */
class DOMHelpers {
    /**
     * Query all elements matching selector
     */
    static queryAll(selector) {
        return document.querySelectorAll(selector);
    }
    
    /**
     * Query single element matching selector
     */
    static query(selector) {
        return document.querySelector(selector);
    }
    
    /**
     * Hide element
     */
    static hide(element) {
        if (element) {
            element.style.display = 'none';
        }
    }
    
    /**
     * Show element
     */
    static show(element) {
        if (element) {
            element.style.display = '';
        }
    }
    
    /**
     * Add CSS class
     */
    static addClass(element, className) {
        if (element) {
            element.classList.add(className);
        }
    }
    
    /**
     * Remove CSS class
     */
    static removeClass(element, className) {
        if (element) {
            element.classList.remove(className);
        }
    }
}

/**
 * Metric Formatters
 */
class MetricFormatters {
    /**
     * Format number with locale-specific thousands separators
     */
    static formatNumber(value) {
        return Number(value).toLocaleString();
    }
    
    /**
     * Format decimal with fixed precision
     */
    static formatDecimal(value, precision = 1) {
        return Number(value).toFixed(precision);
    }
    
    /**
     * Format timestamp as locale time string
     */
    static formatTime(timestamp) {
        return timestamp ? new Date(timestamp).toLocaleTimeString() : '--';
    }
    
    /**
     * Format health status as emoji + text
     */
    static formatHealth(value) {
        if (value >= 0.9) return '✅ Healthy';
        if (value >= 0.7) return '⚠️ Warning';
        return '❌ Critical';
    }
    
    /**
     * Format percentage
     */
    static formatPercent(value, precision = 0) {
        return `${(value * 100).toFixed(precision)}%`;
    }
}

class MetricsUpdater {
    constructor(endpoint = '/api/metrics', interval = 2000) {
        this.endpoint = endpoint;
        this.interval = interval;
        this.intervalId = null;
        this.lastUpdate = null;
    }
    
    /**
     * Start auto-refresh of metrics
     */
    start() {
        // Initial fetch
        this.fetchMetrics();
        
        // Set up interval for auto-refresh
        this.intervalId = setInterval(() => {
            this.fetchMetrics();
        }, this.interval);
    }
    
    /**
     * Stop auto-refresh
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    /**
     * Fetch metrics from API and update DOM
     */
    async fetchMetrics() {
        try {
            const response = await fetch(this.endpoint);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.updateCards(data);
            this.lastUpdate = new Date();
            
        } catch (error) {
            console.error('Failed to fetch metrics:', error);
            this.showError(error.message);
        }
    }
    
    /**
     * Update metric cards with fetched data
     */
    updateCards(data) {
        const current = data.current || {};
        const counters = current.counters || {};
        const gauges = current.gauges || {};
        const histograms = current.histograms || {};
        
        // Hide loading spinners
        DOMHelpers.queryAll('[data-loading]').forEach(el => {
            DOMHelpers.hide(el);
        });
        
        // Update counter cards
        this.updateCounter('notes_processed', counters.notes_processed || 0);
        this.updateCounter('workflow_runs', counters.workflow_runs || 0);
        
        // Update gauge cards
        this.updateGauge('success_rate', gauges.success_rate || 0);
        this.updateGauge('system_health', this.formatHealthStatus(gauges.system_health || 0));
        
        // Update histogram cards
        this.updateHistogram('processing_time', histograms.processing_time || {});
        this.updateHistogram('quality_scores', histograms.quality_scores || {});
        
        // Update timestamps
        this.updateTimestamps(data.timestamp);
        
        // Hide any error messages
        DOMHelpers.queryAll('[data-error-message]').forEach(el => {
            DOMHelpers.addClass(el, 'd-none');
        });
    }
    
    /**
     * Update counter metric value
     */
    updateCounter(metricName, value) {
        const element = DOMHelpers.query(`[data-metric-value="${metricName}"] .value-display`);
        if (element) {
            element.textContent = MetricFormatters.formatNumber(value);
        }
    }
    
    /**
     * Update gauge metric value
     */
    updateGauge(metricName, value) {
        const element = DOMHelpers.query(`[data-metric-value="${metricName}"] .value-display`);
        if (element) {
            element.textContent = typeof value === 'number' ? 
                MetricFormatters.formatDecimal(value) : value;
        }
    }
    
    /**
     * Update histogram summary
     */
    updateHistogram(metricName, data) {
        const container = DOMHelpers.query(`[data-metric-value="${metricName}"] .value-display`);
        if (!container) return;
        
        if (metricName === 'processing_time') {
            const avg = data.mean || 0;
            const p95 = data.p95 || 0;
            container.innerHTML = `
                <p class="mb-1">Average: <strong>${MetricFormatters.formatDecimal(avg, 2)}</strong>s</p>
                <p class="mb-1">P95: <strong>${MetricFormatters.formatDecimal(p95, 2)}</strong>s</p>
            `;
        } else if (metricName === 'quality_scores') {
            const avg = data.mean || 0;
            const highPct = data.high_quality || 0;
            container.innerHTML = `
                <p class="mb-1">Average: <strong>${MetricFormatters.formatDecimal(avg, 2)}</strong></p>
                <p class="mb-1">High Quality: <strong>${MetricFormatters.formatPercent(highPct, 0)}</strong></p>
            `;
        }
    }
    
    /**
     * Update all timestamp elements
     */
    updateTimestamps(timestamp) {
        const timeStr = MetricFormatters.formatTime(timestamp);
        DOMHelpers.queryAll('[data-timestamp]').forEach(el => {
            el.textContent = `Last updated: ${timeStr}`;
        });
    }
    
    /**
     * Format health status as text
     */
    formatHealthStatus(value) {
        return MetricFormatters.formatHealth(value);
    }
    
    /**
     * Show error message on all cards
     */
    showError(message) {
        // Hide loading spinners
        DOMHelpers.queryAll('[data-loading]').forEach(el => {
            DOMHelpers.hide(el);
        });
        
        // Show error messages
        DOMHelpers.queryAll('[data-error-message]').forEach(el => {
            el.textContent = `Unavailable: ${message}`;
            DOMHelpers.removeClass(el, 'd-none');
        });
        
        // Set all values to "--"
        DOMHelpers.queryAll('.value-display').forEach(el => {
            if (!el.innerHTML.includes('<p')) {
                el.textContent = '--';
            }
        });
    }
}
