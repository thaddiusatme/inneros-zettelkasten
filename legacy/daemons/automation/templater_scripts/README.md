# Templater Scripts for InnerOS

This directory contains Templater user scripts that integrate with the InnerOS background daemon for automated knowledge processing.

## Overview

Templater scripts enable automatic processing of notes created from templates. Instead of manually triggering API endpoints, these scripts execute automatically when templates are instantiated in Obsidian.

## Available Scripts

### `trigger_youtube_processing.js`
**Phase**: 2.1 (GREEN)  
**Status**: ✅ Production Ready

Automatically triggers YouTube note processing via the background daemon API when a YouTube template is used.

**Features**:
- Automatic API call to `/api/youtube/process`
- 5-second timeout with graceful fallback
- Offline daemon detection with helpful error messages
- Console logging for debugging
- Returns `job_id` or error object

**Usage**:
```javascript
// In your Templater template:
<%* const result = await tp.user.trigger_youtube_processing(tp); %>
```

See [INSTALLATION.md](./INSTALLATION.md) for setup instructions.

## Directory Structure

```
templater_scripts/
├── README.md                          # This file
├── INSTALLATION.md                    # Setup guide
├── trigger_youtube_processing.js      # YouTube processing hook
└── (future scripts...)
```

## Installation

1. **Copy to Obsidian**:
   ```bash
   cp *.js ~/.obsidian/scripts/
   # Or your configured Templater scripts folder
   ```

2. **Configure Templater**:
   - Open Obsidian Settings → Templater
   - Enable "User Scripts"
   - Set script folder to `.obsidian/scripts`

3. **Update Templates**:
   - Add script calls to your templates
   - See INSTALLATION.md for examples

## Development

### TDD Approach

All scripts follow strict TDD methodology:

1. **RED Phase**: Define tests in `development/tests/manual/`
2. **GREEN Phase**: Minimal implementation to pass tests
3. **REFACTOR Phase**: Extract helpers, improve error handling
4. **COMMIT**: Document lessons learned

### Testing

Scripts are tested manually in Obsidian due to environment constraints:

- Test specifications: `development/tests/manual/test_templater_*.md`
- Follow test checklists for each script
- Document results in lessons learned docs

### Adding New Scripts

1. Create script in this directory
2. Write test specification in `development/tests/manual/`
3. Create INSTALLATION documentation section
4. Copy to `.obsidian/scripts/` for local testing
5. Follow TDD cycle (RED → GREEN → REFACTOR → COMMIT)

## Integration with Daemon

These scripts communicate with the background daemon at `http://localhost:8080`:

- **Health check**: `GET /health`
- **YouTube processing**: `POST /api/youtube/process`
- **Queue status**: `GET /api/youtube/queue`

Ensure daemon is running before using scripts:
```bash
python3 development/src/automation/daemon.py
```

## Error Handling

All scripts implement comprehensive error handling:

- **Network errors**: Graceful degradation with user feedback
- **Timeouts**: 5-second max with clear messaging
- **Daemon offline**: Helpful restart instructions
- **API errors**: Logged but don't block template completion

## Future Scripts (Planned)

- `trigger_reading_intake.js` - Reading list processing
- `trigger_daily_review.js` - Daily note enhancement
- `trigger_literature_processing.js` - Literature note enrichment

## References

- [Templater Plugin Documentation](https://silentvoid13.github.io/Templater/)
- [InnerOS Automation Guide](../../README.md)
- [YouTube API Trigger System](../../../../Projects/ACTIVE/youtube-api-requirements-review.md)
