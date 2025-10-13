#!/usr/bin/env python3
"""
TDD Iteration 9 - Integration Tests: Multi-Device Screenshot Processing
Tests integration of MultiDeviceDetector into ScreenshotProcessor
"""

import sys
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.cli.screenshot_processor import ScreenshotProcessor
from src.cli.multi_device_detector import MultiDeviceDetector, DeviceType


@pytest.mark.integration
@pytest.mark.fast_integration
class TestMultiDeviceScanning:
    """Test multi-device path scanning and screenshot detection.
    
    Performance: Fast (uses tempfile, no external APIs)
    """
    
    @pytest.fixture
    def temp_test_env(self):
        """Create temporary test environment with mock Samsung + iPad screenshots"""
        temp_dir = tempfile.mkdtemp()
        
        # Create Samsung path
        samsung_path = Path(temp_dir) / "Samsung Gallery" / "DCIM" / "Screenshots"
        samsung_path.mkdir(parents=True, exist_ok=True)
        
        # Create iPad path
        ipad_path = Path(temp_dir) / "Camera Roll 1" / "2024" / "09"
        ipad_path.mkdir(parents=True, exist_ok=True)
        
        # Create knowledge base
        knowledge_path = Path(temp_dir) / "knowledge"
        knowledge_path.mkdir(parents=True, exist_ok=True)
        
        # Create mock Samsung screenshots
        samsung_files = [
            samsung_path / "Screenshot_20240301_095442_Chrome.jpg",
            samsung_path / "Screenshot_20240302_143028_Gmail.jpg",
            samsung_path / "Screenshot_20240303_183045_Threads.jpg",
        ]
        for f in samsung_files:
            f.write_text("mock samsung screenshot")
        
        # Create mock iPad screenshots
        ipad_files = [
            ipad_path / "20240305_042410000_iOS.png",
            ipad_path / "20240306_221840000_iOS.png",
            ipad_path / "20240307_190004000_iOS.png",
        ]
        for f in ipad_files:
            f.write_text("mock ipad screenshot")
        
        yield {
            'temp_dir': temp_dir,
            'samsung_path': samsung_path,
            'ipad_path': ipad_path,
            'knowledge_path': knowledge_path,
            'samsung_files': samsung_files,
            'ipad_files': ipad_files
        }
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_scan_multiple_device_paths(self, temp_test_env):
        """Should scan and find screenshots from both Samsung and iPad paths"""
        # Arrange
        device_paths = [
            str(temp_test_env['samsung_path']),
            str(temp_test_env['ipad_path'])
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(temp_test_env['knowledge_path'])
        )
        
        # Act
        screenshots = processor.scan_multi_device_screenshots()
        
        # Assert
        assert len(screenshots) == 6, f"Expected 6 screenshots (3 Samsung + 3 iPad), got {len(screenshots)}"
        
        # Verify we got screenshots from both devices
        samsung_count = sum(1 for s in screenshots if 'Screenshot_' in s.name)
        ipad_count = sum(1 for s in screenshots if '_iOS.png' in s.name)
        
        assert samsung_count == 3, f"Expected 3 Samsung screenshots, got {samsung_count}"
        assert ipad_count == 3, f"Expected 3 iPad screenshots, got {ipad_count}"
    
    def test_sort_by_timestamp_across_devices(self, temp_test_env):
        """Should merge and sort screenshots by timestamp (oldest first)"""
        # Arrange
        device_paths = [
            str(temp_test_env['samsung_path']),
            str(temp_test_env['ipad_path'])
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(temp_test_env['knowledge_path'])
        )
        
        # Act
        screenshots = processor.scan_multi_device_screenshots(sort_by_timestamp=True)
        
        # Assert
        assert len(screenshots) == 6
        
        # Extract timestamps using MultiDeviceDetector
        detector = MultiDeviceDetector()
        timestamps = [detector.extract_timestamp(s) for s in screenshots]
        
        # Verify sorted order (oldest first)
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1], \
                f"Screenshots not sorted by timestamp: {timestamps[i]} > {timestamps[i + 1]}"
        
        # First should be Samsung from March 1
        assert screenshots[0].name == "Screenshot_20240301_095442_Chrome.jpg"
        # Last should be iPad from March 7
        assert screenshots[-1].name == "20240307_190004000_iOS.png"
    
    def test_device_type_detection_during_scan(self, temp_test_env):
        """Should detect device type for each screenshot during scanning"""
        # Arrange
        device_paths = [
            str(temp_test_env['samsung_path']),
            str(temp_test_env['ipad_path'])
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(temp_test_env['knowledge_path'])
        )
        
        # Act
        screenshot_metadata = processor.scan_with_device_metadata()
        
        # Assert
        assert len(screenshot_metadata) == 6
        
        # Check each screenshot has device metadata
        for metadata in screenshot_metadata:
            assert 'screenshot_path' in metadata
            assert 'device_type' in metadata
            assert 'timestamp' in metadata
            
            # Verify device types are correct
            if 'Screenshot_' in Path(metadata['screenshot_path']).name:
                assert metadata['device_type'] == DeviceType.SAMSUNG_S23.value
            elif '_iOS.png' in Path(metadata['screenshot_path']).name:
                assert metadata['device_type'] == DeviceType.IPAD.value


