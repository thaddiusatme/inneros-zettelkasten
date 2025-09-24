#!/usr/bin/env python3
"""
Enhanced Connection Discovery - Feedback Collection System
TDD Iteration 7 - User Feedback Integration

Collects detailed connection data for user feedback and system improvement.
Follows established CLI patterns from fleeting-triage and enhanced-metrics.
"""

import os
import sys
from pathlib import Path
import json
import time
from typing import Dict, List, Any
from datetime import datetime

# Add development directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.ai.enhanced_connections import EnhancedConnectionsEngine
    from src.utils.frontmatter import parse_frontmatter
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure you're running from the development directory")
    sys.exit(1)


class ConnectionFeedbackCollector:
    """Collect detailed connection data and export for user feedback"""
    
    def __init__(self, vault_path: str):
        """Initialize feedback collector"""
        self.vault_path = Path(vault_path)
        self.engine = EnhancedConnectionsEngine()
        self.feedback_data = {
            "session_info": {
                "timestamp": datetime.now().isoformat(),
                "vault_path": str(vault_path),
                "notes_analyzed": 0,
                "connections_found": 0
            },
            "relationship_connections": [],
            "strength_connections": [],
            "cross_domain_connections": [],
            "processing_stats": {}
        }
        
    def load_sample_notes(self, max_notes: int = 10) -> Dict[str, Dict]:
        """Load sample notes with enhanced metadata extraction"""
        sample_notes = {}
        directories_to_check = [
            "knowledge/Fleeting Notes",
            "knowledge/Literature Notes", 
            "knowledge/Permanent Notes",
            "Projects"
        ]
        
        notes_loaded = 0
        for directory in directories_to_check:
            if notes_loaded >= max_notes:
                break
                
            dir_path = self.vault_path / directory
            if not dir_path.exists():
                continue
                
            print(f"📂 Loading from {directory}...")
            
            for md_file in dir_path.glob("*.md"):
                if notes_loaded >= max_notes:
                    break
                    
                try:
                    content = md_file.read_text(encoding='utf-8')
                    frontmatter, body = parse_frontmatter(content)
                    
                    # Skip if content is too short
                    if len(body.strip()) < 100:
                        continue
                    
                    # Extract enhanced metadata
                    concepts = self._extract_concepts(frontmatter, body)
                    domain = self._determine_domain(directory, frontmatter, body)
                    key_snippets = self._extract_key_snippets(body)
                    
                    sample_notes[md_file.name] = {
                        "content": body[:500],  # First 500 chars for analysis
                        "full_content": body,
                        "key_snippets": key_snippets,  # For feedback display
                        "concepts": concepts,
                        "domain": domain,
                        "directory": directory,
                        "tags": frontmatter.get("tags", []),
                        "file_path": str(md_file),
                        "created": frontmatter.get("created", "unknown"),
                        "word_count": len(body.split())
                    }
                    
                    notes_loaded += 1
                    print(f"  ✅ {md_file.name} ({domain}, {len(concepts)} concepts)")
                    
                except Exception as e:
                    print(f"  ⚠️ Skipped {md_file.name}: {e}")
                    continue
        
        self.feedback_data["session_info"]["notes_analyzed"] = len(sample_notes)
        print(f"\n📊 Loaded {len(sample_notes)} notes for connection analysis")
        return sample_notes
    
    def _extract_concepts(self, frontmatter: Dict, content: str) -> List[str]:
        """Extract key concepts with enhanced detection"""
        concepts = []
        
        # Add tags as concepts
        if "tags" in frontmatter:
            concepts.extend(frontmatter["tags"])
        
        # Enhanced key term detection
        key_terms = [
            # AI/Technology
            "machine learning", "deep learning", "neural networks", "AI", "algorithm",
            "automation", "system", "processing", "data", "analysis",
            # Knowledge Management  
            "zettelkasten", "knowledge management", "note taking", "notes",
            "workflow", "productivity", "capture", "triage", "connection",
            # Business/Strategy
            "strategy", "revenue", "business", "consulting", "productivity",
            "evidence-based", "methodology", "pattern", "framework"
        ]
        
        content_lower = content.lower()
        for term in key_terms:
            if term in content_lower:
                concepts.append(term)
        
        return list(set(concepts))  # Remove duplicates
    
    def _determine_domain(self, directory: str, frontmatter: Dict, content: str) -> str:
        """Enhanced domain detection"""
        content_lower = content.lower()
        
        # Technology domain indicators
        tech_keywords = ["ai", "machine learning", "algorithm", "code", "system", "automation", "processing"]
        if any(keyword in content_lower for keyword in tech_keywords):
            return "technology"
        
        # Knowledge management domain
        km_keywords = ["zettelkasten", "notes", "knowledge", "capture", "workflow", "triage", "connection"]
        if any(keyword in content_lower for keyword in km_keywords):
            return "knowledge_management"
        
        # Business/strategy domain
        business_keywords = ["revenue", "business", "strategy", "consulting", "productivity"]
        if any(keyword in content_lower for keyword in business_keywords):
            return "business"
        
        # Directory-based classification
        if "Projects" in directory:
            return "projects"
        elif "Literature" in directory:
            return "literature"
        elif "Fleeting" in directory:
            return "ideas"
        else:
            return "general"
    
    def _extract_key_snippets(self, content: str, max_snippets: int = 3) -> List[str]:
        """Extract key text snippets that represent main concepts"""
        sentences = content.split('. ')
        
        # Filter for sentences with key indicators
        key_indicators = ["is", "are", "means", "involves", "requires", "enables", "creates", "provides"]
        key_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # Reasonable length
                if any(indicator in sentence.lower() for indicator in key_indicators):
                    key_sentences.append(sentence)
        
        # Return first few key sentences or fall back to first sentences
        if key_sentences:
            return key_sentences[:max_snippets]
        else:
            return [s.strip() for s in sentences[:max_snippets] if len(s.strip()) > 20]
    
    def collect_relationship_feedback_data(self, notes: Dict[str, Dict]) -> None:
        """Collect detailed relationship detection data"""
        print("\n🔍 Collecting Relationship Detection Data...")
        
        note_pairs = list(notes.items())
        
        # Analyze first few pairs for detailed feedback
        for i in range(min(4, len(note_pairs))):
            for j in range(i+1, min(i+3, len(note_pairs))):
                note1_name, note1_data = note_pairs[i]
                note2_name, note2_data = note_pairs[j]
                
                print(f"  📊 Analyzing: {note1_name[:25]}... ↔ {note2_name[:25]}...")
                
                start_time = time.time()
                result = self.engine.detect_relationship_type(
                    note1_data["content"], 
                    note2_data["content"]
                )
                duration = time.time() - start_time
                
                # Collect comprehensive feedback data
                feedback_item = {
                    "connection_id": f"rel_{i}_{j}",
                    "connection_type": "relationship_detection",
                    "note1": {
                        "name": note1_name,
                        "domain": note1_data["domain"],
                        "concepts": note1_data["concepts"][:5],  # Top 5 concepts
                        "key_snippet": note1_data["key_snippets"][0] if note1_data["key_snippets"] else note1_data["content"][:100]
                    },
                    "note2": {
                        "name": note2_name,
                        "domain": note2_data["domain"],
                        "concepts": note2_data["concepts"][:5],
                        "key_snippet": note2_data["key_snippets"][0] if note2_data["key_snippets"] else note2_data["content"][:100]
                    },
                    "ai_prediction": {
                        "relationship_type": result["relationship_type"],
                        "confidence": result["confidence"],
                        "explanation": result["explanation"],
                        "processing_time": duration
                    },
                    "feedback_collected": False,
                    "user_feedback": None,
                    "feedback_timestamp": None
                }
                
                self.feedback_data["relationship_connections"].append(feedback_item)
                print(f"    ✅ {result['relationship_type']} (confidence: {result['confidence']:.2f})")
    
    def collect_strength_feedback_data(self, notes: Dict[str, Dict]) -> None:
        """Collect detailed connection strength data"""
        print("\n💪 Collecting Connection Strength Data...")
        
        # Extract unique concepts
        all_concepts = []
        for note_data in notes.values():
            all_concepts.extend(note_data["concepts"])
        unique_concepts = list(set(all_concepts))
        
        print(f"  📋 Analyzing {len(unique_concepts)} unique concepts...")
        
        # Test strength between top concept pairs
        for i in range(min(6, len(unique_concepts))):
            for j in range(i+1, min(i+3, len(unique_concepts))):
                concept1 = unique_concepts[i]
                concept2 = unique_concepts[j]
                
                print(f"  🔗 Testing: '{concept1}' ↔ '{concept2}'")
                
                start_time = time.time()
                result = self.engine.calculate_connection_strength(concept1, concept2)
                duration = time.time() - start_time
                
                # Collect detailed strength data
                feedback_item = {
                    "connection_id": f"strength_{i}_{j}",
                    "connection_type": "strength_calculation",
                    "concept1": concept1,
                    "concept2": concept2,
                    "ai_prediction": {
                        "strength_score": result["strength_score"],
                        "confidence_interval_width": result["confidence_interval_width"],
                        "confidence_lower": result.get("confidence_lower", 0),
                        "confidence_upper": result.get("confidence_upper", 1),
                        "components": result.get("components", {}),
                        "processing_time": duration
                    },
                    "feedback_collected": False,
                    "user_feedback": None,
                    "feedback_timestamp": None
                }
                
                self.feedback_data["strength_connections"].append(feedback_item)
                print(f"    📊 Strength: {result['strength_score']:.3f} (±{result['confidence_interval_width']:.3f})")
    
    def collect_cross_domain_feedback_data(self, notes: Dict[str, Dict]) -> None:
        """Collect cross-domain connection data"""
        print("\n🌐 Collecting Cross-Domain Connection Data...")
        
        start_time = time.time()
        connections = self.engine.discover_cross_domain_connections(notes)
        duration = time.time() - start_time
        
        print(f"  📊 Found {len(connections)} cross-domain connections in {duration:.3f}s")
        
        # Collect detailed cross-domain data
        for i, connection in enumerate(connections[:5]):  # Top 5 connections
            feedback_item = {
                "connection_id": f"cross_domain_{i}",
                "connection_type": "cross_domain_discovery",
                "source_note": connection.get("source_note", "unknown"),
                "target_note": connection.get("target_note", "unknown"),
                "ai_prediction": {
                    "source_domain": connection.get("source_domain", "unknown"),
                    "target_domain": connection.get("target_domain", "unknown"),
                    "shared_concept": connection.get("shared_concept", "unknown"),
                    "analogy_strength": connection.get("analogy_strength", 0),
                    "explanation": connection.get("explanation", "No explanation provided"),
                    "processing_time": duration / len(connections) if connections else 0
                },
                "feedback_collected": False,
                "user_feedback": None,
                "feedback_timestamp": None
            }
            
            self.feedback_data["cross_domain_connections"].append(feedback_item)
            print(f"    🔗 {connection.get('source_note', 'Unknown')[:20]}... ↔ {connection.get('target_note', 'Unknown')[:20]}...")
            print(f"       Strength: {connection.get('analogy_strength', 0):.3f}")
    
    def export_feedback_data(self, export_format: str = "markdown") -> str:
        """Export collected data for user feedback"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format == "json":
            filename = f"connection_feedback_data_{timestamp}.json"
            filepath = self.vault_path / "development" / "feedback" / filename
        else:
            filename = f"connection_feedback_review_{timestamp}.md"
            filepath = self.vault_path / "development" / "feedback" / filename
        
        # Ensure feedback directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        if export_format == "json":
            with open(filepath, 'w') as f:
                json.dump(self.feedback_data, f, indent=2)
        else:
            self._export_markdown_review(filepath)
        
        return str(filepath)
    
    def _export_markdown_review(self, filepath: Path) -> None:
        """Export comprehensive markdown review file"""
        content = []
        
        # Header
        content.append("# Enhanced Connection Discovery - Feedback Review")
        content.append(f"**Generated**: {self.feedback_data['session_info']['timestamp']}")
        content.append(f"**Notes Analyzed**: {self.feedback_data['session_info']['notes_analyzed']}")
        content.append(f"**Total Connections**: {len(self.feedback_data['relationship_connections']) + len(self.feedback_data['strength_connections']) + len(self.feedback_data['cross_domain_connections'])}")
        content.append("")
        content.append("## 📋 Instructions")
        content.append("For each connection below, add your feedback:")
        content.append("- ✅ **ACCEPT** - Connection is accurate and useful")
        content.append("- ❌ **REJECT** - Connection is incorrect or not useful")
        content.append("- 💬 **COMMENT** - Optional explanation of your decision")
        content.append("")
        
        # Relationship Connections
        if self.feedback_data["relationship_connections"]:
            content.append("## 🔍 Relationship Detection Connections")
            content.append("")
            
            for i, conn in enumerate(self.feedback_data["relationship_connections"]):
                content.append(f"### Connection {i+1}: Relationship Detection")
                content.append(f"**ID**: `{conn['connection_id']}`")
                content.append("")
                content.append(f"**Note 1**: {conn['note1']['name']}")
                content.append(f"- Domain: {conn['note1']['domain']}")
                content.append(f"- Key Concepts: {', '.join(conn['note1']['concepts'])}")
                content.append(f"- Key Text: \"{conn['note1']['key_snippet']}\"")
                content.append("")
                content.append(f"**Note 2**: {conn['note2']['name']}")
                content.append(f"- Domain: {conn['note2']['domain']}")
                content.append(f"- Key Concepts: {', '.join(conn['note2']['concepts'])}")
                content.append(f"- Key Text: \"{conn['note2']['key_snippet']}\"")
                content.append("")
                content.append(f"**AI Prediction**:")
                content.append(f"- Relationship Type: **{conn['ai_prediction']['relationship_type']}**")
                content.append(f"- Confidence: {conn['ai_prediction']['confidence']:.2f}")
                content.append(f"- Explanation: {conn['ai_prediction']['explanation']}")
                content.append(f"- Processing Time: {conn['ai_prediction']['processing_time']:.3f}s")
                content.append("")
                content.append("**Your Feedback**:")
                content.append("- [ ] ✅ ACCEPT - This relationship detection is correct")
                content.append("- [ ] ❌ REJECT - This relationship detection is incorrect")
                content.append("- 💬 Comments: _[Your feedback here]_")
                content.append("")
                content.append("---")
                content.append("")
        
        # Connection Strength
        if self.feedback_data["strength_connections"]:
            content.append("## 💪 Connection Strength Calculations")
            content.append("")
            
            for i, conn in enumerate(self.feedback_data["strength_connections"]):
                content.append(f"### Connection {i+1}: Strength Calculation")
                content.append(f"**ID**: `{conn['connection_id']}`")
                content.append("")
                content.append(f"**Concepts**: '{conn['concept1']}' ↔ '{conn['concept2']}'")
                content.append("")
                content.append(f"**AI Prediction**:")
                content.append(f"- Strength Score: **{conn['ai_prediction']['strength_score']:.3f}**")
                content.append(f"- Confidence Interval: ±{conn['ai_prediction']['confidence_interval_width']:.3f}")
                content.append(f"- Range: {conn['ai_prediction']['confidence_lower']:.3f} - {conn['ai_prediction']['confidence_upper']:.3f}")
                content.append(f"- Processing Time: {conn['ai_prediction']['processing_time']:.3f}s")
                content.append("")
                content.append("**Your Feedback**:")
                content.append("- [ ] ✅ ACCEPT - This strength calculation seems reasonable")
                content.append("- [ ] ❌ REJECT - This strength calculation seems wrong")
                content.append("- 💬 Comments: _[Your feedback here]_")
                content.append("")
                content.append("---")
                content.append("")
        
        # Cross-Domain Connections
        if self.feedback_data["cross_domain_connections"]:
            content.append("## 🌐 Cross-Domain Connections")
            content.append("")
            
            for i, conn in enumerate(self.feedback_data["cross_domain_connections"]):
                content.append(f"### Connection {i+1}: Cross-Domain Discovery")
                content.append(f"**ID**: `{conn['connection_id']}`")
                content.append("")
                content.append(f"**Source Note**: {conn['source_note']}")
                content.append(f"**Target Note**: {conn['target_note']}")
                content.append("")
                content.append(f"**AI Prediction**:")
                content.append(f"- Source Domain: {conn['ai_prediction']['source_domain']}")
                content.append(f"- Target Domain: {conn['ai_prediction']['target_domain']}")
                content.append(f"- Shared Concept: **{conn['ai_prediction']['shared_concept']}**")
                content.append(f"- Analogy Strength: {conn['ai_prediction']['analogy_strength']:.3f}")
                content.append(f"- Explanation: {conn['ai_prediction']['explanation']}")
                content.append("")
                content.append("**Your Feedback**:")
                content.append("- [ ] ✅ ACCEPT - This cross-domain connection is meaningful")
                content.append("- [ ] ❌ REJECT - This cross-domain connection is not useful")
                content.append("- 💬 Comments: _[Your feedback here]_")
                content.append("")
                content.append("---")
                content.append("")
        
        # Summary
        content.append("## 📊 Feedback Summary")
        content.append("After reviewing all connections, please provide overall feedback:")
        content.append("")
        content.append("### Overall Assessment")
        content.append("- **Most Accurate Feature**: _[Relationship Detection / Strength Calculation / Cross-Domain Discovery]_")
        content.append("- **Needs Most Improvement**: _[Feature that needs work]_")
        content.append("- **Confidence in AI Predictions**: _[High / Medium / Low]_")
        content.append("- **Would Use in Weekly Review**: _[Yes / No / Maybe]_")
        content.append("")
        content.append("### Suggestions for Improvement")
        content.append("- _[Your suggestions here]_")
        content.append("")
        content.append("---")
        content.append("")
        content.append("**Thank you for your feedback! This data will help improve the Enhanced Connection Discovery System.**")
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(content))
    
    def run_feedback_collection(self, max_notes: int = 8):
        """Run complete feedback data collection"""
        print("🔄 Enhanced Connection Discovery - Feedback Collection")
        print("=" * 60)
        
        # Load notes
        notes = self.load_sample_notes(max_notes=max_notes)
        if not notes:
            print("❌ No notes loaded for analysis")
            return None
        
        # Collect all types of feedback data
        self.collect_relationship_feedback_data(notes)
        self.collect_strength_feedback_data(notes)
        self.collect_cross_domain_feedback_data(notes)
        
        # Update session stats
        total_connections = (len(self.feedback_data["relationship_connections"]) + 
                           len(self.feedback_data["strength_connections"]) + 
                           len(self.feedback_data["cross_domain_connections"]))
        
        self.feedback_data["session_info"]["connections_found"] = total_connections
        
        # Export for review
        markdown_file = self.export_feedback_data("markdown")
        json_file = self.export_feedback_data("json")
        
        print("\n" + "=" * 60)
        print("✅ FEEDBACK COLLECTION COMPLETE")
        print("=" * 60)
        print(f"📊 Total Connections Analyzed: {total_connections}")
        print(f"🔍 Relationship Connections: {len(self.feedback_data['relationship_connections'])}")
        print(f"💪 Strength Connections: {len(self.feedback_data['strength_connections'])}")
        print(f"🌐 Cross-Domain Connections: {len(self.feedback_data['cross_domain_connections'])}")
        print("")
        print("📁 Feedback Files Generated:")
        print(f"  📋 Review File: {markdown_file}")
        print(f"  💾 Data File: {json_file}")
        print("")
        print("🎯 Next Steps:")
        print("  1. Open the markdown review file")
        print("  2. Add ✅ ACCEPT or ❌ REJECT for each connection")
        print("  3. Add comments explaining your decisions")
        print("  4. Use feedback to improve the system")
        
        return {
            "markdown_file": markdown_file,
            "json_file": json_file,
            "total_connections": total_connections,
            "session_data": self.feedback_data
        }


def main():
    """Main execution function"""
    # Detect vault path
    current_dir = Path(__file__).parent
    vault_path = current_dir.parent.parent
    
    print(f"🏠 Vault Path: {vault_path}")
    
    # Initialize and run collector
    collector = ConnectionFeedbackCollector(str(vault_path))
    results = collector.run_feedback_collection(max_notes=8)
    
    if results:
        print(f"\n🚀 Feedback collection successful!")
        print(f"📋 Review your connections at: {results['markdown_file']}")


if __name__ == "__main__":
    main()
