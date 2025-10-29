#!/usr/bin/env python3
"""
TDD RED Phase: LlamaVisionOCR Import Fix (P0-1.2)

Test to verify LlamaVisionOCR class is properly exportable from src.ai package.

ROOT CAUSE: llama_vision_ocr module exists but missing from __init__.py __all__ list
IMPACT: Blocks 70+ screenshot/OCR tests
FIX: Add "llama_vision_ocr" to src/ai/__init__.py __all__ exports
"""

import unittest
import sys
from pathlib import Path

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestLlamaVisionOCRImportFix(unittest.TestCase):
    """
    RED PHASE: Failing test demonstrating LlamaVisionOCR import issue

    This test verifies that the llama_vision_ocr module is properly
    exported from the src.ai package, enabling 70+ failing tests to pass.
    """

    def test_llama_vision_ocr_module_importable_from_src_ai(self):
        """
        RED: Should be able to import llama_vision_ocr module from src.ai

        Currently FAILS because llama_vision_ocr not in __all__ list
        """
        try:
            from src.ai.llama_vision_ocr import LlamaVisionOCR

            self.assertIsNotNone(
                LlamaVisionOCR, "LlamaVisionOCR class should be importable"
            )
        except ImportError as e:
            self.fail(f"Failed to import LlamaVisionOCR: {e}")

    def test_vision_analysis_result_importable_from_src_ai(self):
        """
        RED: Should be able to import VisionAnalysisResult from src.ai

        Currently FAILS because llama_vision_ocr not in __all__ list
        """
        try:
            from src.ai.llama_vision_ocr import VisionAnalysisResult

            self.assertIsNotNone(
                VisionAnalysisResult, "VisionAnalysisResult should be importable"
            )
        except ImportError as e:
            self.fail(f"Failed to import VisionAnalysisResult: {e}")

    def test_llama_vision_ocr_class_instantiable(self):
        """
        RED: Should be able to instantiate LlamaVisionOCR class

        Verifies class interface is accessible after import fix
        """
        try:
            from src.ai.llama_vision_ocr import LlamaVisionOCR

            # Create instance with default params
            ocr = LlamaVisionOCR(local_mode=True)

            self.assertIsNotNone(ocr, "LlamaVisionOCR instance should be created")
            self.assertTrue(
                hasattr(ocr, "analyze_screenshot"),
                "Should have analyze_screenshot method",
            )
            self.assertTrue(
                hasattr(ocr, "model_name"), "Should have model_name attribute"
            )

        except Exception as e:
            self.fail(f"Failed to instantiate LlamaVisionOCR: {e}")

    def test_llama_vision_ocr_in_ai_module_all_list(self):
        """
        RED: llama_vision_ocr should be in src.ai.__all__ for proper export

        This is the root cause fix - adding to __all__ list
        """
        try:
            import src.ai as ai_module

            self.assertIn(
                "llama_vision_ocr",
                ai_module.__all__,
                "llama_vision_ocr should be in __all__ list for proper module export",
            )
        except AttributeError:
            self.fail("src.ai module should have __all__ attribute")


if __name__ == "__main__":
    unittest.main()
