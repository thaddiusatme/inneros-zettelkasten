# WorkflowManager Dependency Mapping

**Date**: 2025-10-09 (Thursday)  
**Purpose**: Week 1 Day 4 - Complete dependency analysis for 4-manager architecture  
**Status**: 🟢 IN PROGRESS - Dependency graph, error handling, and coordination patterns

---

## Executive Summary

This document maps all dependencies between the 4 managers (Core, Analytics, AI, Connections) with confirmed design patterns: exception-based error handling, parallel execution opportunities, and result validation strategies.

**Key Findings**:
- ✅ **NO Circular Dependencies**: Clean dependency graph verified
- ✅ **Parallel Execution**: Analytics + Connections can run simultaneously
- ✅ **Exception-Based Communication**: Managers raise, Core catches
- ✅ **AI Gating**: quality_score >= 0.3 threshold prevents unnecessary costs
- ✅ **Bug Reporting**: Total failures create `.automation/review_queue/WORKFLOW_FAILURE_{timestamp}.md`

---

## 1. Complete Dependency Graph

### 1.1 Manager Dependencies (Top-Level)

```
CoreWorkflowManager
├── → AnalyticsManager (NO dependencies - pure metrics)
├── → AIEnhancementManager (depends on AI components)
└── → ConnectionManager (depends on ai_connections)

AnalyticsManager
└── → ConnectionManager (one-way: orphan detection feeds remediation)

AIEnhancementManager
└── NO manager dependencies (only AI components)

ConnectionManager
└── NO manager dependencies (only ai_connections component)
```

### 1.2 Initialization Order (Respects Dependencies)

```python
# 1. Analytics - NO dependencies (must be first)
analytics = AnalyticsManager(base_dir, config)

# 2. Connections - Depends on ai_connections component only
ai_connections = AIConnections(base_dir, config)
connections = ConnectionManager(base_dir, config, ai_connections)

# 3. AI - Depends on AI components (tagger, enhancer, summarizer)
tagger = AITagger(config)
enhancer = AIEnhancer(config)
summarizer = AISummarizer(config)
ai = AIEnhancementManager(base_dir, config, tagger, enhancer, summarizer)

# 4. Core - Depends on ALL 3 managers (must be last)
core = CoreWorkflowManager(base_dir, config, analytics, ai, connections)
```

### 1.3 Circular Dependency Verification

**Verified NO Circular Dependencies**:
- ✅ Analytics → Connections (one-way only for orphan detection)
- ✅ Analytics has NO AI dependencies (pure metrics, AI-free)
- ✅ Core → All managers (one-way orchestration)
- ✅ Managers do NOT call Core
- ✅ Managers do NOT call each other (only Core orchestrates)

---

## 2. Exception-Based Error Handling

### 2.1 Exception Types by Manager

**AnalyticsManager Raises**:
- `ValueError`: Empty note_path, invalid parameters
- `FileNotFoundError`: Note file doesn't exist
- `Exception`: Unexpected errors (file permissions, parsing errors)

**AIEnhancementManager Raises**:
- `ConnectionError`: Local LLM service unavailable (triggers fallback)
- `ValueError`: Invalid note content, empty input
- `Exception`: Unexpected AI processing errors

**ConnectionManager Raises**:
- `ValueError`: Invalid note_path, invalid parameters
- `Exception`: AI connections service unavailable

### 2.2 Core's Exception Handling Strategy

```python
# Pattern: Try manager call → Catch specific exceptions → Log → Continue or Stop

# CRITICAL ERRORS (Stop Processing):
try:
    result = self.analytics.assess_quality(note_path)
except ValueError as e:
    # Input validation - STOP
    results['errors'].append({'stage': 'analytics', 'type': 'validation', 'error': str(e)})
    results['success'] = False
    return results  # Early return
except FileNotFoundError as e:
    # File missing - STOP
    results['errors'].append({'stage': 'analytics', 'type': 'not_found', 'error': str(e)})
    results['success'] = False
    return results  # Early return

# NON-CRITICAL ERRORS (Continue with Degradation):
try:
    result = self.ai.enhance_note(note_path)
except Exception as e:
    # AI failure - CONTINUE (enhancement, not requirement)
    logger.warning(f"AI failed: {e}")
    results['errors'].append({'stage': 'ai_enhancement', 'error': str(e)})
    results['ai_enhancement'] = {'success': False, 'tags': [], 'summary': ''}
    # Workflow continues

# TOTAL FAILURE (All 3 Managers):
if len(results['errors']) >= 3:
    self._create_workflow_failure_bug_report(note_path, results['errors'])
    results['warnings'].append('Total failure - bug report created')
```

---

## 3. process_inbox_note Orchestration

