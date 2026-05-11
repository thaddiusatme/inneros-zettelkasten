/**
 * Fetch YouTube Video Metadata using yt-dlp
 * 
 * Usage in template:
 * const metadata = await tp.user.fetch_youtube_metadata(youtubeUrl);
 * 
 * Returns: { title, channel, thumbnail_url, duration, upload_date } or null on error
 * 
 * Requires: yt-dlp installed (brew install yt-dlp)
 */

module.exports = async (youtubeUrl) => {
    const { exec } = require('child_process');
    const util = require('util');
    const execPromise = util.promisify(exec);
    
    try {
        console.log('[YouTube Metadata] Fetching via yt-dlp:', youtubeUrl);
        
        // Use yt-dlp to get JSON metadata (skip download, just metadata)
        const cmd = `/opt/homebrew/bin/yt-dlp --no-download --print-json "${youtubeUrl}" 2>/dev/null | /usr/bin/jq -r '{title: .title, channel: .channel, thumbnail: .thumbnail, duration: .duration, upload_date: .upload_date}'`;
        
        const { stdout, stderr } = await execPromise(cmd, { timeout: 15000 });
        
        if (!stdout || stdout.trim() === '') {
            console.error('[YouTube Metadata] Empty response from yt-dlp');
            return null;
        }
        
        const data = JSON.parse(stdout.trim());
        
        console.log('[YouTube Metadata] Success:', data.title);
        
        return {
            title: data.title || "Unknown Video",
            author_name: data.channel || "Unknown Channel",
            thumbnail_url: data.thumbnail || "",
            duration: data.duration || 0,
            upload_date: data.upload_date || ""
        };
        
    } catch (error) {
        console.error('[YouTube Metadata] yt-dlp error:', error.message);
        return null;
    }
};
