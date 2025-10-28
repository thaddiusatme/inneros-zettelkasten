# YouTube Transcript Archival System - Project Manifest

**Status**: 🟢 In Progress - Phase 1 Complete  
**Priority**: P1 - Enhances YouTube Processing  
**Created**: 2025-10-17  
**Updated**: 2025-10-17 23:45  
**Epic**: YouTube Processing Automation  
**Parent Project**: `youtube-api-trigger-system-manifest.md`  
**Related**: `youtube-auto-promotion-integration-manifest.md`

---

## 🎯 Vision

Automatically save complete YouTube video transcripts as separate, searchable markdown files with bidirectional links to parent notes. This creates a comprehensive archive of video content while keeping notes focused on curated insights.

**Key Principle**: Separate full transcripts from curated quotes - notes contain AI-extracted insights, transcripts provide complete searchable context.

---

## 📊 Current State

### **What Works**
- ✅ YouTube transcript fetching via `YouTubeTranscriptFetcher`
- ✅ AI quote extraction from transcripts
- ✅ Quotes inserted into notes
- ✅ Transcript caching (prevents re-fetching)
- ✅ LLM-formatted transcripts available during processing

### **Current Workflow**
```
1. User creates YouTube note
2. Processing triggered (file watcher or API)
3. Transcript fetched → Cached → AI extracts quotes
4. Quotes inserted into note
5. Transcript discarded (not saved) ❌
```

### **Limitations**
- ❌ Full transcripts not preserved after processing
- ❌ No way to search across all video transcripts
- ❌ Cannot reference specific timestamps from notes
- ❌ Lose transcript if cache expires
- ❌ No archive of video content if videos deleted

---

## 🎯 Target State

### **Enhanced Architecture**
```
Processing Flow:
  Fetch Transcript
      ↓
  Save to Media/Transcripts/youtube-{id}-{date}.md
      ↓
  Extract AI Quotes
      ↓
  Update Note with:
    - AI-extracted quotes
    - Link to full transcript
    - Frontmatter reference
```

### **File Structure**
```
knowledge/
  Media/
    Transcripts/
      youtube-dQw4w9WgXcQ-2025-10-17.md  ← Full transcript
      youtube-abc123xyz-2025-10-18.md
  Inbox/
    YouTube/
      ai-coding-tutorial.md  ← Note with link to transcript
```

### **Enhanced Note Format**
```markdown
---
type: literature
source: youtube
url: https://youtube.com/watch?v=dQw4w9WgXcQ
video_id: dQw4w9WgXcQ
created: 2025-10-17 22:00
ai_processed: true
transcript_file: [[youtube-dQw4w9WgXcQ-2025-10-17]]  ← NEW
---

# AI Coding Tutorial

**Full Transcript**: [[youtube-dQw4w9WgXcQ-2025-10-17]]  ← NEW

## Why I'm Saving This
Learn cursor AI features

## Quotes
<!-- AI-extracted quotes -->
```

### **Transcript File Format**
```markdown
---
type: media-transcript
source: youtube
video_id: dQw4w9WgXcQ
video_url: https://youtube.com/watch?v=dQw4w9WgXcQ
video_title: "AI Coding Tutorial"
duration: "15:34"
transcript_length: 2543
fetched: 2025-10-17 22:00
parent_note: [[ai-coding-tutorial]]
---

# YouTube Transcript: AI Coding Tutorial

**Video**: [AI Coding Tutorial](https://youtube.com/watch?v=dQw4w9WgXcQ)  
**Duration**: 15:34  
**Parent Note**: [[ai-coding-tutorial]]

---

## Transcript

**[00:00]** Welcome to this tutorial...
**[00:15]** First, let's look at...
**[01:23]** The most important thing...
```

---

## 🏗️ Technical Architecture

### **New Component: YouTubeTranscriptSaver**

**File**: `development/src/ai/youtube_transcript_saver.py`

