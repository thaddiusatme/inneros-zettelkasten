/**
 * Simple YouTube Processing Trigger
 * 
 * Just copy/paste this line into your YouTube note after creation:
 * <% await tp.user.simple_youtube_trigger(tp) %>
 */

module.exports = async (tp) => {
    const API_BASE_URL = 'http://localhost:8080';
    const API_ENDPOINT = '/api/youtube/process';
    
    try {
        // Get current note path
        const notePath = "knowledge/" + tp.file.path(true);
        
        console.log('[Simple Trigger] Processing YouTube note:', notePath);
        
        // Make POST request
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINT}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ note_path: notePath })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            new Notice(`✅ Processing started! Job ID: ${data.job_id}`);
            console.log('[Simple Trigger] Success:', data);
            return `<!-- Processing started: ${data.job_id} -->`;
        } else {
            new Notice(`❌ Error: ${data.message}`);
            console.error('[Simple Trigger] Error:', data);
            return `<!-- Error: ${data.message} -->`;
        }
        
    } catch (error) {
        const message = error.message.includes('Failed to fetch') 
            ? '⚠️ Server offline - start: python3 development/run_youtube_api_server.py'
            : `❌ Error: ${error.message}`;
        
        new Notice(message);
        console.error('[Simple Trigger] Failed:', error);
        return `<!-- ${message} -->`;
    }
};
