# Windsurf Rules - InnerOS Zettelkasten

> **Purpose**: Modular AI assistant behavior guidelines  
> **Updated**: 2025-10-07 (Added automation/monitoring requirements)  
> **Structure**: 10 focused rule files, each under 12KB limit

---

## 📋 Core Rule Files

### Development & Architecture
- **`updated-development-workflow.md`** - TDD methodology, architectural safeguards, Git standards
- **`architectural-constraints.md`** - God class prevention, size limits, refactoring triggers
- **`automation-monitoring-requirements.md`** ⭐ NEW - Phase 3 & 4 mandatory requirements
  - Event-driven and scheduled automation
  - Monitoring, metrics, health checks, alerting
  - Daemon integration patterns

### Project Organization & Content
- **`updated-file-organization.md`** - Directory structure, metadata schema, templates
- **`content-standards.md`** - Note quality standards, literature notes, permanent notes

### AI Integration & Context
- **`updated-ai-integration.md`** - AI feature guidelines, workflow patterns
- **`updated-session-context.md`** - Project context, current priorities
- **`updated-current-issues.md`** - Active bugs, system integrity issues

### Security & Ethics
- **`privacy-security.md`** - Data preservation, ethics, user decision-making

---

## 🎯 How to Use

**AI Assistant (Cascade)**:
- Automatically loads ALL files in this directory
- Follows guidelines across all files
- Modular structure prevents 12KB limit issues

**Developers**:
- Update individual files as needed
- Keep each file focused and under 12KB
- Archive deprecated files to `.windsurf/archive/`

---

## 📊 File Size Guidelines

- **Target**: <8KB per file (comfortable margin)
- **Warning**: 8-10KB (consider splitting)
- **Limit**: 12KB (hard limit, must split)

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

---

## 🔄 Maintenance

**Monthly Review** (First Monday):
1. Check file sizes (`wc -c .windsurf/rules/*.md`)
2. Identify files approaching 10KB
3. Split or refactor if needed
4. Archive deprecated content

**When Adding New Rules**:
1. Check total character count
2. Keep focused (single responsibility)
3. Update this README
4. Link related files

---

## 🗂️ Archived/Deprecated

Files moved to `.windsurf/archive/rules-backup-YYYY-MM-DD/`:
- `file-organization.md` (2025-10-07) - Superseded by `updated-file-organization.md`
- `updated-windsurfrules-v4-concise.md` (2025-10-07) - Monolithic approach superseded by modular structure

---

**Last Updated**: 2025-10-07  
**Active Files**: 10  
**Total Size**: ~50KB (well within limits)
