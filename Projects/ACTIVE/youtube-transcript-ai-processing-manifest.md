# YouTube Transcript AI Processing System - Project Manifest

**Status**: 📋 PLANNING - Ready for TDD Implementation  
**Type**: Phase 5 Extension (Integration Project)  
**Priority**: High-Impact Workflow Enhancement  
**Created**: 2025-10-03  
**Last Updated**: 2025-10-03 10:57 PDT

---

## 🎯 Project Vision

Transform YouTube video consumption into AI-enhanced knowledge extraction by using **your human insight as context** to guide intelligent transcript processing. This addresses a critical workflow gap: YouTube videos are a major input to your maker hours, but currently require manual quote extraction and connection building.

### User Story
> "As a knowledge worker who spends maker hours watching YouTube videos, I want the system to automatically extract relevant quotes with timestamps based on my initial insight, so that I can focus on synthesis and connection-making rather than manual transcription."

---

## 📊 Current State Analysis

### Existing Template (youtube-video.md)
✅ **Working**: 2-prompt capture (URL + reason)  
✅ **Auto-fetches**: Title, channel, thumbnail (oEmbed API)  
✅ **Manual sections**: Key takeaways, timestamps, quotes (user fills)

### Gap
❌ **Manual quote extraction**: User must watch, pause, transcribe  
❌ **No timestamp automation**: User must track video position  
❌ **No content analysis**: LLM doesn't see video content  
❌ **Disconnected from AI workflows**: Not integrated with connection discovery, tagging

---

## 🎯 Success Criteria

### Must Have (MVP)
- [ ] Fetch full YouTube transcript with timestamps
- [ ] Process transcript using user's initial insight as context
- [ ] Extract 3-7 quality-based quotes with timestamps
- [ ] Store in structured format within literature note
- [ ] Automated background processing + on-demand CLI command
- [ ] Graceful fallback for videos without transcripts

### Nice to Have (Future)
- [ ] User-guided quote selection ("find quotes about X topic")
- [ ] Integration with existing connection discovery
- [ ] Auto-suggest [[wiki-links]] based on transcript content
- [ ] Enhanced tagging from transcript semantic analysis
- [ ] Quality scoring for extracted quotes

---

## 🏗️ Technical Architecture

### Phase 1: Transcript Fetching (TDD Iteration 1)
**Goal**: Reliably fetch YouTube transcripts with timestamps

**Components**:
```python
class YouTubeTranscriptFetcher:
    """Fetches transcripts using youtube-transcript-api library"""
    
    def fetch_transcript(self, video_id: str) -> List[TranscriptSegment]:
        """
        Fetch transcript with timestamps
        Returns: [{"text": "...", "start": 0.0, "duration": 2.5}, ...]
        """
        
    def get_available_languages(self, video_id: str) -> List[str]:
        """Check which transcript languages are available"""
        
    def format_for_storage(self, transcript: List) -> str:
        """Convert to markdown-friendly format"""
```

**Dependencies**: `youtube-transcript-api` (Python library, no API key)

**Tests**:
- Fetch transcript for valid video ID
- Handle videos without transcripts (graceful fallback)
- Handle manual vs auto-generated transcripts
- Format timestamps for markdown display
- Error handling for rate limits, network issues

---

### Phase 2: Context-Aware Quote Extraction (TDD Iteration 2)
**Goal**: Use user insight to guide LLM quote extraction

**Components**:
```python
class ContextAwareQuoteExtractor:
    """Uses user insight + transcript to extract relevant quotes"""
    
    def extract_quotes(
        self, 
        transcript: str, 
        user_insight: str,
        min_quotes: int = 3,
        max_quotes: int = 7
    ) -> List[ExtractedQuote]:
        """
        Returns: [
            {
                "quote": "...",
                "timestamp": "3:42",
                "relevance_score": 0.85,
                "why_relevant": "Connects to user's interest in..."
            }
        ]
        """
        
    def _build_llm_prompt(self, transcript: str, insight: str) -> str:
        """Construct prompt that uses insight as extraction context"""
```

