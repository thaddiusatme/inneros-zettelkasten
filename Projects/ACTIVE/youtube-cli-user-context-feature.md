# YouTube CLI Enhancement: User Context Integration

**Status**: 📋 Backlog  
**Priority**: P1 (High Value, Low Effort)  
**Created**: 2025-10-06  
**Type**: Feature Enhancement  
**Component**: YouTube CLI  

---

## 🎯 Feature Request

**Title**: Extract quotes based on user's existing Key Takeaways

**User Story**: As a user processing YouTube notes, I want the AI to extract quotes that relate to my existing Key Takeaways, so that the extracted quotes are more relevant to what I found interesting.

---

## 📝 Background

### Current Behavior
The YouTube CLI extracts quotes using AI based solely on the video transcript. The AI has no awareness of:
- User's manually captured Key Takeaways
- User's specific interests
- What the user found noteworthy while watching

### Example from Real Use
```markdown
## Key Takeaways
Dev numbers has doubled
    Acceleration is real!
OpenAI is trying to make it easier to work with AI

building apps within ChatGPT with distribution
    - ChatGPT for developers within the ChatGPT UI 
    - Apps SDK!
    - agentic checkout
    - learning is one of the top use-cases
Building agents
AI writing Code
API updates!
```

**Currently**: AI extracts generic quotes  
**Desired**: AI extracts quotes related to these specific topics

---

## 🎯 Proposed Solution

### Option A: Automatic Section Parsing (Recommended)
**Description**: Parse existing note content and use as context automatically

**Implementation**:
```python
def extract_user_context(note_content: str) -> str:
    """Extract user's Key Takeaways section as context"""
    # Parse markdown sections
    # Extract "## Key Takeaways" or "## Why I'm Saving This"
    # Return as context string
```

**Pros**:
- ✅ Zero user friction (automatic)
- ✅ Works with existing note structure
- ✅ Encourages good note-taking habits

**Cons**:
- ⚠️ Assumes consistent section naming
- ⚠️ May miss context if section missing

---

### Option B: CLI Parameter (Flexible)
**Description**: Add `--context` parameter for manual context

**Usage**:
```bash
# With inline context
python3 youtube_cli.py process-note note.md --context "I'm interested in APIs and developer tools"

# With file context
python3 youtube_cli.py process-note note.md --context-file takeaways.txt
```

**Pros**:
- ✅ Maximum flexibility
- ✅ Works for any use case
- ✅ Can combine with automatic parsing

**Cons**:
- ⚠️ Requires manual input
- ⚠️ Extra friction for users

---

### Option C: Hybrid Approach (Best)
**Description**: Automatic parsing with optional manual override

**Implementation**:
1. **First**: Try to parse "Key Takeaways" from existing note
2. **Then**: If `--context` provided, append/override
3. **Finally**: Pass combined context to AI

**Example**:
```python
# Automatic context from note
context = extract_user_context(note_content)

# Add/override with manual context if provided
if args.context:
    context = f"{context}\n\nAdditional focus: {args.context}"

# Pass to AI
quotes = extractor.extract_quotes(
    transcript=transcript,
    user_context=context  # ← This parameter already exists!
)
```

---

## 🔧 Technical Details

### Existing Infrastructure
The `YouTubeQuoteExtractor.extract_quotes()` **already accepts** `user_context`:

```python
def extract_quotes(
    self,
    transcript: str,
    user_context: Optional[str] = None,  # ← Already exists!
    max_quotes: int = 7,
    min_quality: float = 0.7
) -> Dict[str, Any]:
```

**Current CLI Implementation**:
```python
# We're currently passing user_context=None
quotes_result = processor.extractor.extract_quotes(llm_transcript)
```

**Needed Change**:
```python
# Extract context from note
user_context = extract_user_context(note_content)

# Pass to extractor
quotes_result = processor.extractor.extract_quotes(
    llm_transcript,
    user_context=user_context  # ← Just add this!
)
```

---

## 📋 Implementation Plan

