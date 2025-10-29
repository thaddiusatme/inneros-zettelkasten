#!/usr/bin/env python3
"""
Tests for atomic I/O operations.
Tests safe_write() function with atomic file operations using temp + fsync + rename pattern.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open
import shutil
from pathlib import Path

# Ensure src on path to import project modules (matches existing test convention)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../src"))

# Import the module we're testing (will fail initially - RED phase)
from utils.io import safe_write


class TestAtomicIO(unittest.TestCase):

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = Path(self.test_dir) / "test_note.md"
        self.test_content = "# Test Note\n\nThis is test content."

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_safe_write_creates_file(self):
        """Test safe_write creates file with correct content."""
        safe_write(self.test_file, self.test_content)

        # Verify file exists and has correct content
        self.assertTrue(self.test_file.exists())
        self.assertEqual(self.test_file.read_text(), self.test_content)

    def test_safe_write_overwrites_existing_file(self):
        """Test safe_write overwrites existing file atomically."""
        # Create initial file
        self.test_file.write_text("Initial content")

        # Overwrite with safe_write
        new_content = "New content after atomic write"
        safe_write(self.test_file, new_content)

        # Verify overwrite worked
        self.assertEqual(self.test_file.read_text(), new_content)

    def test_safe_write_uses_temp_file_pattern(self):
        """Test safe_write uses temporary file during write operation."""
        temp_file_path = str(self.test_file) + ".tmp"

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.fsync") as mock_fsync:
                with patch("os.replace") as mock_replace:
                    safe_write(self.test_file, self.test_content)

                    # Verify temp file was opened for writing
                    mock_file.assert_called_with(temp_file_path, "w", encoding="utf-8")

                    # Verify fsync was called
                    mock_fsync.assert_called_once()

                    # Verify atomic rename from temp to final
                    mock_replace.assert_called_once_with(
                        temp_file_path, str(self.test_file)
                    )

    def test_safe_write_cleans_up_temp_on_write_failure(self):
        """Test safe_write removes temp file if write operation fails."""
        temp_file_path = str(self.test_file) + ".tmp"

        with patch("builtins.open", side_effect=IOError("Write failed")):
            with patch("os.path.exists", return_value=True):
                with patch("os.unlink") as mock_unlink:

                    with self.assertRaises(IOError):
                        safe_write(self.test_file, self.test_content)

                    # Verify temp file cleanup
                    mock_unlink.assert_called_once_with(temp_file_path)

    def test_safe_write_cleans_up_temp_on_fsync_failure(self):
        """Test safe_write removes temp file if fsync fails."""
        temp_file_path = str(self.test_file) + ".tmp"

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.fsync", side_effect=OSError("Fsync failed")):
                with patch("os.path.exists", return_value=True):
                    with patch("os.unlink") as mock_unlink:

                        with self.assertRaises(OSError):
                            safe_write(self.test_file, self.test_content)

                        # Verify temp file cleanup
                        mock_unlink.assert_called_once_with(temp_file_path)

    def test_safe_write_cleans_up_temp_on_rename_failure(self):
        """Test safe_write removes temp file if rename fails."""
        temp_file_path = str(self.test_file) + ".tmp"

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.fsync"):
                with patch("os.replace", side_effect=OSError("Rename failed")):
                    with patch("os.path.exists", return_value=True):
                        with patch("os.unlink") as mock_unlink:

                            with self.assertRaises(OSError):
                                safe_write(self.test_file, self.test_content)

                            # Verify temp file cleanup
                            mock_unlink.assert_called_once_with(temp_file_path)

    def test_safe_write_handles_unicode_content(self):
        """Test safe_write correctly handles unicode content."""
        unicode_content = "# Unicode Test\n\nEmoji: 🔥 Special chars: àáâãäå"
        safe_write(self.test_file, unicode_content)

        # Verify unicode content preserved
        self.assertEqual(self.test_file.read_text(), unicode_content)

    def test_safe_write_creates_parent_directories(self):
        """Test safe_write creates parent directories if they don't exist."""
        nested_file = Path(self.test_dir) / "nested" / "dir" / "file.md"

        safe_write(nested_file, self.test_content)

        # Verify file created with parent directories
        self.assertTrue(nested_file.exists())
        self.assertEqual(nested_file.read_text(), self.test_content)

    def test_safe_write_preserves_file_on_partial_failure(self):
        """Test original file remains unchanged if atomic write fails partway."""
        # Create original file
        original_content = "Original content that should be preserved"
        self.test_file.write_text(original_content)

        temp_file_path = str(self.test_file) + ".tmp"

        # Simulate failure during rename (after write + fsync succeed)
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.fsync"):
                with patch("os.replace", side_effect=OSError("Rename failed")):
                    with patch("os.path.exists", return_value=True):
                        with patch("os.unlink"):

                            with self.assertRaises(OSError):
                                safe_write(self.test_file, "New content")

        # Verify original file content preserved
        self.assertTrue(self.test_file.exists())
        self.assertEqual(self.test_file.read_text(), original_content)

    def test_safe_write_with_pathlib_path(self):
        """Test safe_write works with pathlib.Path objects."""
        path_obj = Path(self.test_file)
        safe_write(path_obj, self.test_content)

        # Verify pathlib.Path handling
        self.assertTrue(path_obj.exists())
        self.assertEqual(path_obj.read_text(), self.test_content)

    def test_safe_write_with_string_path(self):
        """Test safe_write works with string paths."""
        str_path = str(self.test_file)
        safe_write(str_path, self.test_content)

        # Verify string path handling
        self.assertTrue(Path(str_path).exists())
        self.assertEqual(Path(str_path).read_text(), self.test_content)


if __name__ == "__main__":
    unittest.main()
