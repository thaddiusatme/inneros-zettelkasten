"""
Llama 3.2 Vision OCR Integration for Knowledge Capture System

Provides advanced image understanding and content analysis for Samsung S23 screenshots
using Llama 3.2 Vision multimodal capabilities.

Features:
- Text extraction with context understanding
- Content analysis and topic identification  
- Connection discovery opportunities
- Knowledge insights and recommendations
"""

import base64
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests

logger = logging.getLogger(__name__)


@dataclass
class VisionAnalysisResult:
    """Results from Llama 3.2 Vision analysis of screenshot"""
    extracted_text: str
    content_summary: str
    main_topics: List[str]
    key_insights: List[str]
    suggested_connections: List[str]
    content_type: str  # 'article', 'social_media', 'code', 'diagram', etc.
    confidence_score: float
    processing_time: float


class LlamaVisionOCR:
    """Llama 3.2 Vision integration for screenshot content analysis"""
    
    def __init__(self, 
                 api_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 model_name: Optional[str] = None,
                 local_mode: bool = True):
        """
        Initialize Llama Vision OCR processor
        
        Args:
            api_endpoint: API endpoint for hosted Llama 3.2 Vision
            api_key: API authentication key
            model_name: Model name/version to use
            local_mode: Whether to use local Ollama instance
        """
        self.api_endpoint = api_endpoint or "http://localhost:11434/api/generate"
        self.api_key = api_key
        self.local_mode = local_mode
        
        # Auto-detect available vision model if not specified
        if model_name is None and local_mode:
            self.model_name = self._detect_available_vision_model()
        else:
            self.model_name = model_name or "llama3.2-vision"
        
        logger.info(f"Initialized LlamaVisionOCR with model: {self.model_name}")
        
        # Analysis prompt optimized for LLaVA model
        self.analysis_prompt = """Analyze this screenshot and extract the following information in JSON format only:

1. Extract all visible text verbatim
2. Identify the main topic or subject  
3. List 2-3 key topics
4. Provide 2-3 key insights
5. Suggest potential connections
6. Classify content type
7. Rate confidence 0.0-1.0

Respond with ONLY this JSON, no other text:
{
    "extracted_text": "exact text from image",
    "content_summary": "what this is about",
    "main_topics": ["topic1", "topic2"],
    "key_insights": ["insight1", "insight2"],  
    "suggested_connections": ["connection1", "connection2"],
    "content_type": "social_media",
    "confidence_score": 0.85
}"""

    def _detect_available_vision_model(self) -> str:
        """Detect which vision model is available in Ollama"""
        vision_models = [
            "llama3.2-vision",
            "llama3.2-vision:11b", 
            "llama3.2-vision:90b",
            "llava",
            "llava:7b",
            "llava:13b",
            "bakllava"
        ]
        
        try:
            # Try to get list of installed models
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                installed_models = [model.get('name', '') for model in response.json().get('models', [])]
                
                # Check for vision models in order of preference
                for model in vision_models:
                    if any(model in installed for installed in installed_models):
                        logger.info(f"Detected available vision model: {model}")
                        return model
                        
                logger.warning("No vision models detected, falling back to llama3.2-vision")
                return "llama3.2-vision"
            else:
                logger.warning("Could not connect to Ollama, using default model")
                return "llama3.2-vision"
                
        except Exception as e:
            logger.warning(f"Model detection failed: {e}, using default")
            return "llama3.2-vision"

    def _encode_image(self, image_path: Path) -> str:
        """Encode image to base64 for API transmission"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return ""

    def _make_vision_request(self, image_base64: str) -> Optional[Dict]:
        """Make API request to Llama Vision model"""
        start_time = time.time()
        
        try:
            if self.local_mode:
                # Local Ollama request
                payload = {
                    "model": self.model_name,
                    "prompt": self.analysis_prompt,
                    "images": [image_base64],
                    "stream": False
                }
                
                response = requests.post(
                    self.api_endpoint,
                    json=payload,
                    timeout=60
                )
                
            else:
                # Cloud API request (adjust format based on your provider)
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {
                    "model": self.model_name,
                    "messages": [
                        {
                            "role": "user", 
                            "content": [
                                {"type": "text", "text": self.analysis_prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                            ]
                        }
                    ]
                }
                
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result['processing_time'] = processing_time
                return result
            else:
                logger.error(f"Vision API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Vision request failed: {e}")
            return None

    def _parse_vision_response(self, response_data: Dict) -> Optional[Dict]:
        """Parse Llama Vision response and extract structured data"""
        try:
            # Handle different response formats
            if self.local_mode and 'response' in response_data:
                content = response_data['response']
            elif 'choices' in response_data:
                content = response_data['choices'][0]['message']['content']
            else:
                logger.error(f"Unexpected response format: {response_data}")
                return None
            
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback: parse LLaVA's structured text response
                logger.info("No JSON found, attempting to parse structured text response")
                return self._parse_structured_text_response(content)
                
        except json.JSONDecodeError as e:
            logger.info(f"JSON parsing failed, trying structured text: {e}")
            return self._parse_structured_text_response(content)
        except Exception as e:
            logger.error(f"Failed to parse vision response: {e}")
            return None

    def _parse_structured_text_response(self, content: str) -> Optional[Dict]:
        """Parse LLaVA's structured text response into JSON format"""
        try:
            import re
            
            # Initialize result with defaults
            result = {
                "extracted_text": "",
                "content_summary": "",
                "main_topics": [],
                "key_insights": [],
                "suggested_connections": [],
                "content_type": "unknown",
                "confidence_score": 0.75  # Default confidence for text parsing
            }
            
            # Extract sections using regex patterns
            patterns = {
                "extracted_text": [
                    r"(?:\*\*)?Extracted Text(?:\*\*)?:?\s*\n\n?(.*?)(?=\n\n\*\*|\n\*\*|$)",
                    r"The extracted text.*?is:?\s*\n\n?(.*?)(?=\n\n\*\*|\n\*\*|$)"
                ],
                "content_summary": [
                    r"(?:\*\*)?Content Summary(?:\*\*)?:?\s*\n\n?(.*?)(?=\n\n\*\*|\n\*\*|$)",
                    r"The main topic.*?is.*?\n\n?(.*?)(?=\n\n\*\*|\n\*\*|$)"
                ]
            }
            
            # Try to extract text and summary
            for field, regex_list in patterns.items():
                for pattern in regex_list:
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        extracted = match.group(1).strip()
                        if extracted and len(extracted) > 10:  # Reasonable content
                            result[field] = extracted
                            break
            
            # Extract topics (look for bullet points or listed items)
            topic_patterns = [
                r"(?:\*\*)?Main Topics(?:\*\*)?:?\s*\n(.*?)(?=\n\n\*\*|\n\*\*|$)",
                r"Programming language.*framework.*Code examples.*Technical discussion"
            ]
            
            for pattern in topic_patterns:
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                if match:
                    topics_text = match.group(1).strip() if match.groups() else match.group(0)
                    # Extract individual topics
                    topics = re.findall(r'[\*\-]\s*([^\n\*\-]+)', topics_text)
                    if not topics:
                        # Fallback: look for comma-separated or line-separated items
                        topics = [t.strip() for t in topics_text.replace('*', '').split('\n') if t.strip()]
                    
                    result["main_topics"] = [t.strip() for t in topics if t.strip()][:3]  # Max 3 topics
                    break
            
            # Extract insights
            insights_match = re.search(r"(?:\*\*)?Key Insights(?:\*\*)?:?\s*\n(.*?)(?=\n\n\*\*|\n\*\*|$)", 
                                    content, re.DOTALL | re.IGNORECASE)
            if insights_match:
                insights_text = insights_match.group(1).strip()
                insights = re.findall(r'[\*\-]\s*([^\n\*\-]+)', insights_text)
                if not insights:
                    insights = [i.strip() for i in insights_text.replace('*', '').split('\n') if i.strip()]
                result["key_insights"] = [i.strip() for i in insights if i.strip()][:3]
            
            # Determine content type from description
            content_lower = content.lower()
            if "messaging" in content_lower or "conversation" in content_lower:
                result["content_type"] = "messaging_app"
            elif "social media" in content_lower:
                result["content_type"] = "social_media"
            elif "code" in content_lower or "programming" in content_lower:
                result["content_type"] = "code_discussion"
            elif "article" in content_lower:
                result["content_type"] = "article"
            
            # Generate suggested connections based on content
            if result["main_topics"]:
                result["suggested_connections"] = result["main_topics"][:2]  # Use top topics as connections
            
            logger.info("Successfully parsed structured text response")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse structured text response: {e}")
            return None

    def analyze_screenshot(self, image_path: Path) -> Optional[VisionAnalysisResult]:
        """
        Analyze screenshot using Llama 3.2 Vision
        
        Args:
            image_path: Path to screenshot image file
            
        Returns:
            VisionAnalysisResult with extracted content and analysis
        """
        if not image_path.exists():
            logger.error(f"Image file not found: {image_path}")
            return None
        
        logger.info(f"Analyzing screenshot with Llama Vision: {image_path}")
        start_time = time.time()
        
        try:
            # Encode image for API
            image_base64 = self._encode_image(image_path)
            if not image_base64:
                return None
            
            # Make vision request
            response_data = self._make_vision_request(image_base64)
            if not response_data:
                return None
            
            # Parse response
            parsed_data = self._parse_vision_response(response_data)
            if not parsed_data:
                return None
            
            # Create result object
            processing_time = time.time() - start_time
            
            result = VisionAnalysisResult(
                extracted_text=parsed_data.get('extracted_text', ''),
                content_summary=parsed_data.get('content_summary', ''),
                main_topics=parsed_data.get('main_topics', []),
                key_insights=parsed_data.get('key_insights', []),
                suggested_connections=parsed_data.get('suggested_connections', []),
                content_type=parsed_data.get('content_type', 'unknown'),
                confidence_score=parsed_data.get('confidence_score', 0.0),
                processing_time=processing_time
            )
            
            logger.info(f"Vision analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Screenshot analysis failed: {e}")
            return None

    def analyze_multiple_screenshots(self, image_paths: List[Path]) -> Dict[str, VisionAnalysisResult]:
        """Batch analyze multiple screenshots"""
        results = {}
        
        for image_path in image_paths:
            result = self.analyze_screenshot(image_path)
            if result:
                results[str(image_path)] = result
        
        return results

    def get_fallback_analysis(self, image_path: Path) -> VisionAnalysisResult:
        """Provide fallback analysis when Vision API is unavailable"""
        return VisionAnalysisResult(
            extracted_text="[Vision API unavailable - text extraction skipped]",
            content_summary="Screenshot captured but not analyzed due to API limitations",
            main_topics=["screenshot", "unprocessed"],
            key_insights=["Manual review needed"],
            suggested_connections=[],
            content_type="unknown",
            confidence_score=0.0,
            processing_time=0.0
        )


def test_llama_vision_integration():
    """Test function for Llama Vision OCR integration"""
    # Initialize with local Ollama (adjust as needed)
    vision_ocr = LlamaVisionOCR(local_mode=True)
    
    # Test with a sample image (adjust path)
    test_image = Path("test_screenshot.jpg")
    
    if test_image.exists():
        result = vision_ocr.analyze_screenshot(test_image)
        if result:
            print(f"✅ Vision Analysis Success!")
            print(f"📝 Extracted Text: {result.extracted_text[:100]}...")
            print(f"📊 Topics: {result.main_topics}")
            print(f"💡 Insights: {result.key_insights}")
            print(f"🔗 Connections: {result.suggested_connections}")
        else:
            print("❌ Vision analysis failed")
    else:
        print(f"❌ Test image not found: {test_image}")


if __name__ == "__main__":
    test_llama_vision_integration()
