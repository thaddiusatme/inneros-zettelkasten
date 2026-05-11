/**
 * Manual YouTube Note Processing Trigger
 * 
 * Run this manually AFTER creating a YouTube note to trigger processing.
 * This avoids the timing issues with automatic triggers in templates.
 * 
 * Usage: Use Templater command palette to run this script on current note
 */

module.exports = async (tp) => {
    const API_BASE_URL = 'http://localhost:8080';
    const API_ENDPOINT = '/api/youtube/process';
    
    try {
        // Get current note path
        const notePath = "knowledge/" + tp.file.path(true);
        
        console.log('[Manual Trigger] Processing YouTube note...');
        console.log('[Manual Trigger] Note path:', notePath);
        
        // Make POST request
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINT}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note_path: notePath })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            new Notice(`✅ Processing started! Job ID: ${data.job_id}`);
            console.log('[Manual Trigger] Success:', data);
            return data.job_id;
        } else {
            new Notice(`❌ Error: ${data.message}`);
            console.error('[Manual Trigger] Error:', data);
            return data;
        }
        
    } catch (error) {
        const message = error.message.includes('Failed to fetch') 
            ? '⚠️ Daemon offline - start with: python3 development/run_youtube_api_server.py'
            : `❌ Error: ${error.message}`;
        
        new Notice(message);
        console.error('[Manual Trigger] Failed:', error);
        return { error: error.message };
    }
};
