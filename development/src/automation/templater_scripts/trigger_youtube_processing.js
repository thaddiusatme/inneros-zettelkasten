/**
 * Templater User Script: Trigger YouTube Note Processing
 * 
 * Phase 2.1: GREEN Phase Implementation
 * Minimal working code to pass P0 tests
 * 
 * Usage in template:
 *   <% await tp.user.trigger_youtube_processing(tp) %>
 * 
 * Returns: job_id string or error object
 */

module.exports = async (tp) => {
    // Configuration
    const API_BASE_URL = 'http://localhost:8080';
    const API_ENDPOINT = '/api/youtube/process';
    const TIMEOUT_MS = 5000; // 5 second timeout
    
    try {
        // Get absolute note path (add 'knowledge/' prefix since vault is subdirectory)
        const notePath = "knowledge/" + tp.file.path(true);
        
        console.log('[Templater] Triggering YouTube processing...');
        console.log('[Templater] Note path:', notePath);
        
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);
        
        // Make POST request to daemon API
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                note_path: notePath
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        // Check response status
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[Templater] API error:', response.status, errorText);
            return {
                error: 'api_error',
                status: response.status,
                message: errorText
            };
        }
        
        // Parse JSON response
        const data = await response.json();
        
        if (data.job_id) {
            console.log('[Templater] Job ID:', data.job_id);
            console.log('[Templater] Processing initiated successfully');
            return data.job_id;
        } else {
            console.error('[Templater] Missing job_id in response:', data);
            return {
                error: 'invalid_response',
                message: 'Response missing job_id'
            };
        }
        
    } catch (error) {
        // Handle network errors (daemon offline, timeout, etc.)
        if (error.name === 'AbortError') {
            console.error('[Templater] Request timed out after', TIMEOUT_MS, 'ms');
            console.error('[Templater] Processing may still complete in background');
            return {
                error: 'timeout',
                message: 'Request timed out after 5 seconds'
            };
        }
        
        if (error.code === 'ECONNREFUSED' || error.message.includes('Failed to fetch')) {
            console.error('[Templater] Unable to connect to daemon');
            console.error('[Templater] Daemon may be offline. Start with:');
            console.error('[Templater]   python3 development/src/automation/daemon.py');
            console.error('[Templater] Note created successfully (manual processing required)');
            return {
                error: 'daemon_offline',
                message: 'Unable to connect to daemon'
            };
        }
        
        // Unknown error
        console.error('[Templater] Unexpected error:', error.message);
        console.error('[Templater] Stack:', error.stack);
        return {
            error: 'unknown',
            message: error.message
        };
    }
};
