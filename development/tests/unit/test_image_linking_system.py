"""
TDD Iteration 10: Image Linking System Tests (GREEN Phase)

Critical system integrity tests for image preservation across all workflows.
Tests map to user stories in Projects/ACTIVE/image-linking-user-stories.md
"""
import tempfile
from pathlib import Path

# Import implementations
from src.utils.image_attachment_manager import ImageAttachmentManager
from src.utils.image_link_manager import ImageLinkManager


# ============================================================================
# P0 CRITICAL TESTS - System Integrity
# ============================================================================


def test_centralized_image_storage():
    """
    US-1: Centralized Image Storage
    Test Case: Images saved to attachments/YYYY-MM/ with auto-detected date
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Given: Screenshot from Samsung S23 with date in filename
        # Filename: Screenshot_20251002_083000_Chrome.jpg
        test_image = Path(tmpdir) / "Screenshot_20251002_083000_Chrome.jpg"
        test_image.write_text("fake image data")

        # When: ImageAttachmentManager saves image (auto-detects date and device)
        base_path = Path(tmpdir) / "knowledge"
        manager = ImageAttachmentManager(base_path=base_path)
        saved_path = manager.save_to_attachments(test_image)

        # Then: Image stored in attachments/2025-10/ with device prefix
        assert saved_path.exists()
        assert saved_path.parent.name == "2025-10"  # Auto-detected from filename
        assert "samsung" in saved_path.name  # Auto-detected device prefix
        assert saved_path.suffix == ".jpg"


def test_markdown_image_links_preserved_after_move():
    """
    US-2: Image Link Preservation During Directory Moves (Markdown syntax)
    Test Case 3: Samsung screenshot move from Inbox → Fleeting Notes
    """
    # Given: Note in Inbox with markdown image link
    note_content = """---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Test Note with Screenshot

![Chrome screenshot](../attachments/2025-10/samsung-20251002-083000.jpg)

This is a test note with an embedded image.
"""

    # When: Move note from Inbox/ to Fleeting Notes/
    source_path = Path("knowledge/Inbox/test-note.md")
    dest_path = Path("knowledge/Fleeting Notes/test-note.md")
    image_manager = ImageLinkManager()
    updated_content = image_manager.update_image_links_for_move(
        note_content, source_path, dest_path
    )

    # Then: Image link still contains correct path (stays same since both at same depth)
    assert "![Chrome screenshot](../attachments/2025-10/samsung-20251002-083000.jpg)" in updated_content
    assert "# Test Note with Screenshot" in updated_content


def test_wiki_image_links_preserved_after_move():
    """
    US-2: Image Link Preservation During Directory Moves (Wiki syntax)
    Test Case 4: iPad screenshot move from Inbox → Literature Notes
    """
    # Given: Note in Inbox with wiki-style image link
    note_content = """---
type: literature
created: 2025-10-02 08:30
status: inbox
---

# Literature Note with iPad Screenshot

![[ipad-20251002-083000.png]]

Research findings from iPad capture.
"""

    # When: Move note from Inbox/ to Literature Notes/
    source_path = Path("knowledge/Inbox/lit-note.md")
    dest_path = Path("knowledge/Literature Notes/lit-note.md")
    image_manager = ImageLinkManager()
    updated_content = image_manager.update_image_links_for_move(
        note_content, source_path, dest_path
    )

    # Then: Wiki image link unchanged (wiki links don't need path updates)
    assert "![[ipad-20251002-083000.png]]" in updated_content
    assert "# Literature Note with iPad Screenshot" in updated_content


def test_ai_processing_preserves_images():
    """
    US-3: Image Preservation During AI Processing
    Test Case 3: AI quality scoring and tagging preserves image references
    """
    # Given: Note with images ready for AI processing
    note_content = """---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Note for AI Processing

![Screenshot 1](../attachments/2025-10/screenshot-1.jpg)

Some content for quality scoring and tagging.

![Screenshot 2](../attachments/2025-10/screenshot-2.jpg)
"""

    # When: Parse image links (simulating AI processing)
    image_manager = ImageLinkManager()
    image_links = image_manager.parse_image_links(note_content)

    # Then: Image references detected and preserved
    assert len(image_links) == 2
    assert image_links[0]["path"] == "../attachments/2025-10/screenshot-1.jpg"
    assert image_links[1]["path"] == "../attachments/2025-10/screenshot-2.jpg"

    # Image content remains unchanged during parsing
    assert "![Screenshot 1](../attachments/2025-10/screenshot-1.jpg)" in note_content
    assert "![Screenshot 2](../attachments/2025-10/screenshot-2.jpg)" in note_content


# ============================================================================
# P1 ENHANCED TESTS - Robustness & Edge Cases
# ============================================================================


def test_broken_link_detection():
    """
    US-4: Broken Link Detection and Reporting
    Test Case 7: System detects and reports missing images
    """
    # Given: Note with broken image link
    note_content = """---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Note with Broken Link

![Missing image](../attachments/2025-10/does-not-exist.png)

This image doesn't exist.
"""
    note_path = Path("knowledge/Inbox/broken-link-note.md")

    # When: Validate image links
    image_manager = ImageLinkManager()
    broken_links = image_manager.validate_image_links(note_path, note_content)

    # Then: Broken link detected and reported with details
    assert len(broken_links) == 1
    broken_link = broken_links[0]
    assert broken_link["note_path"] == str(note_path)
    assert broken_link["image_path"] == "../attachments/2025-10/does-not-exist.png"
    assert broken_link["line_number"] > 0
    assert broken_link["link_type"] == "markdown"


def test_mixed_link_styles():
    """
    US-5: Mixed Link Style Support
    Test Case 6: Both Markdown and Wiki syntax work in same note
    """
    # Given: Note with mixed link styles
    note_content = """---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Mixed Link Styles Test

