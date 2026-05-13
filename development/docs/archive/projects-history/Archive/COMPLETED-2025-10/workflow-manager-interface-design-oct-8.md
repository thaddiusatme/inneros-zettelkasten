# WorkflowManager Interface Design

**Date**: 2025-10-08 (Wednesday)  
**Purpose**: Week 1 Day 3 - Complete interface design for 4-manager architecture  
**Status**: 🟢 IN PROGRESS - Comprehensive interface specifications

---

## Executive Summary

This document defines the complete interface contracts for splitting WorkflowManager (2,374 LOC, 59 methods) into 4 domain-focused managers plus a utilities class. All design decisions from Tuesday Oct 7 are incorporated.

**Core Principles**:
- **Standardized Results**: All managers return Dict with consistent structure
- **Defensive Validation**: Each manager validates its own inputs
- **Graceful Degradation**: Failures logged, reported, fallback attempted, workflow continues
- **Dry Run Support**: All operations support preview mode
- **Direct References**: Managers communicate via direct method calls (simple, testable)

**LOC Targets**:
- CoreWorkflowManager: 280-320 LOC
- AnalyticsManager: 380-420 LOC
- AIEnhancementManager: 500-600 LOC
- ConnectionManager: 350-450 LOC
- WorkflowUtilities: 40-60 LOC

---

## Table of Contents