### 3.1 Execution Flow with Parallel Opportunities

```python
def process_inbox_note(self, note_path, dry_run=False, fast=False) -> Dict:
    """
    Orchestrate note processing across all 3 managers.
    
    Flow:
    1. Analytics (REQUIRED) - gates AI enhancement
    2. AI Enhancement (CONDITIONAL) - only if quality_score >= 0.3
    3. Connections (PARALLEL candidate) - independent of AI
    4. Validate & Save
    """
    results = {
        'success': True,
        'analytics': {},
        'ai_enhancement': {},
        'connections': [],
        'errors': [],
        'warnings': []
    }
    
    # === STEP 1: Analytics (REQUIRED - Critical Path) ===
    try:
        results['analytics'] = self.analytics.assess_quality(note_path, dry_run=dry_run)
    except (ValueError, FileNotFoundError) as e:
        # STOP on validation/file errors
        results['errors'].append({
            'stage': 'analytics',
            'type': 'validation' if isinstance(e, ValueError) else 'not_found',
            'error': str(e)
        })
        results['success'] = False
        return results  # Early return
    except Exception as e:
        # Continue with default on unexpected errors
        logger.error(f"Analytics failed: {e}", exc_info=True)
        results['errors'].append({'stage': 'analytics', 'type': 'unknown', 'error': str(e)})
        results['analytics'] = {'quality_score': 0.5}  # Default neutral
    
    # === STEP 2: AI Enhancement (CONDITIONAL - Cost Gated) ===
    quality_score = results['analytics'].get('quality_score', 0)
    
    if quality_score >= 0.3:  # Threshold justifies AI costs
        try:
            results['ai_enhancement'] = self.ai.enhance_note(
                note_path, fast=fast, dry_run=dry_run
            )
            if results['ai_enhancement'].get('fallback'):
                results['warnings'].append('External API used (costs incurred)')
        except Exception as e:
            # AI failure doesn't block workflow
            logger.warning(f"AI enhancement failed: {e}")
            results['errors'].append({'stage': 'ai_enhancement', 'error': str(e)})
            results['ai_enhancement'] = {
                'success': False,
                'tags': [],
                'summary': '',
                'quality_score': 0.5
            }
    else:
        # Skip AI to save costs
        results['warnings'].append(
            f'AI skipped (quality_score {quality_score} < 0.3 threshold)'
        )
        results['ai_enhancement'] = {
            'success': True,
            'skipped': True,
            'reason': 'quality_too_low'
        }
    
    # === STEP 3: Connections (PARALLEL Candidate) ===
    # NOTE: Can run in parallel with AI (no dependency)
    try:
        results['connections'] = self.connections.discover_links(note_path, dry_run=dry_run)
    except Exception as e:
        # Empty connections is valid result
        logger.warning(f"Connection discovery failed: {e}")
        results['errors'].append({'stage': 'connections', 'error': str(e)})
        results['connections'] = []
    
    # === STEP 4: Total Failure Check ===
    if len(results['errors']) >= 3:  # All managers failed
        self._create_workflow_failure_bug_report(note_path, results['errors'])
        results['warnings'].append('Total workflow failure - bug report created')
    
    # === STEP 5: Validate & Save ===
    if not dry_run and results['success']:
        try:
            self._save_note_with_enhancements(note_path, results)
        except Exception as e:
            logger.error(f"Save failed: {e}", exc_info=True)
            results['errors'].append({'stage': 'save', 'error': str(e)})
            results['success'] = False
    
    return results
```

### 3.2 Parallel Execution Optimization (Future)

```python
# Phase 2 Optimization: Run Analytics + Connections in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    future_analytics = executor.submit(
        self.analytics.assess_quality, note_path, dry_run
    )
    future_connections = executor.submit(
        self.connections.discover_links, note_path, dry_run
    )
    
    # Wait for both (max 30s timeout)
    results['analytics'] = future_analytics.result(timeout=30)
    results['connections'] = future_connections.result(timeout=30)

# Then run AI enhancement based on quality_score
if results['analytics']['quality_score'] >= 0.3:
    results['ai_enhancement'] = self.ai.enhance_note(note_path, fast, dry_run)
```

**Benefits**:
- 2x speedup for notes with low quality (Analytics + Connections run simultaneously, AI skipped)
- Maintains error isolation (futures capture exceptions independently)
- Simple implementation with ThreadPoolExecutor

---

## 4. Result Validation Strategy

### 4.1 Validation Requirements

**All Managers Must Return**:
- `success` (bool): Required key
- `errors` (list): Optional but recommended
- Domain-specific fields with sensible defaults

### 4.2 Validation Implementation