```python
class YouTubeTranscriptSaver:
    """Saves YouTube transcripts as separate markdown files."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.transcript_dir = vault_path / 'Media' / 'Transcripts'
    
    def save_transcript(
        self,
        video_id: str,
        transcript_data: Dict[str, Any],
        video_title: str,
        video_url: str,
        parent_note_name: str
    ) -> Path:
        """Save transcript and return path."""
    
    def get_transcript_link(self, video_id: str) -> str:
        """Get wikilink to transcript file."""
```

**Key Methods**:
- `save_transcript()` - Creates transcript markdown file
- `get_transcript_link()` - Generates wikilink
- `_build_transcript_content()` - Formats transcript with frontmatter
- `_format_timestamp()` - Converts seconds to MM:SS
- `_format_duration()` - Formats video duration

### **Integration Point: YouTubeFeatureHandler**

**Modify**: `development/src/automation/feature_handlers.py`

```python
class YouTubeFeatureHandler:
    def __init__(self, config):
        # ... existing code ...
        
        # NEW: Initialize transcript saver
        from src.ai.youtube_transcript_saver import YouTubeTranscriptSaver
        self.transcript_saver = YouTubeTranscriptSaver(self.vault_path)
    
    def handle(self, event):
        # ... fetch transcript ...
        
        # NEW: Save transcript to file
        transcript_path = self.transcript_saver.save_transcript(
            video_id=video_id,
            transcript_data=transcript_result,
            video_title=video_title,
            video_url=video_url,
            parent_note_name=file_path.stem
        )
        
        # Get wikilink
        transcript_link = self.transcript_saver.get_transcript_link(video_id)
        
        # ... extract quotes ...
        
        # NEW: Add transcript link to note
        self._add_transcript_link_to_note(file_path, transcript_link)
```

### **Configuration**

**Update**: `development/daemon_config.yaml`

```yaml
youtube_handler:
  enabled: true
  vault_path: ./knowledge
  
  # Transcript archival settings
  save_transcripts: true              # Enable transcript saving
  transcript_dir: Media/Transcripts   # Directory for transcripts
  add_frontmatter_link: true          # Add link to frontmatter
  add_body_link: true                 # Add link after title
  
  # Existing settings
  max_quotes: 7
  cooldown_seconds: 60
```

---

## 📋 Implementation Phases

### **Phase 1: Core Transcript Saver** ✅ COMPLETE (30 min)
**Goal**: Working transcript file generation

- [x] Create `youtube_transcript_saver.py`
- [x] Implement `save_transcript()` method
- [x] Implement frontmatter generation
- [x] Implement transcript body formatting
- [x] Add timestamp formatting utilities
- [x] Test with sample transcript data

**Status**: ✅ **COMPLETE** (TDD Iteration 1 - Commit: 992c3f0)
- 10/10 tests passing
- 353 LOC, 9 methods (ADR-001 compliant)
- Helper methods extracted during REFACTOR phase
- Full lessons learned documented

**Success Criteria**:
```python
saver = YouTubeTranscriptSaver(vault_path)
path = saver.save_transcript(
    video_id="dQw4w9WgXcQ",
    transcript_data=transcript,
    video_title="Test Video",
    video_url="https://youtube.com/watch?v=dQw4w9WgXcQ",
    parent_note_name="test-note"
)
# Creates: Media/Transcripts/youtube-dQw4w9WgXcQ-2025-10-17.md
```

### **Phase 2: Handler Integration** (20 min)
**Goal**: Automatic transcript saving during processing

- [ ] Add transcript saver to `YouTubeFeatureHandler.__init__`
- [ ] Call `save_transcript()` after fetching
- [ ] Generate wikilink for saved transcript
- [ ] Pass transcript link to note enhancer
- [ ] Test end-to-end flow

**Success Criteria**:
- Processing a YouTube note creates transcript file
- Transcript file contains full timestamped content
- No errors in handler processing

### **Phase 3: Note Linking** (20 min)
**Goal**: Bidirectional links between note and transcript

- [ ] Implement `_add_transcript_link_to_note()`
- [ ] Add `transcript_file` to note frontmatter
- [ ] Insert transcript link after note title
- [ ] Verify bidirectional linking works
- [ ] Test in Obsidian graph view