### Phase 1: Automatic Context Parsing (2 hours)
**Tasks**:
1. ✅ Add `extract_user_context()` function to `youtube_cli_utils.py`
2. ✅ Parse common sections: "Key Takeaways", "Why I'm Saving This", "My Thoughts"
3. ✅ Extract bullet points and key phrases
4. ✅ Clean and format for AI prompt
5. ✅ Add to `process_single_note()` flow

**Acceptance Criteria**:
- Extracts Key Takeaways section if present
- Passes to AI as user_context
- Falls back gracefully if section missing
- Doesn't break existing functionality

---

### Phase 2: CLI Parameter Support (1 hour)
**Tasks**:
1. ✅ Add `--context` parameter to argparse
2. ✅ Add `--context-file` parameter
3. ✅ Merge automatic + manual context
4. ✅ Update help documentation

**Acceptance Criteria**:
- `--context "text"` works
- `--context-file path.txt` works
- Manual context appends to automatic
- Help text clear and actionable

---

### Phase 3: Testing & Validation (1 hour)
**Tasks**:
1. ✅ Test with real notes (Sam Altman keynote)
2. ✅ Compare quotes with/without context
3. ✅ Verify relevance improvement
4. ✅ Update README with examples

**Acceptance Criteria**:
- Extracted quotes match user interests
- Context-aware quotes more relevant
- Documentation includes examples
- Zero breaking changes

---

## 📊 Success Metrics

**How we'll know this works**:
1. **Relevance Score**: Extracted quotes align with Key Takeaways topics
2. **User Feedback**: "These quotes match what I found interesting"
3. **Coverage**: At least 70% of Key Takeaways topics covered in quotes
4. **No Degradation**: Still extracts quality quotes when context missing

**Example Test Case**:
```
Key Takeaways: "Apps SDK, agentic checkout, building agents"
Expected Quotes: Should mention SDK, agents, or app-building
Actual Quotes: [Compare with/without context]
```

---

## 🚀 Estimated Effort

**Total**: ~4 hours
- Phase 1: 2 hours (core feature)
- Phase 2: 1 hour (CLI enhancements)
- Phase 3: 1 hour (testing)

**Complexity**: Low
- ✅ AI infrastructure already exists (`user_context` parameter)
- ✅ Just need to parse markdown and pass data
- ✅ No new dependencies
- ✅ Follows existing patterns

---

## 📚 Related Work

### Existing Features
- ✅ YouTube quote extraction (working)
- ✅ User context parameter (implemented but unused)
- ✅ Markdown parsing utilities (frontmatter parser exists)

### Similar Patterns
- **Smart Link Management**: Context-aware link suggestions
- **Advanced Tag Enhancement**: Context from note content
- **Connection Discovery**: Uses note content for similarity

---

## 🎯 Next Steps

1. **Review & Prioritize**: Discuss with user
2. **TDD Iteration 4**: Plan RED → GREEN → REFACTOR
3. **Write Tests**: Context extraction, merging, AI integration
4. **Implement**: Following proven TDD patterns
5. **Validate**: Test with real notes and user feedback

---

## 💡 Future Enhancements

**Post-MVP Ideas**:
- **Learning User Preferences**: Track which quotes user keeps/deletes
- **Adaptive Context**: Adjust extraction based on user's note-taking style
- **Multi-Note Context**: Use related notes as additional context
- **Category Preferences**: Learn which quote categories user values
- **Quality Feedback Loop**: User rates quotes, AI learns over time

---

## 📎 References

- **Working Example**: `lit-20251006-1706-openai-devday-2025-opening-keynote-with-sam-altman.md.md`
- **User Request**: Session on 2025-10-06 20:10
- **Existing Code**: `development/src/cli/youtube_cli_utils.py`
- **API Docs**: `YouTubeQuoteExtractor.extract_quotes()` already supports `user_context`

---

**Status**: Ready for implementation when prioritized  
**Estimated ROI**: High (low effort, high user value)  
**Risk**: Low (uses existing infrastructure)