**LLM Prompt Strategy**:
```
You are analyzing a YouTube video transcript to extract key quotes.

USER'S INSIGHT: "{user_insight}"

Based on this insight, extract 3-7 quotes from the transcript that:
1. Directly relate to the user's stated interest
2. Are substantive (2-3 sentences minimum)
3. Stand alone and provide value
4. Include exact timestamp for reference

TRANSCRIPT:
{transcript_with_timestamps}

Return quotes in JSON format with timestamp, text, and relevance explanation.
```

**Tests**:
- Extract quotes guided by short insight (1-2 sentences)
- Handle rambling insights (longer, less structured)
- Quality-based selection (relevance scoring)
- Timestamp accuracy preservation
- Handle edge cases (no relevant quotes found)

---

### Phase 3: Template Integration & Storage (TDD Iteration 3)
**Goal**: Seamlessly integrate into youtube-video.md workflow

**Template Enhancement**:
```markdown
## AI-Extracted Insights
*Processed based on: "{user_insight}"*

### Key Quotes

#### Quote 1 [3:42]
> "Exact transcript quote here..."

**Why This Matters**: AI explanation of relevance to your insight

**Your Notes**: <!-- Add your thoughts -->

---

## Full Transcript
<details>
<summary>Click to expand full transcript</summary>

[00:00] Opening segment...
[00:15] Key point about...
...

</details>
```

**Processing Flow**:
```
1. User creates note (2 prompts: URL + insight)
2. Template saves to Inbox/
3a. Automated: Background daemon detects new youtube note
3b. On-demand: User runs `--process-youtube-notes`
4. System fetches transcript
5. LLM extracts quotes using insight as context
6. Updates note file with AI-extracted section
7. Adds processing metadata to frontmatter
```

**Tests**:
- End-to-end note creation → processing → update
- Preserve user's original content
- Handle concurrent processing safely
- Update frontmatter with processing status
- Integration with existing WorkflowManager

---

### Phase 4: CLI & Automation Integration (TDD Iteration 4)
**Goal**: Dual-mode processing (automated + on-demand)

**CLI Commands**:
```bash
# On-demand processing
python3 development/src/cli/workflow_demo.py knowledge/ --process-youtube-notes

# Process specific note
python3 development/src/cli/workflow_demo.py knowledge/ --process-youtube-note path/to/note.md

# Dry-run mode
python3 development/src/cli/workflow_demo.py knowledge/ --process-youtube-notes --preview

# Reprocess with different insight
python3 development/src/cli/workflow_demo.py knowledge/ --reprocess-youtube-note path/to/note.md
```

**Automated Processing**:
- Integrate with existing AutoProcessor daemon
- Detect new `source: youtube` notes in Inbox/
- Process during low-activity periods
- Add to weekly review summary

**Tests**:
- CLI command execution
- Batch processing multiple notes
- Dry-run preview functionality
- Daemon integration
- Performance (<30s per video)

---

## 🔗 Integration Points

### Existing Components to Leverage
1. **WorkflowManager** (`src/ai/workflow_manager.py`)
   - Quality scoring framework
   - AI processing infrastructure
   - Batch processing patterns

2. **Connection Discovery** (`src/ai/connections.py`)
   - Semantic similarity for transcript analysis
   - Link suggestion based on content
   - **BACKLOG**: Investigate transcript → wiki-link automation

3. **AutoProcessor** (`development/src/cli/auto_processor.py`)
   - Background daemon infrastructure
   - File watching patterns
   - Scheduled task execution

4. **Literature Note Templates** (`knowledge/Templates/literature.md`)
   - Existing structure patterns
   - AI-enhanced sections
   - Quote formatting standards

### New Dependencies
- `youtube-transcript-api`: Python library for transcript fetching (MIT license)
- Ollama LLM: Existing infrastructure for quote extraction
- No YouTube API key required for MVP (transcripts are public)

---

## 📋 Implementation Plan

### TDD Iteration 1: Transcript Fetching (Week 1)
- [ ] Install `youtube-transcript-api` dependency
- [ ] Write failing tests for transcript fetching
- [ ] Implement `YouTubeTranscriptFetcher` class
- [ ] Handle edge cases (no transcript, rate limits)
- [ ] Real data validation with 5+ test videos

