# ADR-003: Distribution Repository Architecture

**Date**: 2025-10-09  
**Status**: ✅ ACCEPTED  
**Context**: Distribution & Productionization Manifest  
**Related**: `distribution-productionization-manifest.md`, `adr-001-workflow-manager-refactoring.md`

---

## 📋 Context

InnerOS currently exists as a single repository containing both:
- **Codebase**: Production-ready AI systems with 66+ passing tests
- **Personal Knowledge**: 200+ personal notes, 50K words of private content

We need to separate these concerns to enable public distribution while maintaining development velocity with real test data.

---

## 🎯 Decision

Implement a **Two-Repository Architecture** with automated distribution pipeline:

### **Architecture Pattern: Source-to-Distribution Pipeline**

```
┌─────────────────────────────────────────────┐
│  SOURCE REPO (inneros-zettelkasten)         │
│  - Personal knowledge (private)             │
│  - Real test data (200+ notes)              │
│  - Development playground                   │
│  - Active TDD iterations                    │
└─────────────────────────────────────────────┘
                    ↓
        ┌──────────────────────┐
        │  Distribution Script  │
        │  - Sanitize content   │
        │  - Inject samples     │
        │  - Validate safety    │
        └──────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  DISTRIBUTION REPO (inneros-distribution)   │
│  - All code & tests (public)                │
│  - Sample knowledge only                    │
│  - Clean documentation                      │
│  - Ready for public use                     │
└─────────────────────────────────────────────┘
```

---

## 🏗️ Directory Structure Decisions

### **1. Source Repository (Current)**

**Keep Private**:
```
inneros-zettelkasten/
├── knowledge/                    # ❌ PRIVATE
│   ├── Inbox/                    # Personal notes
│   ├── Fleeting Notes/           # Quick captures
│   ├── Permanent Notes/          # Developed ideas
│   ├── Literature Notes/         # Reading notes
│   ├── Archive/                  # Historical content
│   └── Content Pipeline/         # Work in progress
│
├── Reviews/                      # ❌ PRIVATE (39 weekly reviews)
├── Media/                        # ❌ PRIVATE (screenshots, recordings)
├── backups/                      # ❌ PRIVATE (backup files)
├── .automation/logs/             # ❌ PRIVATE (processing logs)
│
└── development/                  # ✅ PUBLIC (with sanitization)
    ├── src/                      # All code
    ├── tests/                    # All tests
    └── demos/                    # Demo scripts
```

### **2. Distribution Repository (Generated)**

**Public Structure**:
```
inneros-distribution/
├── development/                  # ✅ All code (no changes)
│   ├── src/                      # 12+ AI systems
│   ├── tests/                    # 66+ tests
│   ├── demos/                    # Demo scripts
│   └── requirements.txt          # Dependencies
│
├── knowledge/                    # ⚠️ SANITIZED
│   ├── Templates/                # ✅ All templates
│   ├── Inbox/                    # ✅ Empty + README
│   ├── Fleeting Notes/           # ✅ 1-2 examples + README
│   ├── Permanent Notes/          # ✅ 3-5 examples + README
│   └── Literature Notes/         # ✅ 1-2 examples + README
│
├── Projects/                     # ⚠️ SANITIZED
│   ├── REFERENCE/                # ✅ Core documentation
│   └── COMPLETED-2025-XX/        # ✅ Lessons learned (sanitized)
│
├── .windsurf/                    # ✅ AI rules & workflows
│   ├── rules/                    # Development guidelines
│   └── workflows/                # TDD workflows
│
├── Workflows/                    # ✅ Process docs
├── .gitignore                    # ✅ Distribution version
├── README.md                     # ✅ Distribution marketing
├── INSTALLATION.md               # ✅ Setup guide
├── DISTRIBUTION-NOTES.md         # ✅ What's included/excluded
└── inneros                       # ✅ CLI wrapper
```

---

## 🔒 Security Architecture

### **Safety Guarantees**

**Level 1: Prevention (Automated)**
- `.gitignore-distribution` blocks personal directories
- Distribution script removes personal content by default
- Separate git repositories (no shared history)

**Level 2: Validation (Automated)**
- Pre-distribution security scan
- Pattern matching for personal identifiers
- API key detection
- Private path validation

**Level 3: Manual Review (Human)**
- Final review checklist before each release
- Commit history audit
- Sample content verification

### **Distribution .gitignore Strategy**

