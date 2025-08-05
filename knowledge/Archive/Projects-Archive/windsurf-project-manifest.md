---
type: permanent
created: 2025-07-25 20:10
status: active
tags: [project, manifest]
visibility: private
---

# InnerOS Project Manifest (v2)

## Purpose
A single source-of-truth describing the InnerOS Zettelkasten-plus-AI workspace—its philosophy, file conventions, automation stack, and immediate roadmap.

## Guiding Principles
1. **Frictionless capture → insight**: every thought should become a compliant note in <15 s.
2. **Metadata first**: valid YAML drives all automation; pre-commit hooks enforce it.
3. **Incremental AI**: add machine assistance only where it compounds human creativity.
4. **Privacy by default**: all notes default to `visibility: private`; sharing is explicit.
5. **Audit-trail**: never delete knowledge; deprecate or archive with context.

## Directory & Workflow Overview
| Stage | Folder | Key Status Values | Automation |
|-------|--------|------------------|------------|
| Capture | `Inbox/` | `inbox` | Hotkey spawns `Templates/fleeting.md` |
| Triage  | `Fleeting Notes/` | `inbox` → `promoted` | Validator reports promotion candidates |
| Permanent | `Permanent Notes/` | `draft` → `published` | AI tagging, summarisation (Phase-5) |
| Archive | `Archive/` | `archived` | Auto-move via script after 90 d inactivity |

## Current Automation Stack
- **Metadata Validator** (`.automation/scripts/validate_metadata.py`)
- **Link Checker** (`.automation/scripts/link_checker.py`)
- **Changelog Updater** (`.automation/scripts/update_changelog.py`)
- **Pre-commit Hook** (`.automation/hooks/pre_commit`)

## Phase Roadmap
| Phase | Focus | Status |
|-------|-------|--------|
| 1 | YAML standardisation | ✅ Complete |
| 2 | End-to-end workflow validation | ✅ Complete |
| 3 | Git + Changelog discipline | ✅ Complete |
| 4 | Capture friction removal | ✅ Complete |
| 5.1 | AI Tagger - Mock Implementation | ✅ Complete |
| 5.2 | AI Tagger - Real Ollama Integration | ✅ Complete |
| 5.3 | Smart Content Enhancement | ✅ **COMPLETED 2025-07-27** |
| 5.4 | Advanced Analytics & Workflow Management | ✅ **COMPLETED 2025-07-28** |
| 6 | Multi-user & Sharing | 🔜 Next |

## Near-Term Objectives (Q3-2025) - UPDATED
1. ✅ **COMPLETED**: Basic AI auto-tagging (local model) - Real Ollama integration live
2. ✅ **COMPLETED**: Note summarization with LLM (abstractive + extractive)
3. ✅ **COMPLETED**: Semantic similarity search for connection discovery
4. ✅ **COMPLETED**: Advanced analytics dashboard with quality scoring
5. ✅ **COMPLETED**: Smart workflow management with AI-enhanced processing
6. **Phase 6 Next**: Multi-user collaboration and sharing features
7. **Phase 6 Next**: Advanced visualization and network analysis
4. Extend test suite to cover all `.automation/scripts` and reach ≥ 80 % coverage
5. GitHub Actions CI: run validators + tests on every push
6. Weekly review automation: generate report of `status: inbox` & `promoted` notes

## AI Features Stack (Phase 5.2-5.4 Complete)

### Core AI Components
| Component | Purpose | Status | CLI Demo |
|-----------|---------|--------|----------|
| **AI Tagger** | Automatic contextual tagging | ✅ Production | `src/cli/ai_assistant.py` |
| **AI Enhancer** | Content quality assessment & improvement | ✅ Production | `src/cli/enhance_demo.py` |
| **AI Summarizer** | Abstractive & extractive summarization | ✅ Production | `src/cli/summarizer_demo.py` |
| **AI Connections** | Semantic similarity & link discovery | ✅ Production | `src/cli/connections_demo.py` |
| **Note Analytics** | Collection analysis & quality scoring | ✅ Production | `src/cli/analytics_demo.py` |
| **Workflow Manager** | AI-enhanced workflow automation | ✅ Production | `src/cli/workflow_demo.py` |

### AI Capabilities
- **Intelligent Tagging**: Context-aware tag generation using Ollama LLM
- **Quality Assessment**: 0-1 scoring based on content, metadata, links
- **Content Enhancement**: Gap analysis and improvement suggestions
- **Smart Summarization**: Both AI-generated and extractive summaries
- **Connection Discovery**: Semantic similarity using embeddings (cosine similarity)
- **Workflow Automation**: AI-assisted inbox processing and note promotion
- **Analytics Dashboard**: Comprehensive collection insights and recommendations

### Performance & Integration
- **API**: Local Ollama integration (llama3:latest)
- **Caching**: Embedding cache for performance optimization
- **Fallbacks**: Graceful degradation when AI services unavailable
- **Testing**: 66/66 unit tests + integration tests
- **CLI Tools**: Interactive demos for all features
- **Export**: JSON reports for external analysis

### User Experience
- **Interactive Demos**: `demo_user_journeys.py` with realistic scenarios
- **Quick Start**: `quick_demo.py` for immediate feature demonstration
- **Real Data Testing**: `test_real_analytics.py` for actual note collections
- **Batch Processing**: Handle multiple notes efficiently
- **Progress Reporting**: Real-time feedback during operations
- **Rich Formatting**: Color-coded CLI output with clear sections

## Governance
All structural changes (templates, validation rules, hooks) **must** be logged in `Windsurf Project Changelog.md` and linked to a commit. Deprecated docs are moved to `Archive/` with a timestamp suffix.

---
_This manifest supersedes earlier versions (now archived). Update it as the project evolves._