### TDD Iteration 2: Quote Extraction (Week 1-2)
- [ ] Write failing tests for context-aware extraction
- [ ] Implement `ContextAwareQuoteExtractor` class
- [ ] Optimize LLM prompts for quote quality
- [ ] Test with varied insight styles (short, rambling, structured)
- [ ] Validate quote relevance with real user insights

### TDD Iteration 3: Template Integration (Week 2)
- [ ] Extend youtube-video.md template with AI sections
- [ ] Implement note update logic (preserve user content)
- [ ] Add processing metadata to frontmatter
- [ ] Test end-to-end workflow
- [ ] Real data validation with existing YouTube notes

### TDD Iteration 4: CLI & Automation (Week 2-3)
- [ ] Implement CLI commands in workflow_demo.py
- [ ] Integrate with AutoProcessor daemon
- [ ] Add batch processing capabilities
- [ ] Performance optimization (<30s per video)
- [ ] Production deployment and user validation

---

## 🚀 User Value Proposition

### Time Savings
- **Before**: 30-60 min per video (watch, pause, transcribe, organize)
- **After**: 2 prompts + automated processing = 5 min active time
- **ROI**: 83-90% time reduction on YouTube knowledge capture

### Quality Improvements
- Exact quotes with timestamps (no paraphrasing errors)
- AI identifies connections you might miss
- Consistent structure for all video notes
- Full transcript for future reference/search

### Workflow Integration
- Fits into existing maker hours routine
- Compatible with weekly review process
- Leverages existing AI infrastructure
- Minimal disruption to current templates

---

## 📊 Success Metrics

### Technical
- [ ] 100% test coverage for core components
- [ ] <30s processing time per video
- [ ] >90% transcript fetch success rate
- [ ] Zero data loss (preserve all user content)
- [ ] Graceful fallback for edge cases

### User Experience
- [ ] Still only 2 prompts (URL + insight)
- [ ] AI-extracted quotes rated >70% relevant
- [ ] Users review/approve quotes vs re-extract manually
- [ ] Integration feels seamless with existing workflows
- [ ] Positive feedback on time savings

---

## 🔄 Future Enhancements (Post-MVP)

### Phase 2 Features (Backlog)
- [ ] **User-guided extraction**: "Find quotes about X topic" prompts
- [ ] **Connection Discovery Integration**: Auto-link transcript content to existing notes
- [ ] **Enhanced Tagging**: Generate tags from transcript semantic analysis
- [ ] **Multi-language Support**: Handle non-English transcripts
- [ ] **YouTube Data API v3**: Fetch description, official tags, category

### Phase 3 Features (Long-term)
- [ ] **Summarization**: AI-generated video summaries
- [ ] **Chapter Detection**: Identify major sections/topics
- [ ] **Visual Analysis**: Integrate with frame extraction for key moments
- [ ] **Playlist Processing**: Batch process entire playlists
- [ ] **Export Formats**: Anki cards, study guides from transcripts

---

## 🛡️ Risk Mitigation

### Technical Risks
- **Transcript unavailable**: Fallback to manual entry, prompt user
- **Rate limiting**: Implement exponential backoff, queue system
- **LLM quality issues**: Allow manual re-processing with adjusted prompts
- **Processing time**: Implement async processing, progress indicators

### User Experience Risks
- **Over-extraction**: Limit to 3-7 quotes, quality thresholds
- **Irrelevant quotes**: User insight guides relevance, allow regeneration
- **Data preservation**: Comprehensive backups, non-destructive updates
- **Workflow disruption**: Maintain 2-prompt simplicity, automation optional

---

## 📚 References

- **Existing Manifest**: `Projects/inneros-manifest-v3.md`
- **Template**: `knowledge/Templates/youtube-video.md`
- **Current TODO**: `Projects/ACTIVE/project-todo-v3.md`
- **Backlog Entry**: Added 2025-10-03 under "Template & Workflow Enhancements"

---

**Next Action**: Create TDD Iteration 1 branch when ready to implement after current sprint priorities.
