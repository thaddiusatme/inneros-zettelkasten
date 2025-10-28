# Image Linking System - Test Plan & Implementation Guide

**Created**: 2025-10-02 08:35 PDT  
**Approach**: Option C - Centralized attachments with migration  
**Test Cases**: 7 scenarios covering all workflows

---

## 🎯 Decision: Option C - Centralized Attachments

### Implementation Strategy
- **Location**: `knowledge/attachments/YYYY-MM/` (date-based organization)
- **Link Format**: Always relative `../attachments/YYYY-MM/image.png`
- **Migration**: Move existing images during first pass
- **Intake Integration**: Save screenshots directly to attachments/

### Why Option C?
1. **Scale**: 1,502+ screenshots need organized structure
2. **Links never break**: Path stays consistent across all directories
3. **Obsidian best practice**: Industry standard approach
4. **Clean separation**: Notes vs Media assets
5. **Easy backup**: Single `attachments/` folder

### Development Timeline: 3-4 days
- **Day 1**: Discovery, test cases, RED phase
- **Day 2**: Centralized storage implementation, GREEN phase
- **Day 3**: Migration script, real data validation
- **Day 4**: REFACTOR, lessons learned, commit

---

## 📋 7 Test Cases

### Test Case 1: Existing Note with Markdown Image (Discovery)
**Purpose**: Find existing broken links in Inbox
**Location**: `knowledge/Inbox/`
**Steps**:
1. Search for notes with `![description](path)` syntax
2. Verify if referenced images exist
3. Document current link patterns
4. Use as real-world test case

---

### Test Case 2: Existing Note with Wiki Image (Discovery)
**Purpose**: Find existing wiki-style broken links
**Location**: `knowledge/Inbox/`
**Steps**:
1. Search for notes with `![[image.png]]` syntax
2. Verify if referenced images exist
3. Document attachment patterns
4. Use as real-world test case

---

### Test Case 3: Screenshot from Samsung S23 (Real Data)
**Purpose**: Test screenshot intake → attachment workflow
**Source**: Latest Samsung screenshot from TDD Iteration 9
**Scenario**:
```
1. Screenshot captured: Screenshot_20251002_083000_Chrome.jpg
2. Capture note created: capture-20251002-0830-test.md
3. Image embedded: ![Chrome screenshot](../attachments/2025-10/Screenshot_20251002_083000_Chrome.jpg)
4. Move note: Inbox → Fleeting Notes
5. AI processing: Quality score, tagging
6. Promotion: Fleeting → Permanent Notes
7. Verify: Image link works at each step
```

---

### Test Case 4: Screenshot from iPad (Real Data)
**Purpose**: Test multi-device workflow
**Source**: Latest iPad screenshot from TDD Iteration 9
**Scenario**:
```
1. Screenshot captured: 20241002_083000000_iOS.png
2. Capture note created: capture-20251002-0830-ipad-test.md
3. Image embedded: ![iPad screenshot](../attachments/2025-10/20241002_083000000_iOS.png)
4. Directory organization: Inbox → Literature Notes
5. Verify: Image link works after move
```

---

### Test Case 5: Multiple Images in Single Note (Edge Case)
**Purpose**: Test note with 3+ embedded images
**Scenario**:
```markdown
---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Multi-Screenshot Workflow Test

Step 1: Login screen
![Login](../attachments/2025-10/screenshot-login.png)

Step 2: Dashboard
![Dashboard](../attachments/2025-10/screenshot-dashboard.png)

Step 3: Settings
![Settings](../attachments/2025-10/screenshot-settings.png)
```
**Tests**:
- All 3 images work in Inbox
- All 3 images work after move to Fleeting Notes
- All 3 images work after promotion to Permanent Notes

---

### Test Case 6: Mixed Link Styles (Edge Case)
**Purpose**: Test both Markdown and Wiki syntax in same note
**Scenario**:
```markdown
---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Mixed Link Test

Markdown style:
![Screenshot 1](../attachments/2025-10/screenshot-1.png)

Wiki style:
![[screenshot-2.png]]

Verify both work after directory moves
```

---

### Test Case 7: Missing Image (Error Handling)
**Purpose**: Test broken link detection and reporting
**Scenario**:
```markdown
---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Broken Link Test

This image doesn't exist:
![Missing](../attachments/2025-10/does-not-exist.png)

Expected: System detects broken link and reports it
```

---

## 🔧 Implementation Phases

### Phase 1: Discovery & Setup (Day 1 AM)
```bash
# 1. Create attachments structure
mkdir -p knowledge/attachments/2025-10

# 2. Search for existing image references
grep -r "!\[" knowledge/Inbox/ > existing-markdown-images.txt
grep -r "!\[\[" knowledge/Inbox/ > existing-wiki-images.txt

# 3. Find orphaned images
find knowledge/Inbox -type f \( -name "*.png" -o -name "*.jpg" \) > orphaned-images.txt

# 4. Create test notes (Test Cases 3-7)
```

