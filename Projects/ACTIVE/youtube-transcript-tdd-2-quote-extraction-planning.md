# TDD Iteration 2: Context-Aware Quote Extraction - Strategic Planning

**Date**: 2025-10-03 23:07 PDT  
**Last Updated**: 2025-10-03 23:20 PDT (Incorporated feedback)  
**Planning Phase**: Prompt Engineering & Architecture Design  
**Foundation**: TDD Iteration 1 Complete (10/10 tests, 412 entries in 2.4s)

---

## 📝 **Changelog: Feedback Incorporated**

**Date**: 2025-10-03 23:20 PDT  
**Status**: ✅ All recommended improvements approved and integrated

### **Changes Made:**

1. ✅ **Few-Shot Examples Added to Prompt**
   - Added example quote with all required fields
   - Improves LLM output consistency and format adherence
   - Location: Single-stage prompt design

2. ✅ **Edge Case Instructions Added**
   - Explicit handling for unclear timestamps ("XX:XX")
   - Empty array return for no high-quality quotes
   - No fabrication warning - verbatim text only
   - Lower score when uncertain about relevance

3. ✅ **11th Test Added: Malformed JSON Handling**
   - `test_handle_malformed_llm_json_response()`
   - Handles markdown-wrapped JSON (```json blocks)
   - Handles slightly broken JSON responses
   - Critical for production reliability

4. ✅ **Success Criteria Updated**
   - Test count: 10 → 11 tests
   - Added prompt quality requirements
   - Few-shot examples requirement
   - Edge case handling requirement

### **Deferred to Future Iterations:**
- 🔄 Token limit handling (REFACTOR phase if needed)
- 🔄 Quote deduplication (Iteration 5+)
- 🔄 Timestamp format variations (likely not needed)
- 📝 Prompt versioning (Iteration 5+)
- 📝 Caching strategy (Iteration 4 CLI)
- 📝 Complex fallback strategies (keep simple for MVP)
- ❌ Speaker attribution (out of scope)
- ❌ Language detection (out of scope)

---

## 🎯 **Core Objective**

**Build a context-aware quote extraction system that transforms YouTube transcripts into high-value knowledge quotes, guided by user insights and LLM intelligence.**

**Key Insight**: The user provides context/insights → LLM uses this to extract the MOST RELEVANT quotes → Result is personalized, not generic.

---

## 🧠 **Prompt Engineering Strategy**

### **The Core Challenge**

Traditional quote extraction approaches:
- ❌ Generic: "Extract the most important quotes"
- ❌ No context: Doesn't know WHY user watched video
- ❌ Overwhelming: Returns 20+ quotes, user has to filter
- ❌ Shallow: Picks obvious quotes, misses deep insights

**Our Approach: Context-Aware Intelligence**
- ✅ User-guided: "I watched this for X reason, help me find relevant quotes"
- ✅ Smart filtering: 3-7 high-quality quotes, not 20+ generic ones
- ✅ Quality scoring: Each quote gets relevance score
- ✅ Timestamp preservation: Easy to return to video context

---

## 📐 **System Architecture**

### **Class Structure**

```python
class ContextAwareQuoteExtractor:
    """
    Extracts high-quality quotes from YouTube transcripts using LLM intelligence
    and user-provided context for personalized relevance.
    """
    
    def __init__(self, ollama_client=None):
        """Initialize with Ollama client for LLM processing"""
        
    def extract_quotes(
        self, 
        transcript: str,           # LLM-ready transcript from Iteration 1
        user_context: str = None,  # User's reason for watching/insights
        max_quotes: int = 7,       # Target 3-7 quotes
        min_quality: float = 0.7   # Quality threshold
    ) -> Dict[str, Any]:
        """
        Extract context-aware quotes from transcript.
        
        Returns:
            {
                "quotes": [
                    {
                        "text": "quote text",
                        "timestamp": "MM:SS",
                        "relevance_score": 0.0-1.0,
                        "context": "why this matters",
                        "category": "key-insight|actionable|quote|definition"
                    }
                ],
                "summary": "Overall video summary",
                "key_themes": ["theme1", "theme2"],
                "processing_time": 5.2
            }
        """
```

### **Data Flow**

```
User Input (Video URL + Context)
    ↓
[Iteration 1] YouTubeTranscriptFetcher
    ↓ (412 entries, 2.4s)
LLM-Ready Transcript
    ↓
[Iteration 2] ContextAwareQuoteExtractor
    ↓ (User context guides LLM)
LLM Processing (Ollama)
    ↓
3-7 High-Quality Quotes
    ↓
[Iteration 3] Template Integration
    ↓
Enhanced YouTube Note
```

---

## 🎭 **Prompt Engineering Design**

### **Strategy 1: Two-Stage Prompting (RECOMMENDED)**

**Stage 1: Analysis & Theme Extraction**
```python
analysis_prompt = f"""
You are analyzing a YouTube video transcript to extract key themes and insights.

USER CONTEXT:
{user_context or "No specific context provided - extract generally important insights"}

TRANSCRIPT:
{transcript}

Your task:
1. Identify 3-5 key themes in this video
2. Note the most insightful moments
3. Identify actionable takeaways
4. Flag any unique/surprising insights

Return a JSON object with:
{{
    "key_themes": ["theme1", "theme2", ...],
    "insight_moments": [
        {{"timestamp": "MM:SS", "insight": "description"}}
    ],
    "actionable_items": ["item1", "item2"],
    "unique_insights": ["insight1", "insight2"]
}}
"""
```

**Stage 2: Quote Extraction (Context-Aware)**
```python
extraction_prompt = f"""
You are extracting high-quality quotes from a YouTube transcript.

USER CONTEXT: {user_context}

KEY THEMES IDENTIFIED: {themes_from_stage_1}

TRANSCRIPT:
{transcript}

Extract 3-7 quotes that:
1. Align with user's context/interests
2. Represent key themes identified
3. Are self-contained and meaningful
4. Include actionable insights where possible
5. Preserve speaker's exact words

For each quote, provide:
- exact_text: The verbatim quote
- timestamp: MM:SS format
- relevance_score: 0.0-1.0 (how relevant to user context)
- context: Why this quote matters
- category: "key-insight" | "actionable" | "quote" | "definition"

Return JSON array of quote objects.
"""
```

**Why Two-Stage?**
- ✅ LLM gets better context from its own theme analysis
- ✅ Reduces hallucination (themes grounded in transcript)
- ✅ More accurate relevance scoring
- ✅ Better alignment with user context

### **Strategy 2: Single-Stage with Rich Context (ALTERNATIVE)**

```python
single_stage_prompt = f"""
You are an expert at extracting high-value quotes from YouTube video transcripts.

USER'S CONTEXT FOR WATCHING THIS VIDEO:
{user_context or "User wants to capture key insights and actionable takeaways"}

YOUR TASK:
Analyze this transcript and extract 3-7 quotes that would be MOST VALUABLE 
for someone who watched this video for the reason described above.

QUALITY CRITERIA:
- Must be verbatim from transcript (no paraphrasing)
- Must be self-contained and meaningful
- Must align with user's learning goals
- Prefer actionable insights over generic statements
- Prefer unique/surprising insights over obvious ones

TRANSCRIPT WITH TIMESTAMPS:
{transcript}

EXAMPLE OUTPUT (Few-Shot Learning):
{{
    "text": "AI will amplify individual creators by 10x in the next few years",
    "timestamp": "01:15",
    "relevance_score": 0.88,
    "context": "Directly addresses creator economy trends that user is interested in",
    "category": "actionable"
}}

IMPORTANT EDGE CASES:
- If timestamp is unclear or missing, use "XX:XX"
- If no high-quality quotes found (all below threshold), return empty quotes array
- NEVER fabricate quotes - only use verbatim text from transcript
- If unsure about relevance, err on the side of lower score

RETURN FORMAT (JSON):
{{
    "summary": "2-3 sentence video overview",
    "quotes": [
        {{
            "text": "exact quote text",
            "timestamp": "MM:SS",
            "relevance_score": 0.0-1.0,
            "context": "why this matters for user",
            "category": "key-insight|actionable|quote|definition"
        }}
    ],
    "key_themes": ["theme1", "theme2", "theme3"]
}}

Focus on quality over quantity. 3 great quotes > 7 mediocre quotes.
"""
```

**Why Single-Stage?**
- ✅ Faster (1 LLM call vs 2)
- ✅ Simpler implementation
- ✅ Easier to test
- ❌ May produce less accurate relevance scores

---

## 🎯 **Recommended Approach: Hybrid Strategy**

### **Implementation Plan**

**Phase 1: Start Simple (Single-Stage)**
- Build with single-stage prompt for MVP
- Validate quote quality with real transcripts
- Measure performance and accuracy

**Phase 2: Add Two-Stage if Needed**
- If quote quality insufficient, upgrade to two-stage
- A/B test both approaches
- Choose based on results

**Rationale**:
- TDD methodology prefers simple → complex
- Single-stage easier to test and validate
- Can refactor to two-stage if needed (REFACTOR phase)

---

## 📊 **Test-Driven Development Plan**

### **RED Phase: 11 Failing Tests** (Updated with feedback)

```python
class TestContextAwareQuoteExtractor:
    
    # P0: Core Functionality (4 tests)
    def test_extract_quotes_from_transcript(self):
        """Extract 3-7 quotes from valid transcript"""
        
    def test_extract_quotes_with_user_context(self):
        """User context influences quote selection"""
        
    def test_extract_quotes_without_context(self):
        """Works with no user context (generic extraction)"""
        
    def test_quotes_include_timestamps(self):
        """All quotes preserve MM:SS timestamps"""
    
    # P0: Quality & Filtering (3 tests)
    def test_quote_quality_scoring(self):
        """Each quote has relevance_score 0.0-1.0"""
        
    def test_filter_low_quality_quotes(self):
        """Quotes below min_quality threshold excluded"""
        
    def test_limit_max_quotes(self):
        """Returns max_quotes or fewer (3-7 target)"""
    
    # P0: Error Handling (3 tests) ← ADDED MALFORMED JSON TEST
    def test_handle_empty_transcript(self):
        """Graceful error for empty transcript"""
        
    def test_handle_ollama_unavailable(self):
        """Fallback when LLM service down"""
    
    def test_handle_malformed_llm_json_response(self):
        """Parse quotes even if LLM returns markdown-wrapped or slightly broken JSON"""
    
    # P1: Advanced Features (1 test)
    def test_categorize_quotes_by_type(self):
        """Quotes categorized: key-insight, actionable, quote, definition"""
```

### **Performance Targets**

| Metric | Target | Rationale |
|--------|--------|-----------|
| Processing Time | <10s per transcript | User tolerance for AI processing |
| Quote Count | 3-7 quotes | Quality over quantity |
| Quality Score | >0.7 average | High relevance to user context |
| Timestamp Accuracy | 100% | Must preserve video context |
| LLM Calls | 1-2 max | Cost and speed optimization |

---

## 🔧 **Implementation Details**

### **Ollama Integration Pattern** (from existing codebase)

```python
from src.clients.ollama_client import OllamaClient

class ContextAwareQuoteExtractor:
    def __init__(self, ollama_client=None):
        self.ollama_client = ollama_client or OllamaClient()
        
    def extract_quotes(self, transcript, user_context=None, max_quotes=7, min_quality=0.7):
        # Build prompt using strategy
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(transcript, user_context)
        
        try:
            # Generate using Ollama (follows existing pattern)
            response = self.ollama_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            # Filter by quality threshold
            filtered_quotes = [
                q for q in result['quotes'] 
                if q['relevance_score'] >= min_quality
            ]
            
            # Limit to max_quotes
            return {
                'quotes': filtered_quotes[:max_quotes],
                'summary': result.get('summary', ''),
                'key_themes': result.get('key_themes', []),
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            logger.error(f"Quote extraction failed: {e}")
            # Fallback: Return empty with error
            return {
                'quotes': [],
                'error': str(e),
                'fallback': True
            }
```

### **JSON Response Parsing**

**Challenge**: LLMs sometimes return markdown-wrapped JSON

```python
def _parse_llm_json_response(self, response: str) -> dict:
    """Parse JSON from LLM response, handling markdown wrappers"""
    # Remove markdown code blocks if present
    response = re.sub(r'^```json\n?', '', response, flags=re.MULTILINE)
    response = re.sub(r'\n?```$', '', response, flags=re.MULTILINE)
    response = response.strip()
    
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parse failed, attempting repair: {e}")
        # Attempt basic repairs (trailing commas, unquoted keys, etc)
        return self._repair_and_parse_json(response)
```

---

## 🎨 **User Experience Design**

### **CLI Interface** (Iteration 4 Preview)

```bash
# Future CLI command
python3 development/src/cli/workflow_demo.py \
    --process-youtube-notes \
    --url "https://youtube.com/watch?v=..." \
    --context "I want to learn about AI trends for 2026"

# Output:
✅ Transcript fetched: 412 entries (2.4s)
🤖 Extracting quotes with context: "AI trends for 2026"
✅ Found 5 high-quality quotes (avg score: 0.85)

Top Quotes:
[00:03] "Number one, the individual empire..." (0.92 - key-insight)
[01:15] "AI will amplify individual creators..." (0.88 - actionable)
...

✅ YouTube note created: knowledge/Inbox/youtube-2026-ai-trends.md
```

### **Template Integration** (Iteration 3 Preview)

```yaml
---
type: literature
source: youtube
url: https://youtube.com/watch?v=...
created: 2025-10-03 23:00
status: inbox
tags: [ai-trends, youtube, 2026-predictions]
ai_processed: true
quote_count: 5
avg_quality: 0.85
---

# 5 AI Trends That Will Define 2026

**User Context**: Learning about AI trends for 2026

## Summary
[2-3 sentence AI-generated summary]

## Key Themes
- Individual empires and creator economy
- AI amplification of human creativity
- [theme 3]

## Quotes

### [00:03] Individual Empire
> "Number one, the individual empire. As I think about..."

**Why this matters**: Represents shift toward solo creator economy
**Category**: key-insight
**Relevance**: 0.92

### [01:15] AI Amplification
> "AI will amplify individual creators..."

**Why this matters**: Actionable insight for content creators
**Category**: actionable
**Relevance**: 0.88
```

---

## 🧪 **Testing Strategy**

### **Unit Tests** (Mocked LLM)

```python
@pytest.fixture
def mock_ollama_response():
    return json.dumps({
        "summary": "Video discusses 5 key AI trends...",
        "quotes": [
            {
                "text": "Number one, the individual empire",
                "timestamp": "00:03",
                "relevance_score": 0.92,
                "context": "Shift toward solo creators",
                "category": "key-insight"
            }
        ],
        "key_themes": ["creator economy", "AI trends"]
    })

def test_extract_quotes_from_transcript(mock_ollama):
    extractor = ContextAwareQuoteExtractor(ollama_client=mock_ollama)
    result = extractor.extract_quotes(sample_transcript)
    
    assert len(result['quotes']) <= 7
    assert all(q['relevance_score'] >= 0.7 for q in result['quotes'])
    assert all('timestamp' in q for q in result['quotes'])
```

### **Integration Tests** (Real LLM)

```python
def test_real_quote_extraction_with_user_video():
    """Test with user's actual video from Iteration 1"""
    # Use real transcript from test_your_video.py
    fetcher = YouTubeTranscriptFetcher()
    transcript_result = fetcher.fetch_transcript("-9iDW7Zgv1Q")
    llm_text = fetcher.format_for_llm(transcript_result['transcript'])
    
    # Extract quotes with real LLM
    extractor = ContextAwareQuoteExtractor()
    quotes_result = extractor.extract_quotes(
        llm_text,
        user_context="I want to learn about AI trends for 2026"
    )
    
    # Validate real results
    assert len(quotes_result['quotes']) >= 3
    assert quotes_result['processing_time'] < 10.0
    print(f"Extracted {len(quotes_result['quotes'])} quotes")
    for q in quotes_result['quotes']:
        print(f"[{q['timestamp']}] {q['text'][:50]}... (score: {q['relevance_score']})")
```

---

## 📋 **Development Checklist**

### **Before Starting (Planning Phase)** ✅
- [x] Read TDD Iteration 1 lessons learned
- [x] Review existing prompt patterns (summarizer, tagger, enhancer)
- [x] Design prompt engineering strategy
- [x] Plan test suite (10 tests)
- [x] Document architecture and data flow

### **RED Phase** (Est. 15 minutes)
- [ ] Create branch: `feat/youtube-quote-extraction-tdd-2`
- [ ] Write 10 failing tests with NotImplementedError
- [ ] Run tests: Confirm 10 failures
- [ ] Commit: "feat: TDD Iteration 2 RED Phase - 10 failing tests"

### **GREEN Phase** (Est. 60 minutes)
- [ ] Implement ContextAwareQuoteExtractor class
- [ ] Build single-stage prompt (start simple)
- [ ] Add JSON response parsing with error handling
- [ ] Integrate with OllamaClient (existing pattern)
- [ ] Add quality filtering and quote limiting
- [ ] Run tests: Get to 10/10 passing
- [ ] Real video validation (user's video from Iteration 1)
- [ ] Commit: "feat: TDD Iteration 2 GREEN Phase - Complete implementation"

### **REFACTOR Phase** (Est. 15 minutes)
- [ ] Extract helper methods (_build_prompt, _parse_response, etc)
- [ ] Add comprehensive logging (INFO/DEBUG/WARNING/ERROR)
- [ ] Enhance docstrings with examples
- [ ] Add type hints everywhere
- [ ] Consider two-stage prompt if quality insufficient
- [ ] Run tests: Confirm 10/10 still passing
- [ ] Commit: "feat: TDD Iteration 2 REFACTOR Phase - Production polish"

### **Documentation Phase** (Est. 15 minutes)
- [ ] Create lessons learned document
- [ ] Document prompt engineering insights
- [ ] Update project-todo-v3.md
- [ ] Commit: "docs: TDD Iteration 2 Complete - Lessons learned"

---

## 🎯 **Success Criteria**

### **Must Have (P0)**
- ✅ 11/11 tests passing (added malformed JSON handling)
- ✅ Real video quote extraction working (<10s)
- ✅ 3-7 high-quality quotes extracted
- ✅ User context influences quote selection
- ✅ Timestamps preserved in all quotes
- ✅ Quality scores >=0.7 average
- ✅ Few-shot examples in prompt for consistency
- ✅ Edge case instructions to prevent hallucination

### **Should Have (P1)**
- ✅ Quote categorization (key-insight, actionable, etc)
- ✅ Summary generation
- ✅ Key themes extraction
- ✅ Graceful LLM unavailability handling

### **Nice to Have (P2)**
- 🔄 Two-stage prompting (if quality insufficient)
- 🔄 A/B testing framework for prompt variants
- 🔄 User feedback collection for quote relevance

---

## 💡 **Key Design Decisions**

### **Decision 1: Single-Stage vs Two-Stage Prompting**
**Choice**: Start with single-stage, upgrade if needed  
**Rationale**: TDD prefers simple → complex; easier to test

### **Decision 2: JSON Response Format**
**Choice**: Structured JSON with quotes array  
**Rationale**: Easy to parse, test, and integrate with templates

### **Decision 3: Quality Threshold**
**Choice**: Default 0.7, user-configurable  
**Rationale**: Matches existing quality scoring patterns

### **Decision 4: Quote Count**
**Choice**: Target 3-7, hard limit at max_quotes param  
**Rationale**: Quality over quantity; user can adjust

### **Decision 5: User Context Optional**
**Choice**: Works with or without user context  
**Rationale**: Flexibility; generic extraction if no context

---

## 🚀 **Ready to Start?**

**Preparation Complete**: ✅ All planning done  
**Next Step**: Create RED phase tests  
**Estimated Total Time**: ~90 minutes (following TDD Iteration 1 pattern)

**When you're ready, say "Let's start RED phase" and we'll create the 10 failing tests!**

---

**Planning Document Version**: 1.0  
**Part of**: YouTube Transcript AI Processing System (4-iteration roadmap)  
**Next**: TDD Iteration 2 RED Phase