**Success Criteria**:
- Note frontmatter includes `transcript_file: [[...]]`
- Note body has "Full Transcript: [[...]]" link
- Clicking link opens transcript file
- Transcript has `parent_note: [[...]]` link back

### **Phase 4: Testing & Polish** (20 min)
**Goal**: Production-ready reliability

- [ ] Unit tests for `YouTubeTranscriptSaver`
- [ ] Integration tests with `YouTubeFeatureHandler`
- [ ] Test with various video lengths
- [ ] Test with special characters in titles
- [ ] Add error handling for file operations
- [ ] Update documentation

**Success Criteria**:
- All tests passing
- Handles edge cases gracefully
- Clear error messages
- Documentation updated

---

## 🧪 Testing Strategy

### **Unit Tests**

```python
# tests/unit/test_youtube_transcript_saver.py

def test_save_transcript_creates_file():
    """Saves transcript to correct location"""
    
def test_transcript_filename_format():
    """Uses format: youtube-{video_id}-{date}.md"""
    
def test_transcript_frontmatter():
    """Includes all required frontmatter fields"""
    
def test_transcript_timestamps():
    """Formats timestamps as MM:SS"""
    
def test_bidirectional_links():
    """Transcript includes parent_note link"""
    
def test_duplicate_handling():
    """Doesn't recreate if transcript exists"""
```

### **Integration Tests**

```python
# tests/integration/test_youtube_transcript_archival.py

def test_end_to_end_transcript_saving():
    """Full flow: process → save transcript → link note"""
    
def test_obsidian_linking():
    """Wikilinks work in Obsidian"""
    
def test_search_transcript_content():
    """Transcript content is searchable"""
```

### **Manual Testing Checklist**

- [ ] Process YouTube note → transcript file created
- [ ] Transcript file in Media/Transcripts/ directory
- [ ] Note has transcript link in frontmatter
- [ ] Note has transcript link in body
- [ ] Click link → opens transcript file
- [ ] Transcript has parent_note link back
- [ ] Obsidian graph shows connection
- [ ] Search finds transcript content
- [ ] Dashboard shows transcript metrics

---

## 📊 Success Criteria

### **Functional**
- ✅ Transcript saved for every processed video
- ✅ Bidirectional links work in both directions
- ✅ Timestamps properly formatted (MM:SS)
- ✅ Frontmatter includes all metadata
- ✅ File naming convention followed

### **User Experience**
- ✅ One-click access to full transcript from note
- ✅ One-click return to note from transcript
- ✅ Transcript searchable via Obsidian search
- ✅ Graph view shows note-transcript connections
- ✅ No duplicate transcripts created

### **Performance**
- ✅ Transcript saving adds <1s to processing time
- ✅ File operations don't block processing
- ✅ Handles long transcripts (>10,000 words)
- ✅ No memory issues with large transcripts

---

## 🔗 Related Files

### **Core Processing** (Existing)
- `development/src/ai/youtube_transcript_fetcher.py` - Fetches transcripts
- `development/src/automation/feature_handlers.py` - YouTubeFeatureHandler

### **New Files** (To Create)
- `development/src/ai/youtube_transcript_saver.py` - Transcript saving utility
- `tests/unit/test_youtube_transcript_saver.py` - Unit tests
- `tests/integration/test_youtube_transcript_archival.py` - Integration tests

### **Configuration**
- `development/daemon_config.yaml` - Add transcript settings

### **Directory Structure**
- `knowledge/Media/Transcripts/` - Transcript storage (auto-created)

---

## 🚀 Future Enhancements

### **Phase 5: Advanced Features** (Future)

**Transcript Search**
```python
# Search across all transcripts
def search_transcripts(query: str) -> List[Dict]:
    """Find videos discussing specific topics"""
```

**Quote Regeneration**
```python
# Extract additional quotes from saved transcript
def regenerate_quotes(transcript_file: Path, max_quotes: int):
    """Generate new quotes without re-fetching"""
```

**Transcript Analytics**
```python
# Analyze transcript quality
def analyze_transcript_quality(transcript_file: Path):
    """Word count, unique terms, reading time"""
```