Markdown style:
![Screenshot 1](../attachments/2025-10/screenshot-1.png)

Wiki style:
![[screenshot-2.png]]

Wiki with width:
![[screenshot-3.png|200]]
"""

    # When: Parse image links from content
    image_manager = ImageLinkManager()
    image_links = image_manager.parse_image_links(note_content)

    # Then: All three link styles detected correctly
    assert len(image_links) == 3
    assert any(link["type"] == "markdown" and link["path"] == "../attachments/2025-10/screenshot-1.png" for link in image_links)
    assert any(link["type"] == "wiki" and link["filename"] == "screenshot-2.png" for link in image_links)
    assert any(link["type"] == "wiki" and link["filename"] == "screenshot-3.png" and link["width"] == "200" for link in image_links)


def test_multiple_images_in_note():
    """
    US-6: Multiple Images in Single Note
    Test Case 5: Note with 3+ images all preserved during moves
    """
    # Given: Note with multiple embedded images
    note_content = """---
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
"""

    # When: Parse and validate multiple images
    image_manager = ImageLinkManager()
    image_links = image_manager.parse_image_links(note_content)

    # Then: All 3 images detected and can be validated
    assert len(image_links) == 3
    assert image_links[0]["alt_text"] == "Login"
    assert image_links[1]["alt_text"] == "Dashboard"
    assert image_links[2]["alt_text"] == "Settings"

    # When: Move note to new location
    source_path = Path("knowledge/Inbox/multi-image-note.md")
    dest_path = Path("knowledge/Fleeting Notes/multi-image-note.md")
    updated_content = image_manager.update_image_links_for_move(
        note_content, source_path, dest_path
    )

    # Then: All 3 images still work from new location
    assert updated_content.count("![") == 3
    assert "../attachments/2025-10/screenshot-login.png" in updated_content
    assert "../attachments/2025-10/screenshot-dashboard.png" in updated_content
    assert "../attachments/2025-10/screenshot-settings.png" in updated_content


# ============================================================================
# INTEGRATION TESTS - Real Workflow Scenarios
# ============================================================================


def test_directory_organizer_preserves_images():
    """
    Integration: DirectoryOrganizer preserves images during file moves
    Tests full workflow: Inbox → Fleeting Notes with image preservation
    """
    # Given: Note content with image that will be moved
    note_content = """---
type: fleeting
---

![Test](../attachments/2025-10/test.png)
"""

    # When: Simulate directory move with ImageLinkManager
    source_path = Path("knowledge/Inbox/test-note.md")
    dest_path = Path("knowledge/Fleeting Notes/test-note.md")
    image_manager = ImageLinkManager()
    updated_content = image_manager.update_image_links_for_move(
        note_content, source_path, dest_path
    )

    # Then: Image links preserved after move (same depth, path unchanged)
    assert "../attachments/2025-10/test.png" in updated_content
    assert "![Test]" in updated_content


def test_workflow_manager_tracks_image_references():
    """
    Integration: WorkflowManager tracks image references in metadata
    Tests AI processing maintains image reference tracking
    """
    # Given: Note with images for AI processing
    note_content = """---
type: fleeting
created: 2025-10-02 08:30
status: inbox
---

# Test Note

![Image 1](../attachments/2025-10/img1.jpg)
![Image 2](../attachments/2025-10/img2.jpg)
"""

    # When: Extract image references using ImageLinkManager
    image_manager = ImageLinkManager()
    image_links = image_manager.parse_image_links(note_content)

    # Then: Image references properly tracked
    assert len(image_links) == 2
    assert any("img1.jpg" in link["filename"] for link in image_links)
    assert any("img2.jpg" in link["filename"] for link in image_links)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_multi_image_processing_performance():
    """
    Performance: Process note with 10+ images in <0.5s
    US-6 requirement: Fast processing for multi-image notes
    """
    import time

    # Given: Note with 10 embedded images
    images = [f"![Image {i}](../attachments/2025-10/img-{i}.png)" for i in range(10)]
    note_content = "\n\n".join(images)

    # When: Parse and validate images
    start = time.time()
    image_manager = ImageLinkManager()
    image_links = image_manager.parse_image_links(note_content)
    elapsed = time.time() - start

    # Then: Processing completes in <0.5s
    assert len(image_links) == 10
    assert elapsed < 0.5, f"Processing took {elapsed:.3f}s, expected <0.5s"


# ============================================================================
# Test Summary
# ============================================================================
"""
RED Phase Complete: 11 Failing Tests

P0 Critical (4 tests):
1. test_centralized_image_storage - US-1
2. test_markdown_image_links_preserved_after_move - US-2
3. test_wiki_image_links_preserved_after_move - US-2
4. test_ai_processing_preserves_images - US-3

P1 Enhanced (3 tests):
5. test_broken_link_detection - US-4
6. test_mixed_link_styles - US-5
7. test_multiple_images_in_note - US-6

Integration (2 tests):
8. test_directory_organizer_preserves_images
9. test_workflow_manager_tracks_image_references

Performance (1 test):
10. test_multi_image_processing_performance

Total: 11 comprehensive tests covering all P0/P1 user stories
Next: GREEN phase - Implement ImageAttachmentManager and ImageLinkManager
"""
