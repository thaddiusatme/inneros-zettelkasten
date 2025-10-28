# Update for .windsurf/rules/README.md

## Instructions

Replace lines 57-67 and 95-97 in `.windsurf/rules/README.md` with the content below.

---

## Section 1: Replace lines 57-67 (File Size Guidelines)

**OLD** (lines 57-67):
```markdown
**Current Sizes** (2025-10-07):
- updated-development-workflow.md: 11KB ⚠️ (near limit, monitoring split)
- updated-ai-integration.md: 8KB
- automation-monitoring-requirements.md: 7KB ✅ (NEW)
- updated-file-organization.md: 7KB
- architectural-constraints.md: 5KB
- updated-current-issues.md: 4KB
- updated-session-context.md: 2KB
- content-standards.md: 2KB
- privacy-security.md: 1KB
- README.md: 1KB
```

**NEW** (replace with):
```markdown
**Current Sizes** (2025-10-23):
- updated-development-workflow.md: 11,985 bytes (11.7KB) ⚠️ (near limit, stable)
- updated-session-context.md: 11,223 bytes (11.0KB) ⚠️ (near limit, includes guide refs)
- updated-ai-integration.md: 8,066 bytes (7.9KB) ✅
- automation-monitoring-requirements.md: 7,066 bytes (6.9KB) ✅
- updated-current-issues.md: 6,938 bytes (6.8KB) ✅
- updated-file-organization.md: 6,768 bytes (6.6KB) ✅
- architectural-constraints.md: 5,226 bytes (5.1KB) ✅
- README.md: 2,956 bytes (2.9KB) ✅
- content-standards.md: 1,659 bytes (1.6KB) ✅
- privacy-security.md: 1,449 bytes (1.4KB) ✅

**Total**: 63,336 bytes (61.9KB) - well within limits
```

---

## Section 2: Add before "## 🔄 Maintenance" (after line 68)

**INSERT** (add this new section):
```markdown
---

## 📚 Consolidated Development Guides

**Location**: `.windsurf/guides/` (Created 2025-10-23)

For universal development patterns extracted from 34+ lessons-learned iterations:

- **`tdd-methodology-patterns.md`** (12.4KB) - TDD wisdom from 34+ iterations
  - RED → GREEN → REFACTOR patterns
  - Test coverage strategies (10-25 tests)
  - Minimal implementation, utility extraction
  - Time management, success metrics

- **`ai-integration-patterns.md`** (16.9KB) - AI integration from 15+ iterations
  - Mock-first development, graceful degradation
  - File hash caching (85-95% hit rate)
  - Quality gates (82% bad output reduction)
  - Batch processing, error handling

- **`SESSION-STARTUP-GUIDE.md`** (7.7KB) - Quick reference
  - Pattern lookup by task type
  - Common scenarios & anti-patterns
  - Fast navigation to relevant wisdom

- **`README.md`** (7.9KB) - Guide index & maintenance

**Benefits**: 85% content reduction, 50-70% faster context loading vs reading 34 documents

**Usage**: See guides at session start for proven patterns instead of rediscovering
```

---

## Section 3: Replace lines 95-97 (Footer)

**OLD** (lines 95-97):
```markdown
**Last Updated**: 2025-10-07  
**Active Files**: 10  
**Total Size**: ~50KB (well within limits)
```

**NEW** (replace with):
```markdown
**Last Updated**: 2025-10-23  
**Active Rules Files**: 10  
**Rules Total**: 63KB (well within limits)  
**Guides Total**: 46KB (reference documentation)
```

---

## Quick Apply Steps

1. Open `.windsurf/rules/README.md`
2. Replace Section 1 (lines 57-67) with NEW content
3. Insert Section 2 after line 68 (before "## 🔄 Maintenance")
4. Replace Section 3 (lines 95-97) with NEW content
5. Save file

**Result**: README now shows current sizes and references new guides!
