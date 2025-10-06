# Image Linking System - User Stories & Product Backlog

**Created**: 2025-10-02 09:08 PDT  
**Epic**: Image Linking System - Preserve media assets through all workflows  
**Priority**: 🔴 CRITICAL - System Integrity

---

## 🎯 Epic Statement

**As a** knowledge worker capturing ideas via screenshots  
**I want** my images to remain accessible no matter how I organize or process my notes  
**So that** I can trust my knowledge system to preserve my visual context forever

---

## 📋 User Stories by Priority

### P0 - Critical Foundation (Must Have)

#### US-1: Centralized Image Storage
**As a** knowledge worker with 1,500+ screenshots  
**I want** all my images stored in a single, organized location (`attachments/YYYY-MM/`)  
**So that** I have a predictable structure and my images don't get scattered across directories

**Acceptance Criteria**:
- [ ] New screenshots saved directly to `knowledge/attachments/YYYY-MM/`
- [ ] Folder structure auto-created based on capture date
- [ ] Naming convention preserves original filename with device prefix
- [ ] Existing scattered images can be migrated to centralized location

**Test Mapping**: Foundation for Test Cases 3, 4, 5

**Technical Tasks**:
- [ ] Create `ImageAttachmentManager` class
- [ ] Add `save_to_attachments(image_path, capture_date)` method
- [ ] Implement folder structure creation (`YYYY-MM/`)
- [ ] Add file naming convention logic

---

#### US-2: Image Link Preservation During Directory Moves
**As a** user moving notes from Inbox to Fleeting/Permanent Notes  
**I want** my image links to automatically work in the new location  
**So that** I don't lose visual context when organizing my knowledge

**Acceptance Criteria**:
- [ ] Moving note from `Inbox/` → `Fleeting Notes/` preserves image links
- [ ] Moving note from `Fleeting Notes/` → `Permanent Notes/` preserves image links
- [ ] Both Markdown `![](path)` and Wiki `![[image]]` syntax supported
- [ ] Relative paths calculated correctly: `../attachments/YYYY-MM/image.png`
- [ ] Multiple images in single note all preserved

**Test Mapping**: Test Cases 3, 4, 5, 6

**Technical Tasks**:
- [ ] Integrate `ImageLinkManager` with `DirectoryOrganizer`
- [ ] Add `update_image_links(note_path, new_location)` method
- [ ] Implement relative path calculation
- [ ] Support both markdown and wiki syntax parsing

---

#### US-3: Image Preservation During AI Processing
**As a** user running AI workflows (quality scoring, tagging, summarization)  
**I want** my images to remain accessible after AI processing  
**So that** automation doesn't break my visual references

**Acceptance Criteria**:
- [ ] AI quality scoring preserves image links in metadata
- [ ] Auto-tagging preserves embedded images
- [ ] Weekly review processing doesn't corrupt image references
- [ ] Inbox enhancement maintains image links
- [ ] Image references tracked in YAML frontmatter if needed

**Test Mapping**: Test Case 3 (AI processing step)

**Technical Tasks**:
- [ ] Audit `WorkflowManager.process_inbox_note()` for image handling
- [ ] Add image reference preservation to AI processing pipeline
- [ ] Test with real Samsung/iPad screenshot notes

---

### P1 - Enhanced Features (Should Have)

#### US-4: Broken Link Detection and Reporting
**As a** user with a large knowledge base  
**I want** to be alerted when image links are broken  
**So that** I can fix issues before they cause problems

**Acceptance Criteria**:
- [ ] System scans notes and detects missing images
- [ ] CLI command: `--validate-images` reports broken links
- [ ] Broken link report shows: note path, image path, line number
- [ ] Export report as markdown and JSON
- [ ] Integration with weekly review: "X broken image links detected"

**Test Mapping**: Test Case 7

**Technical Tasks**:
- [ ] Create `validate_image_links(note_path)` method
- [ ] Add CLI integration: `workflow_demo.py --validate-images`
- [ ] Generate broken link report with details
- [ ] Add to weekly review metrics

---

#### US-5: Mixed Link Style Support
**As a** user who sometimes uses Markdown syntax and sometimes Wiki syntax  
**I want** both formats to work seamlessly  
**So that** I don't have to worry about which syntax I used

**Acceptance Criteria**:
- [ ] Parse and preserve `![description](path/to/image.png)` (Markdown)
- [ ] Parse and preserve `![[image.png]]` (Wiki)
- [ ] Parse and preserve `![[image.png|200]]` (Wiki with width)
- [ ] Mixed syntax in same note works correctly
- [ ] Conversion between formats optional (future enhancement)

**Test Mapping**: Test Case 6

**Technical Tasks**:
- [ ] Implement regex patterns for both syntaxes
- [ ] Create unified `ImageLink` data structure
- [ ] Handle edge cases (embedded links, special characters)

---

#### US-6: Multiple Images in Single Note
**As a** user documenting multi-step processes  
**I want** to embed multiple screenshots in one note  
**So that** I can tell complete stories with visual context

**Acceptance Criteria**:
- [ ] Notes with 3+ images all preserved during moves
- [ ] Each image link independently validated
- [ ] Performance: <0.5s to process note with 10 images
- [ ] No duplicate images created
- [ ] All images visible in Obsidian after processing

**Test Mapping**: Test Case 5

**Technical Tasks**:
- [ ] Batch process multiple image links in single note
- [ ] Optimize performance for multi-image notes
- [ ] Add test with 10+ images

---

### P2 - Future Enhancements (Nice to Have)