### Phase 2: TDD RED Phase (Day 1 PM)
```python
# Create: development/tests/unit/test_image_linking_system.py

def test_markdown_image_links_preserved_after_move():
    """Test Case 3: Samsung screenshot move"""
    # Given: Note with markdown image in Inbox
    # When: Move to Fleeting Notes
    # Then: Image link still works
    assert False  # RED: Not implemented yet

def test_wiki_image_links_preserved_after_move():
    """Test Case 4: iPad screenshot move"""
    # Given: Note with wiki-style image in Inbox
    # When: Move to Literature Notes
    # Then: Image link still works
    assert False  # RED: Not implemented yet

def test_multiple_images_in_note():
    """Test Case 5: Multiple images"""
    # Given: Note with 3 embedded images
    # When: Move through workflow (Inbox → Fleeting → Permanent)
    # Then: All 3 images work at each step
    assert False  # RED: Not implemented yet

def test_mixed_link_styles():
    """Test Case 6: Mixed markdown and wiki syntax"""
    # Given: Note with both link styles
    # When: Directory organization runs
    # Then: Both link styles work
    assert False  # RED: Not implemented yet

def test_broken_link_detection():
    """Test Case 7: Missing image detection"""
    # Given: Note with broken image link
    # When: Validation runs
    # Then: Broken link detected and reported
    assert False  # RED: Not implemented yet

def test_ai_processing_preserves_images():
    """Test Case 3: AI workflow"""
    # Given: Note with images
    # When: AI quality scoring, tagging runs
    # Then: Image references preserved in metadata
    assert False  # RED: Not implemented yet

def test_image_migration_to_attachments():
    """Existing images migrated"""
    # Given: Images scattered in Inbox/
    # When: Migration script runs
    # Then: All images in attachments/, links updated
    assert False  # RED: Not implemented yet
```

### Phase 3: Implementation (Day 2)
Create utility classes:
```python
# development/src/utils/image_link_manager.py

class ImageLinkManager:
    """Manages image references and attachment storage"""
    
    def parse_image_links(self, markdown_content: str) -> List[ImageLink]
        """Extract all image references (markdown + wiki style)"""
        
    def move_images_to_attachments(self, note_path: Path) -> None:
        """Move referenced images to centralized location"""
        
    def update_image_links(self, note_path: Path, new_location: Path) -> None:
        """Rewrite image links to maintain correctness"""
        
    def validate_image_links(self, note_path: Path) -> List[BrokenLink]:
        """Detect broken image references"""
```

Integrate with DirectoryOrganizer:
```python
# development/src/utils/directory_organizer.py

class DirectoryOrganizer:
    def __init__(self):
        self.image_manager = ImageLinkManager()  # NEW
    
    def execute_moves(self, move_plan):
        """Execute with image preservation"""
        for move in move_plan.moves:
            # NEW: Move images first
            self.image_manager.move_images_to_attachments(move.source)
            # NEW: Update links
            self.image_manager.update_image_links(move.source, move.destination)
            # Existing: Move note
            shutil.move(move.source, move.destination)
```

### Phase 4: Migration Script (Day 3)
```python
# development/scripts/migrate_images_to_attachments.py

"""
One-time migration of existing images to centralized attachments/
"""

def migrate_existing_images():
    """
    1. Find all images in knowledge/ (not in attachments/)
    2. Move to attachments/YYYY-MM/ based on file date
    3. Update all notes that reference them
    4. Generate migration report
    5. Backup before changes
    """
```

### Phase 5: Real Data Validation (Day 3)
```bash
# Run migration
python3 development/scripts/migrate_images_to_attachments.py --dry-run
python3 development/scripts/migrate_images_to_attachments.py --execute

# Test workflows
python3 development/src/cli/workflow_demo.py knowledge/ --process-inbox
python3 development/src/utils/directory_organizer.py --dry-run

# Verify in Obsidian
# Open test notes, confirm images visible
```

---

## ✅ Success Criteria

- [ ] All 7 test cases have passing tests
- [ ] Existing images migrated to `attachments/`
- [ ] New screenshots go directly to `attachments/` during intake
- [ ] Directory organization preserves image links (100%)
- [ ] AI processing preserves image references (100%)
- [ ] Note promotion preserves images (100%)
- [ ] Broken link detection reports missing images
- [ ] Real data validation: Open notes in Obsidian, images visible
- [ ] Zero data loss (backup/rollback working)
- [ ] Performance: <1s for image scanning, <0.1s per link rewrite

---

## 📊 Metrics to Track

### During Development
- Number of existing image references found
- Number of orphaned images
- Number of broken links detected
- Migration success rate

### After Deployment
- Images moved: X → attachments/
- Links rewritten: Y notes updated
- Broken links: Z detected and reported
- Test pass rate: 7/7 (100%)

---

**Ready to begin! Let me know if you want to proceed with Option C or adjust the approach.** 🚀