```gitignore
# PERSONAL KNOWLEDGE - NEVER DISTRIBUTE
knowledge/Inbox/*.md
knowledge/Fleeting Notes/*.md
knowledge/Permanent Notes/*.md
knowledge/Literature Notes/*.md
knowledge/Archive/
knowledge/Content Pipeline/
knowledge/*MOC.md

# PERSONAL ARTIFACTS
Reviews/
Media/
backups/
.automation/logs/
.automation/review_queue/

# KEEP FOR DISTRIBUTION (Explicit allowlist)
!knowledge/Templates/
!knowledge/README-knowledge.md
!knowledge/GETTING-STARTED.md
!knowledge/Inbox/README.md
!knowledge/Fleeting Notes/README.md
!knowledge/Permanent Notes/README.md
!knowledge/Literature Notes/README.md

# SAMPLE CONTENT (Added by script)
!knowledge/Inbox/EXAMPLE-*.md
!knowledge/Fleeting Notes/example-*.md
!knowledge/Permanent Notes/example-*.md
!knowledge/Literature Notes/example-*.md
```

---

## 🔄 Distribution Pipeline

### **Script: `scripts/create-distribution.sh`**

**Phase 1: Clone & Clean**
```bash
#!/bin/bash
# Creates clean distribution from source repository

set -e  # Exit on error

DIST_DIR="../inneros-distribution"
SAMPLE_DIR="knowledge-starter-pack"

echo "🚀 Creating InnerOS Distribution..."

# 1. Clone current repo
git clone . "$DIST_DIR"
cd "$DIST_DIR"

# 2. Remove personal content
echo "🧹 Removing personal content..."
rm -rf knowledge/Inbox/*.md
rm -rf knowledge/Fleeting\ Notes/*.md
rm -rf knowledge/Permanent\ Notes/*.md
rm -rf knowledge/Literature\ Notes/*.md
rm -rf knowledge/Archive
rm -rf knowledge/Content\ Pipeline
rm -rf knowledge/*MOC.md
rm -rf Reviews/
rm -rf Media/
rm -rf backups/
rm -rf .automation/logs/
rm -rf .automation/review_queue/

# 3. Add sample content
echo "📦 Adding sample content..."
cp -r "../$SAMPLE_DIR"/* knowledge/

# 4. Update .gitignore
mv .gitignore-distribution .gitignore

# 5. Run security scan
echo "🔒 Running security scan..."
python3 scripts/security-audit.py

# 6. Validate tests
echo "🧪 Running tests..."
cd development
python3 -m pytest tests/

# 7. Create distribution commit
cd ..
git add .
git commit -m "feat: InnerOS distribution v0.1.0-alpha

- Clean codebase with sample knowledge
- All personal content removed
- 66+ tests passing
- Ready for public use"

echo "✅ Distribution created successfully at $DIST_DIR"
```

**Phase 2: Validation**
```python
#!/usr/bin/env python3
# scripts/security-audit.py

import re
from pathlib import Path

PERSONAL_PATTERNS = [
    r'YourName',  # Personal name
    r'your-github-username',  # GitHub username
    r'personal project',  # Personal references
    r'my vault',  # Personal language
]

SENSITIVE_PATTERNS = [
    r'API_KEY\s*=\s*["\']',
    r'PASSWORD\s*=\s*["\']',
    r'SECRET\s*=\s*["\']',
    r'TOKEN\s*=\s*["\']',
]

def scan_distribution():
    issues = []
    
    for md_file in Path('.').rglob('*.md'):
        content = md_file.read_text()
        
        # Check for personal information
        for pattern in PERSONAL_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"❌ Personal info in {md_file}: {pattern}")
        
        # Check for secrets
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, content):
                issues.append(f"🔒 Potential secret in {md_file}: {pattern}")
    
    if issues:
        print("⚠️  Security Issues Found:")
        for issue in issues:
            print(f"  {issue}")
        exit(1)
    else:
        print("✅ Security scan passed - no issues found")

if __name__ == '__main__':
    scan_distribution()
```

---

## 📦 Sample Knowledge Structure

### **Directory: `knowledge-starter-pack/`**

**Purpose**: Demonstrates InnerOS features without exposing personal content

```
knowledge-starter-pack/
├── Templates/
│   └── (copied from source - no changes)
│
├── Inbox/
│   ├── README.md                 # Explains inbox workflow
│   └── EXAMPLE-quick-capture.md  # Shows quick capture
│
├── Fleeting Notes/
│   ├── README.md                 # Explains fleeting notes
│   ├── example-fleeting-zettelkasten.md
│   └── example-fleeting-note-taking.md
│
├── Permanent Notes/
│   ├── README.md                 # Explains permanent notes
│   ├── example-zettelkasten-method.md
│   ├── example-note-linking.md
│   ├── example-ai-workflows.md
│   └── example-knowledge-management.md
│
└── Literature Notes/
    ├── README.md                 # Explains literature notes
    └── example-youtube-20251009.md
```

