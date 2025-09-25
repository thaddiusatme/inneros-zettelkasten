#!/usr/bin/env python3
"""
Test Vision Models - Quick check for available Ollama vision models
"""

import sys
import os
import requests
import json
from pathlib import Path

# Add development directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def check_ollama_models():
    """Check what models are installed in Ollama"""
    print("🔍 **CHECKING OLLAMA MODELS**")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            models = models_data.get('models', [])
            
            print(f"📊 **Found {len(models)} installed models:**")
            
            vision_models = []
            other_models = []
            
            for model in models:
                model_name = model.get('name', 'unknown')
                model_size = model.get('size', 0)
                size_gb = model_size / (1024**3) if model_size else 0
                
                # Check if it's a vision model
                if any(keyword in model_name.lower() for keyword in ['vision', 'llava', 'bakllava']):
                    vision_models.append((model_name, size_gb))
                else:
                    other_models.append((model_name, size_gb))
            
            # Display vision models
            if vision_models:
                print("\n🤖 **VISION MODELS (OCR Capable):**")
                for name, size in vision_models:
                    print(f"   ✅ {name} ({size:.1f} GB)")
            else:
                print("\n⚠️  **NO VISION MODELS FOUND**")
            
            # Display other models
            if other_models:
                print(f"\n📝 **TEXT-ONLY MODELS ({len(other_models)}):**")
                for name, size in other_models[:5]:  # Show first 5
                    print(f"   • {name} ({size:.1f} GB)")
                if len(other_models) > 5:
                    print(f"   ... and {len(other_models) - 5} more")
            
            return vision_models
            
        else:
            print(f"❌ Failed to connect to Ollama: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error checking Ollama: {e}")
        return []

def test_vision_model(model_name: str):
    """Test a specific vision model with a simple request"""
    print(f"\n🧪 **TESTING VISION MODEL: {model_name}**")
    print("-" * 40)
    
    # Simple test prompt
    test_prompt = "Describe what you see in this image. Be brief."
    
    # Create test request (without actual image for now)
    payload = {
        "model": model_name,
        "prompt": test_prompt,
        "stream": False
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Model {model_name} is responding")
            print(f"   📝 Response length: {len(result.get('response', ''))}")
            return True
        else:
            print(f"   ❌ Model test failed: {response.status_code}")
            print(f"   📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Model test error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 **VISION MODEL AVAILABILITY TEST**")
    print("=" * 60)
    print("   Checking what vision models are ready for OCR")
    print()
    
    # Check installed models
    vision_models = check_ollama_models()
    
    if not vision_models:
        print("\n💡 **RECOMMENDATIONS:**")
        print("   Run these commands to install vision models:")
        print("   • ollama pull llava           # Faster, good quality")
        print("   • ollama pull llama3.2-vision # Latest, may be slower")
        print()
        return
    
    # Test available vision models
    print(f"\n🧪 **TESTING {len(vision_models)} VISION MODELS**")
    print("=" * 50)
    
    working_models = []
    
    for model_name, size in vision_models:
        if test_vision_model(model_name):
            working_models.append(model_name)
    
    # Summary
    print(f"\n🎉 **TEST RESULTS SUMMARY**")
    print("=" * 50)
    
    if working_models:
        print(f"✅ **{len(working_models)} VISION MODELS READY:**")
        for model in working_models:
            print(f"   • {model}")
        
        print(f"\n🔄 **NEXT STEPS:**")
        print(f"   1. Your Llama Vision OCR will auto-detect: {working_models[0]}")
        print(f"   2. Run the vision capture test:")
        print(f"      python3 demos/llama_vision_capture_test.py")
        print(f"   3. Your screenshots will now include OCR text extraction!")
        
    else:
        print("❌ **NO WORKING VISION MODELS**")
        print("   Models may still be downloading or need troubleshooting")
        
        # Check if models are still downloading
        print(f"\n📥 **DOWNLOAD STATUS CHECK:**")
        try:
            # Check llama3.2-vision download
            response = requests.get("http://localhost:11434/api/ps", timeout=5)
            if response.status_code == 200:
                processes = response.json().get('models', [])
                if processes:
                    print("   🔄 Active downloads/processes:")
                    for proc in processes[:3]:  # Show first 3
                        print(f"      • {proc}")
                else:
                    print("   📝 No active downloads detected")
            
        except:
            pass

if __name__ == "__main__":
    main()