1. [CoreWorkflowManager Interface](#1-coreworkflowmanager-interface)
2. [AnalyticsManager Interface](#2-analyticsmanager-interface)
3. [AIEnhancementManager Interface](#3-aienhancementmanager-interface)
4. [ConnectionManager Interface](#4-connectionmanager-interface)
5. [WorkflowUtilities Class](#5-workflowutilities-class)
6. [Critical: process_inbox_note Split Design](#6-critical-process_inbox_note-split-design)
7. [Manager Coordination Patterns](#7-manager-coordination-patterns)
8. [Error Handling Strategy](#8-error-handling-strategy)

---

## 1. CoreWorkflowManager Interface

**Responsibility**: Workflow orchestration, file operations, session management, note lifecycle

**Target**: 280-320 LOC, 12-14 methods (6 public, 6-8 private)

### 1.1 Constructor

```python
class CoreWorkflowManager:
    def __init__(
        self,
        base_directory: Path,
        config: Dict,
        analytics_manager: 'AnalyticsManager',
        ai_enhancement_manager: 'AIEnhancementManager',
        connection_manager: 'ConnectionManager'
    ):
        """Initialize with dependency injection."""
        self.base_dir = Path(base_directory)
        self.config = config
        self.analytics = analytics_manager
        self.ai = ai_enhancement_manager
        self.connections = connection_manager
        self.active_sessions: Dict[str, Dict] = {}
```

### 1.2 Public Methods

**process_inbox_note(note_path, dry_run=False, fast=False) -> Dict**
- Orchestrates quality assessment, AI enhancement, connection discovery
- Returns: `{'success': bool, 'note_path': str, 'analytics': {}, 'ai_enhancement': {}, 'connections': [], 'errors': [], 'warnings': []}`
- Validates note exists, coordinates manager calls, merges results

**promote_note(note_path, target_type=None) -> Dict**
- Promotes note from inbox/fleeting to permanent/literature
- Coordinates AI assessment, directory move, metadata update
- Returns: `{'success': bool, 'original_type': str, 'new_path': str, 'quality_assessment': {}}`

**batch_process_inbox(limit=None, fast=False) -> Dict**
- Processes multiple inbox notes with progress reporting
- Returns: `{'success': bool, 'total_processed': int, 'successful': int, 'results': []}`

**safe_batch_process_inbox(limit=None) -> Dict**
- Image-safe batch processing using ConcurrentSessionManager
- Returns: batch results + `{'session_id': str, 'session_committed': bool}`

**start_safe_processing_session(operation_name) -> str**
- Creates atomic session for transactional batch operations
- Returns: session_id

**commit_safe_processing_session(session_id) -> bool**
- Commits or rolls back session
- Returns: True if committed, False if rolled back

---

## 2. AnalyticsManager Interface

**Responsibility**: Quality assessment, metrics, reporting (NO AI dependencies)

**Target**: 380-420 LOC, 26 methods (8 public, 18 private)

### 2.1 Constructor

```python
class AnalyticsManager:
    def __init__(
        self,
        base_directory: Path,
        config: Dict
    ):
        """Initialize with vault access only."""
        self.base_dir = Path(base_directory)
        self.config = config
        self.quality_thresholds = config.get('quality_thresholds', {})
```

### 2.2 Public Methods

**assess_quality(note_path, dry_run=False) -> Dict** ⭐ NEW
- Assesses note quality from structure, metadata, links
- Returns: `{'success': bool, 'quality_score': float, 'word_count': int, 'recommendations': []}`
- For process_inbox_note split - provides metrics to Core

**generate_workflow_report() -> Dict**
- Comprehensive workflow health report
- Returns: `{'total_notes': int, 'notes_by_type': {}, 'ai_adoption': {}, 'quality_distribution': {}}`

**scan_review_candidates() -> List[Dict]**
- Identifies notes needing review
- Returns: `[{'path': str, 'reason': str, 'quality_score': float}, ...]`

**generate_weekly_recommendations(candidates, dry_run=False) -> Dict**
- Generates prioritized recommendations from candidates
- Returns: `{'high_priority': [], 'medium_priority': [], 'low_priority': []}`

**detect_orphaned_notes() -> List[Dict]**
- Finds notes with no incoming/outgoing links
- Returns: `[{'path': str, 'incoming_links': 0, 'outgoing_links': 0}, ...]`

**detect_stale_notes(days_threshold=90) -> List[Dict]**
- Finds notes not modified within threshold
- Returns: `[{'path': str, 'days_since_modified': int}, ...]`

**generate_enhanced_metrics() -> Dict**
- Comprehensive metrics dashboard
- Returns: `{'orphaned_notes': [], 'stale_notes': [], 'link_density': float, 'productivity_metrics': {}}`

**analyze_fleeting_notes() -> Dict**
- Analyzes fleeting collection for triage
- Returns: `{'total_fleeting': int, 'promotion_ready': [], 'needs_attention': [], 'health_score': float}`

---

## 3. AIEnhancementManager Interface

**Responsibility**: AI enhancement, LLM integration, fallback handling

**Target**: 500-600 LOC, 18-20 methods (8 public, 10-12 private)

### 3.1 Constructor

```python
class AIEnhancementManager:
    def __init__(
        self,
        base_directory: Path,
        config: Dict,
        tagger: 'AITagger',
        enhancer: 'AIEnhancer',
        summarizer: 'AISummarizer'
    ):
        """Initialize with AI components."""
        self.base_dir = Path(base_directory)
        self.config = config
        self.tagger = tagger
        self.enhancer = enhancer
        self.summarizer = summarizer
        self.external_api = self._init_external_api_fallback()
        self.bug_report_dir = Path('.automation/review_queue')
```

### 3.2 Public Methods

**enhance_note(note_path, fast=False, dry_run=False) -> Dict** ⭐ NEW
- AI enhancement with fallback: Local LLM → External API → Degraded
- Returns: `{'success': bool, 'source': str, 'fallback': bool, 'tags': [], 'summary': str, 'quality_score': float}`
- For process_inbox_note split
- On local failure: logs error, creates bug report in `.automation/review_queue/`, tries external API

**assess_promotion_readiness(note_path) -> Dict** ⭐ NEW
- AI assessment for promotion decision
- Returns: `{'ready_for_promotion': bool, 'recommended_type': str, 'confidence': float, 'reasons': []}`
- For promote_fleeting_note split

**process_note_with_ai(note_path, preserve_images=True, dry_run=False) -> Dict**
- Full AI enhancement suite
- Returns: comprehensive AI results

**generate_ai_tags(content, max_tags=8) -> List[str]**
- Generate tags from content
- Returns: List of kebab-case tags

**summarize_content(content, fast=False) -> str**
- Generate summary (1-2 sentences if fast, paragraph if detailed)
- Returns: summary string

**assess_quality(note_data) -> float**
- AI quality score
- Returns: 0.0-1.0

**promote_with_ai(note_path, target_type=None, preview_mode=False) -> Dict**
- AI-enhanced promotion

**batch_promote_with_ai(quality_threshold=0.7, target_type=None) -> Dict**
- Batch promotion with AI filtering

### 3.3 Fallback Strategy (Private)

```python
def _enhance_with_local_llm(note_path, fast) -> Dict:
    """Try local Ollama first."""
    pass

def _enhance_with_external_api(note_path, fast) -> Dict:
    """Fallback to OpenAI/Anthropic."""
    pass

def _report_ai_failure(note_path, error):
    """Create bug report in .automation/review_queue/."""
    bug_file = self.bug_report_dir / f'AI_FAILURE_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    bug_file.write_text(f"""# AI Enhancement Failure

**Date**: {datetime.now().isoformat()}
**Note**: {note_path}
**Error**: {error}
**Action**: Investigate local LLM, fallback used
""")
```

---

## 4. ConnectionManager Interface

**Responsibility**: Link discovery, relationship analysis, orphan remediation

**Target**: 350-450 LOC, 15-18 methods (6 public, 9-12 private)

### 4.1 Constructor

```python
class ConnectionManager:
    def __init__(
        self,
        base_directory: Path,
        config: Dict,
        ai_connections: 'AIConnections'
    ):
        """Initialize with AI connections component."""
        self.base_dir = Path(base_directory)
        self.config = config
        self.ai_connections = ai_connections
```

### 4.2 Public Methods

**discover_links(note_path, dry_run=False) -> List[Dict]** ⭐ NEW
- Semantic link discovery for process_inbox_note split
- Returns: `[{'target': str, 'score': float, 'reason': str}, ...]`

**discover_connections(note_path) -> List[Dict]**
- Full connection discovery

**remediate_orphaned_notes(scope, target_note=None, dry_run=True) -> Dict**
- Fix orphaned notes with bidirectional links
- Returns: `{'success': bool, 'orphans_fixed': int, 'links_inserted': int}`

**build_link_graph() -> Dict[str, set]**
- Construct bidirectional link graph
- Returns: `{'note1.md': {'linked1.md', 'linked2.md'}, ...}`

**insert_bidirectional_links(orphan_path, target_path, dry_run=True) -> Dict**
- Insert links between orphan and target
- Returns: `{'success': bool, 'links_inserted': []}`

**validate_connections(note_path) -> Dict**
- Validate link integrity
- Returns: `{'valid': bool, 'broken_links': [], 'suggestions': []}`

---

## 5. WorkflowUtilities Class

**Responsibility**: Pure utility functions (NO workflow knowledge)

**Target**: 40-60 LOC, MAX 10 methods

### 5.1 Static Utility Methods

```python
class WorkflowUtilities:
    """Static utility methods extracted from managers."""
    
    @staticmethod
    def merge_tags(existing_tags: List[str], new_tags: List[str], max_tags: int) -> List[str]:
        """Merge tag lists intelligently."""
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()
        merged = sorted(list(existing_set | new_set))
        return merged[:max_tags]
    
    @staticmethod
    def load_notes_corpus(directory: Path) -> Dict[str, str]:
        """Load all notes from directory into corpus."""
        corpus = {}
        if not directory.exists():
            return corpus
        for md_file in directory.glob("*.md"):
            try:
                corpus[md_file.name] = md_file.read_text(encoding='utf-8')
            except Exception:
                continue
        return corpus
    
    @staticmethod
    def read_text(path: Path) -> str:
        """Read file with encoding handling."""
        return path.read_text(encoding='utf-8')
    
    @staticmethod
    def write_text(path: Path, text: str) -> None:
        """Write file with encoding handling."""
        path.write_text(text, encoding='utf-8')
    
    @staticmethod
    def backup_file(path: Path) -> Optional[Path]:
        """Create timestamped backup of file."""
        if not path.exists():
            return None
        backup_path = path.with_suffix(f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.bak')
        backup_path.write_text(path.read_text())
        return backup_path
```

**Hard Limit**: Max 10 methods to prevent utility god class

---

## 6. Critical: process_inbox_note Split Design

**Current Monolithic**: 268 LOC (lines 133-400 in workflow_manager.py)

**New Distributed Architecture**:

### 6.1 Core Orchestration (~50 LOC)

```python
def process_inbox_note(self, note_path, dry_run=False, fast=False) -> Dict:
    """Orchestrate across all managers."""
    results = {
        'success': True,
        'note_path': str(note_path),
        'analytics': {},
        'ai_enhancement': {},
        'connections': [],
        'errors': [],
        'warnings': [],
        'dry_run': dry_run
    }
    
    start_time = time.time()
    
    # 1. Analytics assessment (read-only, always safe)
    try:
        results['analytics'] = self.analytics.assess_quality(note_path, dry_run=dry_run)
    except Exception as e:
        results['errors'].append({'stage': 'analytics', 'error': str(e)})
        results['success'] = False
    
    # 2. AI enhancement (may fall back to external API)
    try:
        results['ai_enhancement'] = self.ai.enhance_note(note_path, fast=fast, dry_run=dry_run)
        if results['ai_enhancement'].get('fallback'):
            results['warnings'].append('Used external API fallback (costs incurred)')
    except Exception as e:
        results['errors'].append({'stage': 'ai_enhancement', 'error': str(e)})
        # Don't fail workflow - AI is enhancement, not requirement
    
    # 3. Connection discovery
    try:
        results['connections'] = self.connections.discover_links(note_path, dry_run=dry_run)
    except Exception as e:
        results['errors'].append({'stage': 'connections', 'error': str(e)})
    
    # 4. Merge and save (if not dry_run)
    if not dry_run and results['success']:
        self._save_note_with_enhancements(note_path, results)
    
    results['processing_time'] = time.time() - start_time
    return results
```

### 6.2 Analytics.assess_quality (~60 LOC)

```python
def assess_quality(self, note_path, dry_run=False) -> Dict:
    """Calculate quality metrics from structure and metadata."""
    note_file = Path(note_path)
    
    # Validate input
    if not note_file.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")
    
    # Parse note
    content = note_file.read_text(encoding='utf-8')
    frontmatter, body = parse_frontmatter(content)
    
    # Calculate metrics
    word_count = len(body.split())
    tag_count = len(frontmatter.get('tags', []))
    link_count = len(re.findall(r'\[\[([^\]]+)\]\]', body))
    
    # Calculate quality score
    quality_score = self._calculate_quality_score({
        'word_count': word_count,
        'tag_count': tag_count,
        'link_count': link_count,
        'has_frontmatter': bool(frontmatter),
        'metadata_completeness': self._calculate_metadata_completeness(frontmatter)
    })
    
    # Generate recommendations
    recommendations = self._generate_quality_recommendations(quality_score, word_count, tag_count, link_count)
    
    return {
        'success': True,
        'quality_score': quality_score,
        'quality_level': self._get_quality_level(quality_score),
        'word_count': word_count,
        'tag_count': tag_count,
        'link_count': link_count,
        'has_frontmatter': bool(frontmatter),
        'metadata_completeness': self._calculate_metadata_completeness(frontmatter),
        'recommendations': recommendations
    }
```

### 6.3 AI.enhance_note (~100 LOC)

```python
def enhance_note(self, note_path, fast=False, dry_run=False) -> Dict:
    """Enhance with AI tagging and summarization + fallback."""
    try:
        # Try local LLM first
        result = self._enhance_with_local_llm(note_path, fast)
        return {
            'success': True,
            'source': 'local_ollama',
            'fallback': False,
            'tags': result['tags'],
            'summary': result['summary'],
            'quality_score': result['quality_score'],
            'content_gaps': result.get('content_gaps', [])
        }
    except Exception as local_error:
        # Log error
        logger.error(f"Local LLM failed for {note_path}: {local_error}")
        
        # Create bug report
        self._report_ai_failure(note_path, local_error)
        
        # Try external API fallback
        try:
            result = self._enhance_with_external_api(note_path, fast)
            logger.warning(f"Used external API fallback for {note_path}")
            return {
                'success': True,
                'source': 'external_api',
                'fallback': True,
                'tags': result['tags'],
                'summary': result['summary'],
                'quality_score': result['quality_score']
            }
        except Exception as external_error:
            # Both failed - return degraded result
            logger.critical(f"All AI enhancement failed for {note_path}")
            return {
                'success': False,
                'source': 'none',
                'fallback': False,
                'errors': [str(local_error), str(external_error)],
                'tags': [],          # Empty but valid
                'summary': '',
                'quality_score': 0.5  # Neutral
            }
```

### 6.4 Connections.discover_links (~50 LOC)

```python
def discover_links(self, note_path, dry_run=False) -> List[Dict]:
    """Discover semantic connections using AI."""
    note_file = Path(note_path)
    
    # Validate
    if not note_file.exists():
        raise FileNotFoundError(f"Note not found: {note_path}")
    
    # Get note content
    content = note_file.read_text(encoding='utf-8')
    
    # Use AI connections for semantic similarity
    try:
        connections = self.ai_connections.find_similar_notes(
            note_path=str(note_file),
            content=content,
            top_k=5
        )
        
        return [
            {
                'target': conn['note_path'],
                'score': conn['similarity'],
                'reason': conn.get('reason', 'Semantic similarity')
            }
            for conn in connections
        ]
    except Exception as e:
        logger.error(f"Connection discovery failed for {note_path}: {e}")
        return []  # Return empty list, don't fail workflow
```

### 6.5 LOC Distribution Summary

| Component | LOC | Responsibility |
|-----------|-----|----------------|
| Core orchestration | ~50 | Coordinate managers, merge results |
| Analytics.assess_quality | ~60 | Quality metrics calculation |
| AI.enhance_note | ~100 | AI tagging + summarization + fallback |
| Connections.discover_links | ~50 | Semantic link discovery |
| **Total Distributed** | **~260** | **vs. 268 monolithic** |

**Benefits**:
- ✅ Each piece <100 LOC (testable)
- ✅ Clear separation of concerns
- ✅ Independent testing possible
- ✅ Failures isolated (AI fails ≠ workflow fails)
- ✅ Graceful degradation built-in

---

## 7. Manager Coordination Patterns

### 7.1 Direct Reference Pattern

**Chosen Approach**: Direct references via dependency injection

```python
# Core calls managers directly
analytics_result = self.analytics.assess_quality(note_path)
ai_result = self.ai.enhance_note(note_path, fast=fast)
connections = self.connections.discover_links(note_path)
```

**Rationale**:
- ✅ Simple and straightforward
- ✅ Easy to test with mocks
- ✅ Clear ownership (Core orchestrates)
- ✅ Can refactor to interfaces in Week 3 if needed

**Alternative Considered**: Interface-based (IAnalytics, IAIEnhancement, etc.)
- More complex, not needed for initial implementation
- Can add later if multiple implementations emerge

### 7.2 Error Propagation Strategy

**Pattern**: Managers raise exceptions, Core catches and handles

```python
try:
    result = self.analytics.assess_quality(note_path)
except ValueError as e:
    # Input validation failure
    results['errors'].append({'stage': 'analytics', 'type': 'validation', 'error': str(e)})
    results['success'] = False
except FileNotFoundError as e:
    # File doesn't exist
    results['errors'].append({'stage': 'analytics', 'type': 'file_not_found', 'error': str(e)})
    results['success'] = False
except Exception as e:
    # Unexpected error
    results['errors'].append({'stage': 'analytics', 'type': 'unknown', 'error': str(e)})
    # Log for investigation
    logger.error(f"Unexpected analytics error: {e}", exc_info=True)
```

**Benefits**:
- Specific exception types enable targeted handling
- Core decides whether to continue or abort
- AI failures don't block workflow (enhancement, not requirement)
- All errors logged and returned to caller

---

## 8. Error Handling Strategy

### 8.1 Standardized Error Structure

```python
{
    'stage': str,           # 'analytics', 'ai_enhancement', 'connections', 'core'
    'type': str,            # 'validation', 'file_not_found', 'api_failure', 'unknown'
    'error': str,           # Error message
    'timestamp': str,       # ISO format
    'note_path': str        # Affected note
}
```

### 8.2 AI Failure Handling (Detailed)

**3-Tier Fallback**:

1. **Local LLM (Ollama)**
   - Primary AI source
   - Fast, free, private
   - May fail if service down

2. **External API (OpenAI/Anthropic)**
   - Fallback on local failure
   - Log warning (costs incurred)
   - Create bug report for investigation

3. **Degraded Result**
   - Both failed
   - Return empty but valid response
   - Workflow continues without AI enhancement

**Bug Report Format**:
```markdown
# AI Enhancement Failure

**Date**: 2025-10-08T14:23:45
**Note**: Inbox/my-note.md
**Error**: ConnectionError: Could not connect to Ollama service

**Local LLM Error**: Connection refused on localhost:11434
**External API Used**: Yes (OpenAI GPT-4)
**Cost Estimate**: $0.03

**Action Required**:
- [ ] Investigate Ollama service health
- [ ] Check if service is running: `systemctl status ollama`
- [ ] Review Ollama logs: `journalctl -u ollama`

**Impact**: Note processed successfully using fallback, but costs incurred
```

### 8.3 Validation Errors

**Pattern**: Fail fast with clear messages

```python
# In AnalyticsManager.assess_quality
if not note_path:
    raise ValueError("note_path cannot be empty")

note_file = Path(note_path)
if not note_file.exists():
    raise FileNotFoundError(f"Note not found: {note_path}")

if not note_file.suffix == '.md':
    raise ValueError(f"Only markdown files supported, got: {note_file.suffix}")
```

**Benefits**:
- Clear error messages for users
- Early detection of invalid inputs
- Each manager validates its own inputs (defensive programming)

---

## Summary & Next Steps

### Interfaces Defined

- ✅ **CoreWorkflowManager**: 6 public methods, orchestration + file operations
- ✅ **AnalyticsManager**: 8 public methods, pure metrics (no AI)
- ✅ **AIEnhancementManager**: 8 public methods, AI with fallback + bug reporting
- ✅ **ConnectionManager**: 6 public methods, link discovery + remediation
- ✅ **WorkflowUtilities**: 5 static methods, pure utilities (max 10)

### Critical Designs Complete

- ✅ **process_inbox_note split**: 268 LOC → 4 focused methods (~260 LOC distributed)
- ✅ **Manager coordination**: Direct references via dependency injection
- ✅ **Error handling**: 3-tier fallback for AI, graceful degradation, bug reporting
- ✅ **Return formats**: Standardized Dict structure across all managers

### Ready For

**Thursday Oct 9**: Dependency mapping and detailed coordination contracts  
**Friday Oct 10**: RED Phase - Write 30 failing tests for new architecture

---

**Status**: 🟢 **INTERFACE DESIGN COMPLETE**  
**Next**: Dependency mapping (Thursday)  
**Branch**: feat/workflow-manager-refactor-week-1