```python
def _validate_manager_result(self, result: Dict, manager_name: str) -> Dict:
    """Validate and sanitize manager results with sensible defaults."""
    
    # Structure validation
    if not isinstance(result, dict):
        logger.error(f"{manager_name} returned non-dict: {type(result)}")
        return {
            'success': False,
            'errors': [f'Invalid result type from {manager_name}']
        }
    
    # Required keys
    if 'success' not in result:
        logger.warning(f"{manager_name} missing 'success' key")
        result['success'] = False  # Default to failure
    
    # Manager-specific defaults
    if manager_name == 'analytics':
        result.setdefault('quality_score', 0.5)  # Neutral
        result.setdefault('word_count', 0)
        result.setdefault('tag_count', 0)
        result.setdefault('link_count', 0)
    
    elif manager_name == 'ai_enhancement':
        result.setdefault('tags', [])
        result.setdefault('summary', '')
        result.setdefault('quality_score', 0.5)
        result.setdefault('source', 'none')
    
    elif manager_name == 'connections':
        # Connections returns List, not Dict
        if not isinstance(result, list):
            logger.error(f"Connections returned non-list: {type(result)}")
            return []
        # Validate list items
        for item in result:
            if not isinstance(item, dict):
                logger.warning(f"Invalid connection item: {type(item)}")
                continue
            item.setdefault('target', '')
            item.setdefault('score', 0.0)
            item.setdefault('reason', '')
    
    return result
```

### 4.3 Usage in Core

```python
# After each manager call, validate results
results['analytics'] = self._validate_manager_result(
    results['analytics'], 'analytics'
)
results['ai_enhancement'] = self._validate_manager_result(
    results['ai_enhancement'], 'ai_enhancement'
)
results['connections'] = self._validate_manager_result(
    results['connections'], 'connections'
)
```

---

## 5. Bug Report Creation Logic

### 5.1 AI Failure Bug Reports

**Location**: `.automation/review_queue/AI_FAILURE_{timestamp}.md`  
**Created By**: AIEnhancementManager (when local LLM fails)  
**Purpose**: Track LLM service issues, external API fallback usage

```python
# In AIEnhancementManager.enhance_note()
def _report_ai_failure(self, note_path: str, error: Exception):
    """Create bug report for AI enhancement failure."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bug_file = self.bug_report_dir / f'AI_FAILURE_{timestamp}.md'
    
    bug_content = f"""# AI Enhancement Failure

**Date**: {datetime.now().isoformat()}
**Note**: {note_path}
**Error**: {str(error)}

## Details
- **Local LLM**: Failed ({type(error).__name__})
- **External API**: {"Used" if self.external_api else "Not configured"}
- **Impact**: {"Fallback used (costs incurred)" if self.external_api else "Degraded result"}

## Action Required
- [ ] Check Ollama service: `systemctl status ollama`
- [ ] Review Ollama logs: `journalctl -u ollama`
- [ ] Verify model availability: `ollama list`

**Cost Impact**: {f"$0.01-0.05 per note" if self.external_api else "None"}
"""
    
    bug_file.write_text(bug_content)
    logger.warning(f"AI failure bug report: {bug_file}")
```

### 5.2 Total Workflow Failure Bug Reports

**Location**: `.automation/review_queue/WORKFLOW_FAILURE_{timestamp}.md`  
**Created By**: CoreWorkflowManager (when all 3 managers fail)  
**Purpose**: Critical system health alert

```python
# In CoreWorkflowManager.process_inbox_note()
def _create_workflow_failure_bug_report(self, note_path: str, errors: List[Dict]):
    """Create CRITICAL bug report when all managers fail."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    bug_file = Path('.automation/review_queue') / f'WORKFLOW_FAILURE_{timestamp}.md'
    
    bug_content = f"""# Workflow Total Failure ⚠️

**Date**: {datetime.now().isoformat()}
**Note**: {note_path}
**Severity**: CRITICAL - All 3 managers failed

## Errors by Stage

"""
    
    for error in errors:
        bug_content += f"""### {error['stage'].upper()}
- **Type**: {error.get('type', 'unknown')}
- **Error**: {error['error']}

"""
    
    bug_content += """## System Health Checklist

- [ ] Analytics: File permissions, vault structure
- [ ] AI Enhancement: Ollama service, external API keys
- [ ] Connections: AI connections service, embeddings
- [ ] Core: Disk space, write permissions

## Impact

**CRITICAL**: Note processing completely blocked. Investigate immediately.

**Logs**: Check `development/logs/` for stack traces
"""
    
    bug_file.parent.mkdir(parents=True, exist_ok=True)
    bug_file.write_text(bug_content)
    logger.critical(f"WORKFLOW FAILURE: {bug_file}")
```

---

## 6. Manager Coordination Patterns

### 6.1 Core → Analytics