#### US-7: Image Migration for Existing Notes
**As a** user with existing notes containing scattered images  
**I want** a one-time migration to centralized attachments  
**So that** my old notes benefit from the new system

**Acceptance Criteria**:
- [ ] CLI command: `--migrate-images` with dry-run mode
- [ ] Finds all images in `knowledge/` (excluding `attachments/`)
- [ ] Moves images to `attachments/YYYY-MM/` based on file date
- [ ] Updates all notes referencing moved images
- [ ] Generates migration report: "X images moved, Y notes updated"
- [ ] Backup created before migration
- [ ] Rollback available if migration fails

**Test Mapping**: Test Cases 1, 2 (discovery phase)

**Technical Tasks**:
- [ ] Create `migrate_images_to_attachments.py` script
- [ ] Implement dry-run mode
- [ ] Add backup/rollback safety
- [ ] Generate detailed migration report

---

#### US-8: Image Metadata Tracking
**As a** user with many screenshots  
**I want** to track which images are used in which notes  
**So that** I can clean up unused images and understand dependencies

**Acceptance Criteria**:
- [ ] YAML frontmatter tracks referenced images: `images: [file1.png, file2.png]`
- [ ] Inverse index: given image, find all notes using it
- [ ] Orphaned image detection: images not referenced anywhere
- [ ] CLI command: `--unused-images` finds orphans
- [ ] Safe deletion: "Image used in 3 notes, confirm deletion?"

**Test Mapping**: Future analytics feature

**Technical Tasks**:
- [ ] Add `images: []` field to YAML schema
- [ ] Build image-to-notes index
- [ ] Create orphaned image detector
- [ ] Add safe deletion workflow

---

#### US-9: Multi-Device Image Consistency
**As a** user capturing screenshots from Samsung S23 and iPad  
**I want** images from all devices treated consistently  
**So that** I have a unified workflow regardless of device

**Acceptance Criteria**:
- [ ] Samsung screenshots: `attachments/YYYY-MM/samsung-YYYYMMDD-HHMMSS.jpg`
- [ ] iPad screenshots: `attachments/YYYY-MM/ipad-YYYYMMDD-HHMMSS.png`
- [ ] Device prefix in filename for easy identification
- [ ] Same relative path structure for all devices
- [ ] Integration with TDD Iteration 9 multi-device detection

**Test Mapping**: Test Case 3 (Samsung), Test Case 4 (iPad)

**Technical Tasks**:
- [ ] Integrate with `MultiDeviceDetector` from TDD Iteration 9
- [ ] Add device-aware filename prefixes
- [ ] Test with real Samsung + iPad screenshots

---

## 🗺️ Story Mapping

### Sprint 1: Foundation (Days 1-2)
- US-1: Centralized Image Storage
- US-2: Image Link Preservation During Directory Moves
- US-3: Image Preservation During AI Processing

**Goal**: Core image preservation working for all workflows

---

### Sprint 2: Validation & Edge Cases (Day 3)
- US-4: Broken Link Detection and Reporting
- US-5: Mixed Link Style Support
- US-6: Multiple Images in Single Note

**Goal**: Robust handling of edge cases and error conditions

---

### Sprint 3: Migration & Enhancement (Future)
- US-7: Image Migration for Existing Notes
- US-8: Image Metadata Tracking
- US-9: Multi-Device Image Consistency

**Goal**: Production-ready system with full feature set

---

## ✅ Definition of Done (DoD)

For each user story to be considered "done":

- [ ] **Tests**: Failing test written (RED) → Implementation (GREEN) → Refactored
- [ ] **Code**: Production-quality with error handling and logging
- [ ] **Integration**: Works with DirectoryOrganizer and WorkflowManager
- [ ] **Validation**: Tested with real screenshots from Samsung S23 and iPad
- [ ] **Documentation**: Code comments, docstrings, usage examples
- [ ] **Performance**: Meets target (<1s image scan, <0.1s link rewrite)
- [ ] **Safety**: Backup/rollback working, no data loss risk
- [ ] **User Testing**: Images visible in Obsidian after processing

---

## 📊 Success Metrics

### Technical Metrics
- **Test Coverage**: 100% on ImageLinkManager and integration
- **Performance**: <1s to scan 100+ notes, <0.1s per link rewrite
- **Reliability**: 0 image loss events in production
- **Broken Links**: <1% broken link rate after migration

### User Metrics
- **Trust**: User confident automating workflows with images
- **Organization**: All 1,502+ screenshots in predictable structure
- **Workflow**: Zero manual image link fixes needed
- **Adoption**: All 7 test cases passing in production

---

## 🚀 Implementation Order

### Phase 1: TDD RED (Day 1)
1. **US-1** tests: Centralized storage structure
2. **US-2** tests: Link preservation during moves
3. **US-3** tests: AI processing preservation
4. **US-5** tests: Mixed link styles
5. **US-6** tests: Multiple images
6. **US-4** tests: Broken link detection

### Phase 2: TDD GREEN (Day 2)
1. Implement `ImageAttachmentManager`
2. Implement `ImageLinkManager`
3. Integrate with `DirectoryOrganizer`
4. Integrate with `WorkflowManager`
5. Add CLI commands

### Phase 3: TDD REFACTOR (Day 3)
1. Extract utility classes
2. Real data validation (7 test cases)
3. Performance optimization
4. Documentation and lessons learned

---

**Ready to begin Sprint 1! Next: Create TDD RED phase tests for US-1, US-2, US-3.** 🎯