**Multiple Format Export**
```yaml
transcript_formats:
  - markdown  # Default
  - json      # For programmatic access
  - txt       # Plain text
  - srt       # Subtitle format
```

### **Phase 6: Advanced Linking** (Future)

**Timestamp Links**
```markdown
## Quotes
- "Important concept" [[youtube-abc-2025-10-17#01:23]]
  Links to specific timestamp in transcript
```

**Multi-Video Comparison**
```markdown
## Related Transcripts
- [[youtube-video1-2025-10-17]] - Similar topic
- [[youtube-video2-2025-10-17]] - Counter-argument
```

---

## ⚠️ Known Constraints

### **Technical**
- Transcript file size can be large (50KB-500KB)
- One transcript per video per day (by design)
- Requires vault structure with Media/Transcripts/
- Wikilinks require Obsidian or compatible editor

### **Operational**
- Transcripts not retroactively created for existing notes
- Migration script needed for historical videos
- Transcript format is markdown-specific

### **Dependencies**
- YouTubeTranscriptFetcher (existing)
- Frontmatter utilities (existing)
- File system access for Media/ directory

---

## 📝 Decision Log

### **Why Separate Transcript Files?**
- **Decision**: Save transcripts as separate files
- **Rationale**:
  - Keeps notes focused on curated insights
  - Makes transcripts searchable independently
  - Enables transcript-specific features later
  - Better file size management
- **Trade-off**: Two files per video vs one large file

### **Why Media/Transcripts/ Directory?**
- **Decision**: Store in Media/Transcripts/ not Inbox/
- **Rationale**:
  - Transcripts are supporting media, not primary notes
  - Keeps Inbox/ focused on active notes
  - Allows transcript-specific organization
  - Consistent with other media storage (screenshots, images)
- **Trade-off**: Deeper directory nesting

### **Why Bidirectional Links?**
- **Decision**: Links in both note and transcript
- **Rationale**:
  - Easy navigation in both directions
  - Graph view shows relationships
  - Transcript context shows parent note
  - Note has quick access to full context
- **Trade-off**: Slightly more complex linking logic

### **Why Date in Filename?**
- **Decision**: Include date in transcript filename
- **Rationale**:
  - Supports re-processing same video later
  - Shows when transcript was fetched
  - Prevents filename collisions
  - Useful for transcript version tracking
- **Trade-off**: Longer filenames

---

## 📅 Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Core Transcript Saver | 30 min | None |
| Phase 2: Handler Integration | 20 min | Phase 1 complete |
| Phase 3: Note Linking | 20 min | Phase 2 complete |
| Phase 4: Testing & Polish | 20 min | Phases 1-3 complete |
| **Total** | **90 min** | - |

**Recommended Approach**:
1. Build transcript saver utility (testable in isolation)
2. Integrate into handler (verify saves work)
3. Add note linking (complete the flow)
4. Test thoroughly (production readiness)

---

## 🎯 Integration with Parent Project

This feature enhances the **YouTube API Trigger System** by:

1. **Complements API Trigger**: Works with both file watcher and API triggers
2. **Enhances Dashboard**: Can show transcript statistics
3. **Enables Search**: Full-text search across all video content
4. **Supports Analytics**: Transcript length, quality metrics
5. **Future-Proof**: Foundation for advanced features

**Dependency**: Can be implemented independently or as part of API trigger system

---

## 🎯 Next Actions

1. **Review this manifest** - confirm approach
2. **Create feature branch**: `feat/youtube-transcript-archival`
3. **Phase 1**: Build `YouTubeTranscriptSaver` utility
4. **Phase 2**: Integrate into `YouTubeFeatureHandler`
5. **Phase 3**: Add bidirectional linking
6. **Phase 4**: Test and document

---

**Last Updated**: 2025-10-17  
**Status**: 🟡 Ready for implementation  
**Owner**: @thaddius  
**Epic**: YouTube Processing Automation  
**Estimated Effort**: 90 minutes  
**Dependencies**: None (uses existing infrastructure)