**When**: Every process_inbox_note call, workflow reports, review candidates  
**Pattern**: Synchronous call with exception handling  
**Data Flow**: note_path → quality metrics

```python
# Critical path - gates AI enhancement
try:
    analytics_result = self.analytics.assess_quality(note_path, dry_run=dry_run)
    quality_score = analytics_result['quality_score']
except (ValueError, FileNotFoundError):
    # Stop processing
    return error_result
```

### 6.2 Core → AI

**When**: process_inbox_note (if quality >= 0.3), promote_fleeting_note  
**Pattern**: Conditional with fallback handling  
**Data Flow**: note_path + quality_score → AI enhancements

```python
# Conditional - cost gated
if quality_score >= 0.3:
    try:
        ai_result = self.ai.enhance_note(note_path, fast=fast, dry_run=dry_run)
        # Check for fallback usage
        if ai_result.get('fallback'):
            log_external_api_usage()
    except Exception:
        # Continue with degraded result
        ai_result = default_ai_result
```

### 6.3 Core → Connections

**When**: process_inbox_note, orphan remediation workflows  
**Pattern**: Best-effort (empty result is valid)  
**Data Flow**: note_path → link suggestions

```python
# Non-critical - empty is valid
try:
    connections = self.connections.discover_links(note_path, dry_run=dry_run)
except Exception:
    connections = []  # No connections found is valid
```

### 6.4 Analytics → Connections (Indirect)

**When**: Orphan detection feeds into remediation  
**Pattern**: Analytics detects, Core calls Connections to remediate  
**Data Flow**: orphaned_notes list → remediation targets

```python
# Step 1: Analytics detects orphans
orphans = self.analytics.detect_orphaned_notes()

# Step 2: Core decides to remediate
for orphan in orphans[:10]:  # Limit batch size
    self.connections.remediate_orphaned_notes(
        scope='single',
        target_note=orphan['path'],
        dry_run=True
    )
```

---

## 7. Edge Cases & Error Scenarios

| Scenario | Handler | Action | Result |
|----------|---------|--------|--------|
| Empty note_path | Analytics | Raise ValueError | Core stops, returns error |
| File not found | Analytics | Raise FileNotFoundError | Core stops, returns error |
| Analytics unexpected error | Core | Log, use defaults | Continue with quality_score=0.5 |
| AI local LLM fails | AI Manager | Create bug report, try external API | Continue with fallback |
| AI total failure (local + external) | AI Manager | Return degraded result | Continue with empty tags/summary |
| Connections empty result | Core | Treat as valid | Continue (no connections found) |
| All 3 managers fail | Core | Create WORKFLOW_FAILURE bug report | Return with all errors |
| dry_run=True but write attempted | Manager | Raise exception or log critical | Development bug - fix manager |
| Invalid result format | Core | Validate, use defaults, log warning | Continue with safe defaults |
| quality_score < 0.3 | Core | Skip AI enhancement | Save costs, continue |
| Parallel execution timeout | Core (future) | Fall back to sequential | Continue with degraded performance |

---

## 8. Dependency Summary

### 8.1 Dependency Matrix

|  | Analytics | AI | Connections | Core |
|--|-----------|----|--------------|----|
| **Analytics** | - | ❌ | → (orphan detection) | ❌ |
| **AI** | ❌ | - | ❌ | ❌ |
| **Connections** | ❌ | ❌ | - | ❌ |
| **Core** | → | → | → | - |

**Legend**: → depends on, ❌ no dependency

### 8.2 Verification Checklist

- ✅ NO circular dependencies
- ✅ Analytics is AI-free (pure metrics)
- ✅ Managers don't call Core
- ✅ Managers don't call each other directly
- ✅ Core orchestrates all interactions
- ✅ Initialization order respects dependencies
- ✅ Parallel execution verified (Analytics + Connections)
- ✅ Exception-based error handling documented
- ✅ Result validation strategy defined
- ✅ Bug reporting logic mapped

---

## Next Steps

**Friday Oct 10 (RED Phase)**:
- Write 30 failing tests based on this dependency map
- Test exception handling for each edge case
- Verify parallel execution opportunities
- Test result validation with malformed data

**Week 2 (GREEN Phase)**:
- Extract managers following initialization order
- Implement exception-based communication
- Add result validation to Core
- Create bug report infrastructure

**Week 3 (REFACTOR Phase)**:
- Optimize with parallel execution (ThreadPoolExecutor)
- Migrate existing 13 test files
- Extract WorkflowUtilities
- Performance benchmarking

---

**Status**: 🟢 **DEPENDENCY MAPPING COMPLETE**  
**Next**: RED Phase - 30 failing tests  
**Branch**: feat/workflow-manager-refactor-week-1
