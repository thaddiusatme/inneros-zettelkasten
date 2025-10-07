# YouTube CLI - Dedicated YouTube Note Processing

**Clean Architecture**: Focused CLI for YouTube workflows without bloating workflow_demo.py

## 🎯 Purpose

Process YouTube video notes with AI-extracted quotes while maintaining clean separation of concerns. Built on top of production-ready utilities from TDD Iteration 3.

## 🚀 Quick Start

```bash
# Navigate to development directory
cd development

# Process a single note
python3 src/cli/youtube_cli.py process-note ../knowledge/Inbox/youtube-note.md

# Batch process all YouTube notes
python3 src/cli/youtube_cli.py batch-process

# Preview what would be processed
python3 src/cli/youtube_cli.py batch-process --preview
```

## 📖 Commands

### `process-note` - Process Single Note

Process a single YouTube note with transcript and quotes.

```bash
python3 src/cli/youtube_cli.py process-note <note-path> [options]

Options:
  --preview              Show quotes without modifying note
  --min-quality FLOAT    Minimum relevance score (0.0-1.0)
  --categories LIST      Comma-separated categories
  --format {normal|json} Output format
```

**Examples:**
```bash
# Basic processing
python3 src/cli/youtube_cli.py process-note note.md

# Preview mode (no modifications)
python3 src/cli/youtube_cli.py process-note note.md --preview

# Quality filtering
python3 src/cli/youtube_cli.py process-note note.md --min-quality 0.7

# Specific categories
python3 src/cli/youtube_cli.py process-note note.md --categories "key_insights,actionable"

# JSON output
python3 src/cli/youtube_cli.py process-note note.md --format json
```

### `batch-process` - Process All YouTube Notes

Process all unprocessed YouTube notes in Inbox directory.

```bash
python3 src/cli/youtube_cli.py batch-process [options]

Options:
  --preview              Show what would be processed
  --min-quality FLOAT    Minimum relevance score
  --categories LIST      Comma-separated categories
  --format {normal|json} Output format
  --export PATH          Export report to markdown file
```

**Examples:**
```bash
# Process all notes
python3 src/cli/youtube_cli.py batch-process

# Preview mode
python3 src/cli/youtube_cli.py batch-process --preview

# Quality filtering
python3 src/cli/youtube_cli.py batch-process --min-quality 0.7

# JSON output for automation
python3 src/cli/youtube_cli.py batch-process --format json

# Export report
python3 src/cli/youtube_cli.py batch-process --export report.md

# Combined options
python3 src/cli/youtube_cli.py batch-process --preview --min-quality 0.7 --export preview-report.md
```

## 🌍 Global Options

```bash
--vault PATH    Path to vault root (default: current directory)
--verbose       Enable verbose logging
--help          Show help message
```

**Examples:**
```bash
# Process with different vault
python3 src/cli/youtube_cli.py --vault /path/to/vault batch-process

# Verbose logging for debugging
python3 src/cli/youtube_cli.py --verbose batch-process
```

## 🏗️ Architecture

```
youtube_cli.py (thin CLI layer)
    ↓
YouTubeCLIProcessor (orchestration)
    ↓
├── YouTubeProcessor (transcript/quotes)
├── YouTubeNoteEnhancer (note modification)
└── Utilities (validation, formatting, export)
```

**Design Principles:**
- **Thin CLI Layer**: Just argument parsing and output
- **Business Logic in Utilities**: All processing in testable utilities
- **Single Responsibility**: Each class does one thing well
- **Zero God Classes**: No bloated monolithic components

## 📊 Output Formats

### Normal (Human-Readable)

```
🎬 YouTube Batch Processing
   📁 Vault: /path/to/vault
   📥 Inbox: /path/to/vault/Inbox

🔄 Processing 1/3: youtube-note-1.md
✅ Enhanced youtube-note-1.md with 5 quotes

🔄 Processing 2/3: youtube-note-2.md
✅ Enhanced youtube-note-2.md with 3 quotes

📊 Batch Processing Summary:
   ✅ Successful: 2
   ❌ Failed: 0
   ⚠️ Skipped: 0
   📝 Total Quotes: 8
   📈 Total Notes: 2
```

### JSON (Automation-Friendly)

```json
{
  "successful": 2,
  "failed": 0,
  "skipped": 0,
  "total": 2,
  "total_quotes": 8
}
```

## 🔍 Exit Codes

- **0**: Success (all notes processed successfully)
- **1**: Failure (one or more notes failed to process)
- **130**: Cancelled by user (Ctrl+C)

Use exit codes for automation:
```bash
if python3 src/cli/youtube_cli.py batch-process; then
    echo "All notes processed successfully"
else
    echo "Some notes failed"
fi
```

## 🧪 Testing

The CLI is built on top of fully tested utilities (16/16 tests passing):

```bash
# Test utilities
cd development
python3 -m pytest tests/unit/test_youtube_cli_utils.py -v

# Test integration
python3 -m pytest tests/unit/test_youtube_cli_integration.py -v
```

## 📝 Note Requirements

For a note to be processed, it must:

1. **Exist** in the Inbox directory
2. **Have valid YAML frontmatter** with:
   - `source: youtube`
   - `url: <youtube-url>`
   - `ai_processed: false` (or missing)

**Example Valid Note:**
```markdown
---
type: literature
source: youtube
url: https://www.youtube.com/watch?v=VIDEO_ID
created: 2025-10-06 19:00
ai_processed: false
---

# Video Title

## Why I'm Saving This
Interesting content about AI...
```

## 🐛 Troubleshooting

### "Note not found"
- Check the file path is correct
- Use absolute paths or paths relative to current directory

### "Note is missing 'source' field"
- Add `source: youtube` to YAML frontmatter

### "Note source is 'article', expected 'youtube'"
- This CLI only processes YouTube notes
- Change `source: youtube` or use different processor

### "Transcript unavailable"
- Video may have no captions
- Video may be private/deleted
- API rate limiting (wait and retry)

### JSON output shows progress messages
- Bug: Use `--format json` flag
- This enables quiet mode internally

## 🔗 Related Files

- **`youtube_cli_utils.py`** - Utility classes (TDD Iteration 3)
- **`youtube_processor.py`** - Core YouTube processing
- **`youtube_note_enhancer.py`** - Note enhancement logic
- **Test files** - `test_youtube_cli_utils.py`, `test_youtube_cli_integration.py`

## 📚 Documentation

- **Lessons Learned**: `Projects/COMPLETED-2025-10/youtube-cli-integration-tdd-iteration-3-lessons-learned.md`
- **Integration Tests**: `development/tests/unit/test_youtube_cli_integration.py`
- **Utility Tests**: `development/tests/unit/test_youtube_cli_utils.py`

## 🎯 Future Enhancements

Potential additions (not yet implemented):
- Progress bar for batch processing
- Retry failed notes automatically
- Resume from last processed note
- Parallel processing for multiple notes
- Custom template selection
- Video metadata extraction (duration, views, etc.)

## 💡 Tips

1. **Always preview first**: Use `--preview` to see what will happen
2. **Start with quality filtering**: Use `--min-quality 0.7` for better quotes
3. **Export reports**: Use `--export` to track processing over time
4. **Use JSON for automation**: `--format json` for scripts
5. **Check exit codes**: Important for automation pipelines

---

**Built with TDD**: All utilities tested with 16/16 passing tests  
**Clean Architecture**: Follows Single Responsibility Principle  
**Zero God Classes**: Each component has a focused purpose
