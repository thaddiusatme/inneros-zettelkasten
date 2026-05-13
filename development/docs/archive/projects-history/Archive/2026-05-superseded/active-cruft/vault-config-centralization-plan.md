# Vault Configuration Centralization Plan

**Created**: 2025-11-02  
**Context**: Sprint 1 Retrospective complete, improving starter pack  
**Goal**: Point all automations to `knowledge/Inbox` instead of root-level `Inbox/`

---

## 🎯 Objective

Centralize vault directory configuration so all automations, CLIs, and workflows consistently use:
- **Primary vault root**: `knowledge/`
- **Primary inbox**: `knowledge/Inbox/`
- **All other directories**: `knowledge/{Directory Name}/`

---

## 📊 Current State Analysis

### **Hardcoded Paths Found**

| Module | Current Code | Affected |
|--------|-------------|----------|
| `promotion_engine.py` | `self.inbox_dir = self.base_dir / "Inbox"` | ✅ Auto-promotion |
| `workflow_reporting_coordinator.py` | `self.inbox_dir = self.base_dir / "Inbox"` | ✅ Reports |
| `fleeting_note_coordinator.py` | `inbox_dir: Path` (parameter) | ✅ Note promotion |
| `metadata_repair_engine.py` | `inbox_dir: str` (parameter) | ✅ Metadata repair |
| `safe_image_processing_coordinator.py` | `inbox_dir: Path` (parameter) | ✅ Image processing |
| `review_triage_coordinator.py` | `self.inbox_dir = self.base_dir / "Inbox"` | ✅ Weekly reviews |
| `analytics_coordinator.py` | `self.inbox_dir = self.base_dir / "Inbox"` | ✅ Analytics |
| `.automation/scripts/` | Various hardcoded paths | ✅ All automation |
| `daemon_config.yaml` | `watch_path: ../knowledge/Inbox` | ✅ Already correct! |

**Total Affected**: 15+ modules, 812 file references

---

## 🔧 Solution Architecture

### **Phase 1: Configuration Infrastructure** ✅ COMPLETE

Created centralized configuration system:

1. **`vault_config.yaml`** - Central configuration file
   ```yaml
   vault:
     root: knowledge
     directories:
       inbox: Inbox
       fleeting: Fleeting Notes
       permanent: Permanent Notes
       # ... etc
   ```

2. **`vault_config_loader.py`** - Configuration loader module
   ```python
   from src.config import get_vault_config
   
   config = get_vault_config()
   inbox_path = config.inbox_dir  # Returns: knowledge/Inbox
   ```

3. **Benefits**:
   - ✅ Single source of truth for directory structure
   - ✅ Easy to switch between `knowledge/` and root-level for testing
   - ✅ No code changes needed to adjust paths
   - ✅ Backwards compatible with existing tests

---

### **Phase 2: Module Migration** (TODO)

**Strategy**: Update modules progressively, maintain backwards compatibility

#### **Priority 1: Core Workflow Modules** (Highest Impact)

1. **`promotion_engine.py`**
   ```python
   # OLD:
   self.inbox_dir = self.base_dir / "Inbox"
   
   # NEW:
   from src.config import get_vault_config
   config = get_vault_config(str(self.base_dir))
   self.inbox_dir = config.inbox_dir
   ```
   **Impact**: Auto-promotion workflow uses correct inbox

2. **`workflow_reporting_coordinator.py`**
   ```python
   # OLD:
   self.inbox_dir = self.base_dir / "Inbox"
   
   # NEW:
   from src.config import get_vault_config
   config = get_vault_config(str(self.base_dir))
   self.inbox_dir = config.inbox_dir
   ```
   **Impact**: Reports scan correct directory

3. **`review_triage_coordinator.py`**
   ```python
   # OLD:
   self.inbox_dir = self.base_dir / "Inbox"
   
   # NEW:
   from src.config import get_vault_config
   config = get_vault_config(str(self.base_dir))
   self.inbox_dir = config.inbox_dir
   ```
   **Impact**: Weekly reviews scan correct inbox

#### **Priority 2: CLI Tools** (User-Facing)

4. **`core_workflow_cli.py`**
   - Update to use vault config for directory resolution
   - Maintain existing auto-detection logic as fallback

5. **`workflow_demo.py`**
   - Already has auto-detection for `knowledge/Inbox`
   - Add explicit vault config support
   - Update help text to mention `knowledge/` structure

#### **Priority 3: Coordinators** (Moderate Impact)

6. **`fleeting_note_coordinator.py`** - Update `__init__` parameter defaults
7. **`analytics_coordinator.py`** - Update directory initialization
8. **`safe_image_processing_coordinator.py`** - Update parameter defaults

#### **Priority 4: Automation Scripts** (Production Impact)