**Sample Note Example**:
```markdown
# Example: Zettelkasten Method

**Type**: permanent
**Created**: 2025-10-09 08:00
**Status**: published
**Tags**: #knowledge-management #zettelkasten #note-taking
**Quality Score**: 0.85

## Core Principle

The Zettelkasten method emphasizes **atomic notes** - each note contains
one idea that can stand alone and be linked to other ideas.

## Key Components

1. **Atomic Notes**: Single, focused ideas
2. **Bidirectional Links**: [[example-note-linking]]
3. **Emergent Structure**: Bottom-up organization
4. **Permanent Collection**: Long-term knowledge store

## AI Enhancement

InnerOS extends traditional Zettelkasten with:
- Automatic tagging and quality assessment
- Semantic connection discovery
- Note promotion workflows
- Literature note processing

## References

- Original method by Niklas Luhmann
- Modern adaptation: [[example-knowledge-management]]
- Practical implementation: [[example-ai-workflows]]
```

---

## 🔍 Directory Context Awareness

### **AI Agent Guidelines**

**When working in SOURCE repository**:
```python
# AI agents should recognize context
def get_repository_context():
    """Determine if working in source or distribution."""
    has_personal_content = Path('Reviews/').exists()
    
    if has_personal_content:
        return {
            'repo': 'source',
            'mode': 'development',
            'safety': 'protect_personal_data',
            'test_data': 'use_real_notes'
        }
    else:
        return {
            'repo': 'distribution',
            'mode': 'production',
            'safety': 'public_ready',
            'test_data': 'use_sample_notes'
        }
```

**Context-Aware Operations**:
```python
def process_notes(repo_context):
    """Operations adapt to repository type."""
    
    if repo_context['repo'] == 'source':
        # Use all personal notes for testing
        notes = scan_directory('knowledge/Permanent Notes/')
        
    elif repo_context['repo'] == 'distribution':
        # Use only sample notes
        notes = scan_directory('knowledge/Permanent Notes/example-*.md')
    
    return notes
```

### **.windsurf/rules Directory Context**

Add to `.windsurf/rules/updated-file-organization.md`:

```markdown
## 🏛️ Repository Context Recognition

### Source Repository (inneros-zettelkasten)
**Indicators**:
- `Reviews/` directory exists
- `knowledge/` contains personal content
- `.automation/logs/` has processing history

**AI Agent Behavior**:
- ✅ Access all personal notes for testing
- ✅ Generate real insights from personal data
- ✅ Create backups in `.automation/`
- ❌ Never commit personal content

### Distribution Repository (inneros-distribution)
**Indicators**:
- `DISTRIBUTION-NOTES.md` exists
- `knowledge/` has only example-*.md files
- No `Reviews/` directory

**AI Agent Behavior**:
- ✅ Use sample notes only
- ✅ Generate generic examples
- ✅ Test with synthetic data
- ❌ Never reference personal information
```

---

## 📊 Consequences

### **Benefits** ✅

1. **Privacy Protection**: Personal knowledge never exposed publicly
2. **Development Velocity**: Continue using real data for testing
3. **Public Distribution**: Clean, installable package for users
4. **Automated Process**: Script handles distribution creation
5. **Separate Concerns**: Code updates don't risk personal data exposure

### **Tradeoffs** ⚠️

1. **Maintenance Overhead**: Must maintain two repositories
2. **Sync Complexity**: Code changes need manual sync initially
3. **Testing Gap**: Distribution testing requires separate validation
4. **Documentation Duplication**: Some docs exist in both repos

### **Mitigations** 🛠️

1. **Automation**: Script automates most distribution work
2. **CI/CD**: GitHub Actions can automate sync (Phase 2)
3. **Testing**: Distribution tests run automatically pre-release
4. **Templates**: Shared documentation reduces duplication

---

## 🔄 Migration Path

### **Phase 1: Initial Split** (Week 1)
- Create distribution script
- Build sample knowledge structure
- Test distribution creation locally
- Validate security scanning

### **Phase 2: Documentation** (Week 2)
- Write INSTALLATION.md
- Create DISTRIBUTION-NOTES.md
- Update README for distribution
- Add directory context rules

### **Phase 3: Public Release** (Week 3)
- Create public GitHub repository
- Push distribution
- Tag v0.1.0-alpha release
- Enable GitHub Discussions

### **Phase 4: Automation** (Future)
- GitHub Actions for automated sync
- Automated testing on distribution
- Release notes generation
- Version bump automation

---

## 📚 References

- **Manifest**: `distribution-productionization-manifest.md`
- **File Organization**: `.windsurf/rules/updated-file-organization.md`
- **Similar Pattern**: Obsidian vault distributions
- **Security**: OWASP Secret Management guidelines

---

## ✅ Acceptance Criteria

**This ADR is accepted when**:
- ✅ Distribution script creates clean repository
- ✅ Security scan prevents personal data leakage
- ✅ Sample knowledge demonstrates all features
- ✅ AI agents respect repository context
- ✅ Tests pass in both source and distribution

---

**Status**: ✅ ACCEPTED  
**Next**: Implement distribution script and security audit  
**Owner**: InnerOS Development Team  
**Review Date**: 2025-11-09 (1 month post-implementation)
