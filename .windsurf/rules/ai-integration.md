# AI Integration Guidelines

> **Purpose**: AI capabilities, usage patterns, ethics & transparency  
> **Updated**: 2025-08-10  

## 🤖 AI Integration Guidelines (Current State)

### Phase 5 AI Capabilities (COMPLETED)
- ✅ Smart Tagging: Context-aware auto-tagging (3-8 tags/note)
- ✅ Quality Scoring: 0-1 scale with actionable feedback
- ✅ Summarization: Both abstractive (AI) and extractive methods
- ✅ Connection Discovery: Semantic similarity + link suggestions
- ✅ Weekly Review: Automated promotion candidates with rationale
- ✅ Analytics Dashboard: Temporal analysis, productivity metrics
- ✅ Enhanced Metrics: Orphaned/stale note detection

### Phase 5 Extensions (IN DEVELOPMENT)
- 🔄 Reading Intake Pipeline: Literature note workflow automation
- 🔄 Template System Enhancement: Improved reliability and new templates
- 🔄 Import Adapters: CSV/JSON, bookmarks, Twitter, YouTube, RSS

### AI Usage Patterns
```bash
# Core analytics and insights
python3 src/cli/analytics_demo.py . --interactive

# Weekly review automation  
python3 src/cli/workflow_demo.py . --weekly-review

# Enhanced metrics with orphaned/stale detection
python3 src/cli/workflow_demo.py . --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .

# System health check (verify before development)
python3 src/cli/workflow_demo.py . --status

# NEW: Reading Intake Pipeline (once template bug fixed)
# python3 src/cli/workflow_demo.py . --import-bookmarks file.html
# python3 src/cli/workflow_demo.py . --process-literature
```

### AI Ethics & Transparency
- Augment, Don't Replace: AI enhances human creativity
- Explainable Decisions: Every AI action includes rationale
- User Override: Always allow human correction
- Progressive Disclosure: Simple by default, powerful when needed
- Integration Focus: Leverage existing AI workflows rather than duplicating
- Preserve human decision-making in note promotion
- Maintain metadata consistency in automated processes
- Log AI-assisted actions for transparency

## 🔗 Performance Targets
- Summarization: <10s for 1000+ word documents ✅
- Similarity Analysis: <5s per comparison ✅
- Weekly Review: <5s for 100+ notes ✅
- Connection Mapping: <20s for full network analysis ✅
- Enhanced Metrics: <5s for 76+ note analysis ✅
- Reading Intake: <30s per item triage (TARGET)