9. **`.automation/scripts/`**:
   - `repair_metadata.py`
   - `validate_metadata.py`
   - `organize_harissa_content.py`
   - `update_changelog.py`
   - Others as needed

---

### **Phase 3: Testing & Verification** (TODO)

**Test Strategy**:
1. ✅ Config loader unit tests
2. ✅ Integration tests with `knowledge/Inbox`
3. ✅ Verify existing tests still pass (use test fixtures)
4. ✅ Manual testing with live `knowledge/` vault

**Verification Checklist**:
- [ ] Auto-promotion scans `knowledge/Inbox/`
- [ ] CLI commands default to `knowledge/`
- [ ] Reports generated in correct location
- [ ] Automation scripts use correct paths
- [ ] Tests still pass (using fixture paths)
- [ ] Documentation updated

---

### **Phase 4: Documentation** (TODO)

**Update Required**:
1. **README.md** - Update vault structure examples
2. **CLI-REFERENCE.md** - Update path examples
3. **GETTING-STARTED.md** - Update directory references
4. **knowledge-starter-pack/README.md** - Update structure guide
5. **`.windsurf/rules/`** - Update file organization rules

---

## 🚀 Migration Script

Create automated migration script for batch updates:

```python
# scripts/migrate_to_vault_config.py
"""
Automated migration script to update modules to use vault config.

Usage:
    python scripts/migrate_to_vault_config.py --dry-run  # Preview changes
    python scripts/migrate_to_vault_config.py            # Apply changes
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_hardcoded_inbox_paths(file_path: Path) -> List[Tuple[int, str]]:
    """Find lines with hardcoded Inbox paths."""
    pattern = r'["\']Inbox["\']'
    matches = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if re.search(pattern, line):
                matches.append((line_num, line.strip()))
    
    return matches

def migrate_file(file_path: Path, dry_run: bool = True) -> bool:
    """Migrate a single file to use vault config."""
    # Implementation here
    pass

def main(dry_run: bool = True):
    """Run migration on all Python files."""
    src_dir = Path("development/src/ai")
    files_to_migrate = list(src_dir.glob("*.py"))
    
    for file_path in files_to_migrate:
        print(f"Processing: {file_path}")
        matches = find_hardcoded_inbox_paths(file_path)
        
        if matches:
            print(f"  Found {len(matches)} hardcoded paths:")
            for line_num, line in matches:
                print(f"    Line {line_num}: {line}")
            
            if not dry_run:
                migrate_file(file_path, dry_run=False)
    
    if dry_run:
        print("\n✅ Dry run complete. Run without --dry-run to apply changes.")
```

---

## 📝 Rollout Plan

### **Week 1: Foundation** (Current Sprint)
- [x] Create `vault_config.yaml`
- [x] Create `vault_config_loader.py`
- [ ] Write unit tests for config loader
- [ ] Create migration script skeleton

### **Week 2: Core Modules** (Sprint 2 - Automation Stability)
- [ ] Migrate Priority 1 modules (promotion, reporting, triage)
- [ ] Migrate Priority 2 modules (CLI tools)
- [ ] Update automation scripts
- [ ] Integration testing

### **Week 3: Polish & Documentation**
- [ ] Migrate remaining modules
- [ ] Update all documentation
- [ ] Update starter pack examples
- [ ] Create migration guide for users

---

## 🎓 Benefits

### **Immediate**:
- ✅ All automations use `knowledge/Inbox/` consistently
- ✅ No more confusion between root-level and knowledge-level directories
- ✅ Easier to understand vault structure for new users

### **Long-term**:
- ✅ Easy to reconfigure vault structure without code changes
- ✅ Support multiple vault configurations (dev, test, prod)
- ✅ Simpler testing (can specify test fixture paths)
- ✅ Better starter pack examples

---

## 🔗 Related

- **Starter Pack Improvements**: Vault config enables better templates
- **Sprint 1 Success**: Demonstrated workflows now use correct paths
- **Sprint 2 Automation**: Stability work benefits from consistent paths

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Break existing tests | High | Keep test fixtures separate, backwards compatibility |
| Break automation scripts | High | Phase rollout, extensive testing |
| User confusion | Medium | Clear documentation, migration guide |
| Performance overhead | Low | Config cached with @lru_cache |

---

## ✅ Acceptance Criteria

Migration is complete when:
1. ✅ Config system implemented and tested
2. ✅ All Priority 1-2 modules migrated
3. ✅ Automation scripts use vault config
4. ✅ All tests pass
5. ✅ Documentation updated
6. ✅ Live vault (`knowledge/`) works correctly
7. ✅ Starter pack reflects new structure

---

**Next Steps**: 
1. Write tests for `vault_config_loader.py`
2. Start Priority 1 module migrations
3. Update documentation as we go

**Estimated Effort**: 4-6 hours over 2-3 sessions