class TestUnifiedProcessingPipeline:
    """Test unified OCR and note generation for all devices"""
    
    @pytest.fixture
    def mock_screenshots(self):
        """Create mock screenshot files for testing"""
        temp_dir = tempfile.mkdtemp()
        
        samsung_path = Path(temp_dir) / "samsung"
        samsung_path.mkdir()
        samsung_file = samsung_path / "Screenshot_20240301_095442_Chrome.jpg"
        samsung_file.write_text("mock content")
        
        ipad_path = Path(temp_dir) / "ipad"
        ipad_path.mkdir()
        ipad_file = ipad_path / "20240305_042410000_iOS.png"
        ipad_file.write_text("mock content")
        
        knowledge_path = Path(temp_dir) / "knowledge"
        knowledge_path.mkdir()
        
        yield {
            'temp_dir': temp_dir,
            'samsung_file': samsung_file,
            'ipad_file': ipad_file,
            'knowledge_path': knowledge_path
        }
        
        shutil.rmtree(temp_dir)
    
    def test_device_metadata_in_notes(self, mock_screenshots):
        """Should include device_type in note frontmatter"""
        # Arrange
        device_paths = [
            str(mock_screenshots['samsung_file'].parent),
            str(mock_screenshots['ipad_file'].parent)
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(mock_screenshots['knowledge_path'])
        )
        
        # Act - Process screenshots and generate notes
        result = processor.process_multi_device_batch(limit=2)
        
        # Assert
        assert result['processed_count'] == 2
        assert 'individual_note_paths' in result
        
        # Check each note has device metadata
        for note_path in result['individual_note_paths']:
            note_content = Path(note_path).read_text()
            
            # Should have device_type in frontmatter
            assert 'device_type:' in note_content
            assert 'device_name:' in note_content
            
            # Device type should be Samsung Galaxy S23 or iPad
            assert 'Samsung Galaxy S23' in note_content or 'iPad' in note_content
    
    def test_process_mixed_device_batch(self, mock_screenshots):
        """Should process Samsung + iPad with same OCR pipeline"""
        # Arrange
        device_paths = [
            str(mock_screenshots['samsung_file'].parent),
            str(mock_screenshots['ipad_file'].parent)
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(mock_screenshots['knowledge_path'])
        )
        
        # Act
        result = processor.process_multi_device_batch(limit=2)
        
        # Assert - Both devices processed
        assert result['processed_count'] == 2
        assert len(result['individual_note_paths']) == 2
        
        # Assert - OCR results for both devices
        assert result['ocr_results'] == 2
        
        # Assert - Processing time reasonable
        assert result['processing_time'] < 300  # Less than 5 minutes
    
    def test_no_filename_collisions(self, mock_screenshots):
        """Should ensure no filename collisions between device notes"""
        # Arrange
        device_paths = [
            str(mock_screenshots['samsung_file'].parent),
            str(mock_screenshots['ipad_file'].parent)
        ]
        
        processor = ScreenshotProcessor(
            device_paths=device_paths,
            knowledge_path=str(mock_screenshots['knowledge_path'])
        )
        
        # Act
        result = processor.process_multi_device_batch(limit=2)
        
        # Assert
        note_paths = result['individual_note_paths']
        note_filenames = [Path(p).name for p in note_paths]
        
        # Check for duplicates
        assert len(note_filenames) == len(set(note_filenames)), \
            f"Duplicate filenames detected: {note_filenames}"


class TestDeviceFilterCLI:
    """Test CLI device filter functionality"""
    
    def test_filter_samsung_only(self):
        """Should filter to Samsung screenshots only when --device samsung"""
        # This will be implemented in P1 CLI enhancement
        pytest.skip("P1 feature: CLI device filter")
    
    def test_filter_ipad_only(self):
        """Should filter to iPad screenshots only when --device ipad"""
        pytest.skip("P1 feature: CLI device filter")
    
    def test_process_all_devices_default(self):
        """Should process all devices by default (--device all)"""
        pytest.skip("P1 feature: CLI device filter")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
