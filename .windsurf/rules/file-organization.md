# File Organization & Structure Rules

> **Purpose**: File patterns, metadata schemas, directory structure  
> **Updated**: 2025-09-18  

## 📁 File Organization Rules

### Markdown Files
Requirements:
- All new notes must start in `Inbox/` with `status: inbox`
- YAML frontmatter is required for all notes
- Use kebab-case for filenames (e.g., `my-note-title.md`)
- Include created timestamp in ISO format (YYYY-MM-DD HH:mm)

### Metadata Schema (Extended for Reading Intake Pipeline)
```yaml
# Required Fields
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published | archived
visibility: private | shared | team | public

# Optional Fields  
tags: [kebab-case, hierarchical]
linked_notes: [[note-name]]
quality_score: 0.0-1.0
ai_tags: [auto-generated, contextual]

# Reading Intake Extensions (new)
source: url | book | article | video | podcast
url: https://example.com (if applicable)
saved_at: YYYY-MM-DD HH:mm
claims: [key-assertions]
quotes: ["important-quotes"]
```

### Directory Structure
| Stage | Directory | Status Values | AI Features |
|-----------|---------------|-------------------|-----------------|
| Capture | `Inbox/` | `status: inbox` | Auto-tagging, quality assessment, import processing |
| Process | `Fleeting Notes/` | `inbox → promoted` | Semantic analysis, connection discovery |
| Literature | `Literature Notes/` | `promoted → published` | Claims extraction, quote analysis, source linking |
| Permanent | `Permanent Notes/` | `draft → published` | Summarization, link prediction, gap analysis |
| Archive | `Archive/` | `archived` | Compression, backup, historical analysis |
| Templates | `Templates/` | N/A | Dynamic content generation, Templater scripts |

### Templates (Enhanced)
Current Templates:
- `fleeting.md` - Quick capture (WORKING - Updated Templater syntax)
- `permanent.md` - Structured permanent notes
- `literature-note.md` - NEW: For imported articles/books with claims/quotes
- `saved-article.md` - NEW: For Reading Intake Pipeline processing

Requirements:
- Include workflow guidance comments in all templates
- Use Templater syntax for dynamic content generation
- Never modify templates without testing timestamp generation
- All templates must work with AI workflow integration

## 🎯 Naming Conventions

### File & Directory Standards
- Files: kebab-case (e.g., `my-note-title.md`)
- Folders: Title Case (e.g., `Literature Notes`)
- Tags: lowercase, hyphenated (e.g., `note-taking`, `ai-workflow`, `reading-intake`)
- Timestamps: ISO format (YYYY-MM-DD HH:mm)
- Import Files: Include source in filename (e.g., `twitter-thread-20250810.md`)

## 🔄 Workflow State Management

### Note Lifecycle (Enhanced)
```
Saved Article/Import → 
Inbox (status: inbox) → 
Literature Notes (promoted) OR Fleeting Notes (promoted) → 
Permanent Notes (published) → 
Archive (archived)
```

### Reading Intake Integration
- Import Sources: Bookmarks, RSS, Twitter, YouTube, articles
- Processing Pipeline: Import → Triage → Literature/Fleeting → Permanent
- AI Enhancement: Uses existing quality scoring, tagging, weekly review
- Template Integration: Specialized literature note templates
- Performance Target: <30 seconds per item triage

### Inbox Processing Rules
- `Inbox/` is staging area for all imports and quick captures
- Status field drives workflow, not folder location
- Only notes with `status: inbox` require active triage
- AI tagging, quality assessment, connection discovery applied during processing
- Literature notes require claims/quotes extraction for promotion
- Reading intake items get source/url/saved_at metadata
