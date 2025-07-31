"""
Smart workflow manager that integrates AI features into the Zettelkasten workflow.
Follows the established patterns from the project manifest.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

from .tagger import AITagger
from .summarizer import AISummarizer
from .connections import AIConnections
from .enhancer import AIEnhancer
from .analytics import NoteAnalytics


class WorkflowManager:
    """Manages the complete AI-enhanced Zettelkasten workflow."""
    
    def __init__(self, base_directory: str):
        """
        Initialize workflow manager.
        
        Args:
            base_directory: Root directory of the Zettelkasten
        """
        self.base_dir = Path(base_directory)
        
        # Define workflow directories
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"
        
        # Initialize AI components
        self.tagger = AITagger()
        self.summarizer = AISummarizer()
        self.connections = AIConnections()
        self.enhancer = AIEnhancer()
        self.analytics = NoteAnalytics(str(self.base_dir))
        
        # Workflow configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load workflow configuration."""
        config_file = self.base_dir / ".ai_workflow_config.json"
        
        default_config = {
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "auto_enhance_permanent_notes": False,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7,
            "archive_after_days": 90
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass
        
        return default_config
    
    def process_inbox_note(self, note_path: str) -> Dict:
        """
        Process a note in the inbox with AI assistance.
        
        Args:
            note_path: Path to the note in inbox
            
        Returns:
            Processing results and recommendations
        """
        note_file = Path(note_path)
        
        if not note_file.exists():
            return {"error": "Note file not found"}
        
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read note: {e}"}
        
        results = {
            "original_file": str(note_file),
            "processing": {},
            "recommendations": []
        }
        
        # Extract frontmatter and body
        frontmatter, body = self._extract_frontmatter(content)
        
        # Auto-tag if enabled
        if self.config["auto_tag_inbox"]:
            try:
                suggested_tags = self.tagger.generate_tags(content)
                existing_tags = frontmatter.get("tags", [])
                
                # Merge tags intelligently
                merged_tags = self._merge_tags(existing_tags, suggested_tags)
                
                if merged_tags != existing_tags:
                    frontmatter["tags"] = merged_tags
                    results["processing"]["tags"] = {
                        "added": list(set(merged_tags) - set(existing_tags)),
                        "total": len(merged_tags)
                    }
            except Exception as e:
                results["processing"]["tags"] = {"error": str(e)}
        
        # Analyze note quality and suggest improvements
        try:
            enhancement = self.enhancer.enhance_note(content)
            quality_score = enhancement.get("quality_score", 0)
            
            results["processing"]["quality"] = {
                "score": quality_score,
                "suggestions": enhancement.get("suggestions", [])[:3]
            }
            
            # Generate workflow recommendations based on quality
            if quality_score > 0.7:
                results["recommendations"].append({
                    "action": "promote_to_permanent",
                    "reason": "High quality content suitable for permanent notes",
                    "confidence": "high"
                })
            elif quality_score > 0.4:
                results["recommendations"].append({
                    "action": "move_to_fleeting",
                    "reason": "Medium quality content needs development",
                    "confidence": "medium"
                })
            else:
                results["recommendations"].append({
                    "action": "improve_or_archive",
                    "reason": "Low quality content needs significant improvement",
                    "confidence": "high"
                })
        except Exception as e:
            results["processing"]["quality"] = {"error": str(e)}
        
        # Find potential connections
        try:
            # Load existing permanent notes for connection analysis
            permanent_notes = self._load_notes_corpus(self.permanent_dir)
            
            if permanent_notes:
                similar_notes = self.connections.find_similar_notes(content, permanent_notes)
                
                if similar_notes:
                    results["processing"]["connections"] = {
                        "similar_notes": [
                            {"file": filename, "similarity": float(score)}
                            for filename, score in similar_notes[:3]
                        ]
                    }
                    
                    results["recommendations"].append({
                        "action": "add_links",
                        "reason": f"Found {len(similar_notes)} related notes",
                        "details": similar_notes[:3]
                    })
        except Exception as e:
            results["processing"]["connections"] = {"error": str(e)}
        
        # Update note with AI enhancements
        if any(key in results["processing"] for key in ["tags", "quality"]):
            try:
                # Update status to indicate AI processing
                frontmatter["ai_processed"] = datetime.now().isoformat()
                
                # Rebuild content
                updated_content = self._rebuild_content(frontmatter, body)
                
                with open(note_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                results["file_updated"] = True
            except Exception as e:
                results["file_update_error"] = str(e)
        
        return results
    
    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to permanent notes.
        
        Args:
            note_path: Path to the note to promote
            target_type: Target note type ("permanent" or "fleeting")
            
        Returns:
            Promotion results
        """
        source_file = Path(note_path)
        
        if not source_file.exists():
            return {"error": "Source note not found"}
        
        # Determine target directory
        if target_type == "permanent":
            target_dir = self.permanent_dir
        elif target_type == "fleeting":
            target_dir = self.fleeting_dir
        else:
            return {"error": f"Invalid target type: {target_type}"}
        
        target_dir.mkdir(exist_ok=True)
        target_file = target_dir / source_file.name
        
        try:
            # Read and update content
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, body = self._extract_frontmatter(content)
            
            # Update metadata for promotion
            frontmatter["type"] = target_type
            frontmatter["status"] = "promoted" if target_type == "permanent" else "draft"
            frontmatter["promoted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Add AI summary for long permanent notes
            if (target_type == "permanent" and 
                self.config["auto_summarize_long_notes"] and
                self.summarizer.should_summarize(content)):
                
                try:
                    summary = self.summarizer.generate_summary(content)
                    if summary:
                        frontmatter["ai_summary"] = summary
                except Exception:
                    pass  # Don't fail promotion if summary fails
            
            # Rebuild and save to target location
            updated_content = self._rebuild_content(frontmatter, body)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            # Remove from source location
            source_file.unlink()
            
            return {
                "success": True,
                "source": str(source_file),
                "target": str(target_file),
                "type": target_type,
                "has_summary": "ai_summary" in frontmatter
            }
            
        except Exception as e:
            return {"error": f"Failed to promote note: {e}"}
    
    def batch_process_inbox(self) -> Dict:
        """Process all notes in the inbox."""
        inbox_files = list(self.inbox_dir.glob("*.md"))
        
        results = {
            "total_files": len(inbox_files),
            "processed": 0,
            "failed": 0,
            "results": [],
            "summary": {
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0
            }
        }
        
        for note_file in inbox_files:
            try:
                result = self.process_inbox_note(str(note_file))
                
                if "error" not in result:
                    results["processed"] += 1
                    
                    # Categorize recommendations
                    for rec in result.get("recommendations", []):
                        action = rec.get("action", "")
                        if action == "promote_to_permanent":
                            results["summary"]["promote_to_permanent"] += 1
                        elif action == "move_to_fleeting":
                            results["summary"]["move_to_fleeting"] += 1
                        elif action == "improve_or_archive":
                            results["summary"]["needs_improvement"] += 1
                else:
                    results["failed"] += 1
                
                results["results"].append(result)
                
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "original_file": str(note_file),
                    "error": str(e)
                })
        
        return results
    
    def generate_workflow_report(self) -> Dict:
        """Generate a comprehensive workflow status report."""
        # Get analytics for the entire collection
        analytics_report = self.analytics.generate_report()
        
        # Count notes by directory
        directory_counts = {}
        for dir_name, dir_path in [
            ("Inbox", self.inbox_dir),
            ("Fleeting Notes", self.fleeting_dir),
            ("Permanent Notes", self.permanent_dir),
            ("Archive", self.archive_dir)
        ]:
            if dir_path.exists():
                directory_counts[dir_name] = len(list(dir_path.glob("*.md")))
            else:
                directory_counts[dir_name] = 0
        
        # Workflow health metrics
        inbox_count = directory_counts["Inbox"]
        fleeting_count = directory_counts["Fleeting Notes"]
        permanent_count = directory_counts["Permanent Notes"]
        
        workflow_health = "healthy"
        if inbox_count > 20:
            workflow_health = "needs_attention"
        elif inbox_count > 50:
            workflow_health = "critical"
        
        # AI feature usage
        ai_usage = self._analyze_ai_usage()
        
        return {
            "workflow_status": {
                "health": workflow_health,
                "directory_counts": directory_counts,
                "total_notes": sum(directory_counts.values())
            },
            "ai_features": ai_usage,
            "analytics": analytics_report,
            "recommendations": self._generate_workflow_recommendations(
                directory_counts, ai_usage
            )
        }
    
    def _analyze_ai_usage(self) -> Dict:
        """Analyze usage of AI features across the collection."""
        usage_stats = {
            "notes_with_ai_tags": 0,
            "notes_with_ai_summaries": 0,
            "notes_with_ai_processing": 0,
            "total_analyzed": 0
        }
        
        # Scan all notes for AI features
        for md_file in self.base_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, _ = self._extract_frontmatter(content)
                usage_stats["total_analyzed"] += 1
                
                if "ai_summary" in frontmatter:
                    usage_stats["notes_with_ai_summaries"] += 1
                
                if "ai_processed" in frontmatter:
                    usage_stats["notes_with_ai_processing"] += 1
                
                # Check if tags were likely AI-generated (heuristic)
                tags = frontmatter.get("tags", [])
                if isinstance(tags, list) and len(tags) >= 3:
                    # Look for AI-style kebab-case tags
                    ai_style_tags = [t for t in tags if '-' in t and len(t) > 5]
                    if len(ai_style_tags) >= 2:
                        usage_stats["notes_with_ai_tags"] += 1
                
            except Exception:
                continue
        
        return usage_stats
    
    def _generate_workflow_recommendations(self, directory_counts: Dict, 
                                         ai_usage: Dict) -> List[str]:
        """Generate workflow improvement recommendations."""
        recommendations = []
        
        # Inbox management
        inbox_count = directory_counts.get("Inbox", 0)
        if inbox_count > 20:
            recommendations.append(
                f"Process {inbox_count} notes in inbox - consider batch processing"
            )
        
        # AI feature adoption
        total_notes = ai_usage.get("total_analyzed", 0)
        if total_notes > 0:
            ai_summary_rate = ai_usage["notes_with_ai_summaries"] / total_notes
            if ai_summary_rate < 0.3:
                recommendations.append(
                    "Consider enabling auto-summarization for long notes"
                )
            
            ai_processing_rate = ai_usage["notes_with_ai_processing"] / total_notes
            if ai_processing_rate < 0.5:
                recommendations.append(
                    "Enable AI processing for inbox notes to improve workflow efficiency"
                )
        
        # Balance between note types
        permanent_count = directory_counts.get("Permanent Notes", 0)
        fleeting_count = directory_counts.get("Fleeting Notes", 0)
        
        if fleeting_count > permanent_count * 2:
            recommendations.append(
                "Consider promoting more fleeting notes to permanent status"
            )
        
        return recommendations
    
    def _load_notes_corpus(self, directory: Path) -> Dict[str, str]:
        """Load all notes from a directory into a corpus."""
        corpus = {}
        
        if not directory.exists():
            return corpus
        
        for md_file in directory.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    corpus[md_file.name] = f.read()
            except Exception:
                continue
        
        return corpus
    
    def _extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and body content."""
        yaml_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(yaml_pattern, content, re.DOTALL)
        
        if match:
            yaml_content = match.group(1)
            body = match.group(2)
            
            frontmatter = {}
            for line in yaml_content.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if value.startswith('[') and value.endswith(']'):
                        items = value[1:-1].split(',')
                        frontmatter[key] = [item.strip().strip('"\'') for item in items if item.strip()]
                    else:
                        frontmatter[key] = value.strip('"\'')
            
            return frontmatter, body
        
        return {}, content
    
    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """Merge existing and new tags intelligently."""
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()
        
        merged = sorted(list(existing_set | new_set))
        return merged[:self.config["max_tags_per_note"]]
    
    def _rebuild_content(self, frontmatter: Dict, body: str) -> str:
        """Rebuild content with updated frontmatter."""
        if not frontmatter:
            return body
        
        yaml_lines = ["---"]
        
        # Preserve field order
        field_order = ["type", "created", "status", "tags", "ai_summary", "ai_processed"]
        
        for field in field_order:
            if field in frontmatter:
                value = frontmatter[field]
                if isinstance(value, list):
                    if value:
                        formatted_list = "[" + ", ".join(f'"{item}"' for item in value) + "]"
                        yaml_lines.append(f"{field}: {formatted_list}")
                else:
                    yaml_lines.append(f"{field}: {value}")
        
        # Add remaining fields
        for key, value in frontmatter.items():
            if key not in field_order:
                if isinstance(value, list):
                    if value:
                        formatted_list = "[" + ", ".join(f'"{item}"' for item in value) + "]"
                        yaml_lines.append(f"{key}: {formatted_list}")
                else:
                    yaml_lines.append(f"{key}: {value}")
        
        yaml_lines.extend(["---", ""])
        return "\n".join(yaml_lines) + body
    
    def scan_review_candidates(self) -> List[Dict]:
        """Scan for notes that need weekly review attention.
        
        Finds all notes that require review:
        - All .md files in Inbox/ directory (regardless of status)
        - Files in Fleeting Notes/ directory with status: inbox
        
        Returns:
            List of candidate dictionaries with:
                - path: Path object to the note file
                - source: "inbox" or "fleeting" indicating origin
                - metadata: Parsed YAML frontmatter (empty dict if invalid)
        """
        candidates = []
        
        # Scan inbox directory - all .md files are candidates
        candidates.extend(self._scan_directory_for_candidates(
            self.inbox_dir, 
            source_type="inbox", 
            filter_func=None  # All inbox files are candidates
        ))
        
        # Scan fleeting notes directory - only notes with status: inbox
        candidates.extend(self._scan_directory_for_candidates(
            self.fleeting_dir,
            source_type="fleeting",
            filter_func=lambda metadata: metadata.get("status") == "inbox"
        ))
        
        return candidates
    
    def _scan_directory_for_candidates(self, directory: Path, source_type: str, 
                                     filter_func: Optional[callable] = None) -> List[Dict]:
        """Helper method to scan a directory for review candidates.
        
        Args:
            directory: Path to scan
            source_type: Type identifier ("inbox" or "fleeting")
            filter_func: Optional function to filter candidates based on metadata
            
        Returns:
            List of candidate dictionaries
        """
        candidates = []
        
        if not directory.exists():
            return candidates
            
        try:
            for note_path in directory.glob("*.md"):
                try:
                    candidate = self._create_candidate_dict(note_path, source_type)
                    
                    # Apply filter if provided
                    if filter_func is None or filter_func(candidate["metadata"]):
                        candidates.append(candidate)
                        
                except Exception as e:
                    # Log error but continue processing other files
                    # For now, include problematic files with empty metadata
                    candidates.append({
                        "path": note_path,
                        "source": source_type,
                        "metadata": {},
                        "error": str(e)
                    })
        except Exception:
            # Handle directory access errors gracefully
            pass
            
        return candidates
    
    def _create_candidate_dict(self, note_path: Path, source_type: str) -> Dict:
        """Create a candidate dictionary from a note file.
        
        Args:
            note_path: Path to the note file
            source_type: Source type ("inbox" or "fleeting")
            
        Returns:
            Dictionary with path, source, and metadata
            
        Raises:
            Exception: If file cannot be read or processed
        """
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata, _ = self._extract_frontmatter(content)
        
        return {
            "path": note_path,
            "source": source_type,
            "metadata": metadata
        }


def main():
    """CLI entry point for workflow manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-enhanced Zettelkasten workflow manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process inbox
    process_parser = subparsers.add_parser("process-inbox", help="Process inbox notes")
    process_parser.add_argument("directory", help="Zettelkasten root directory")
    process_parser.add_argument("--batch", action="store_true", help="Process all inbox notes")
    
    # Promote note
    promote_parser = subparsers.add_parser("promote", help="Promote a note")
    promote_parser.add_argument("directory", help="Zettelkasten root directory")
    promote_parser.add_argument("note", help="Note file to promote")
    promote_parser.add_argument("--type", choices=["permanent", "fleeting"], 
                               default="permanent", help="Target note type")
    
    # Workflow report
    report_parser = subparsers.add_parser("report", help="Generate workflow report")
    report_parser.add_argument("directory", help="Zettelkasten root directory")
    report_parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    workflow = WorkflowManager(args.directory)
    
    if args.command == "process-inbox":
        if args.batch:
            print("📥 Processing all inbox notes...")
            result = workflow.batch_process_inbox()
            
            print(f"📊 Results:")
            print(f"   Total files: {result['total_files']}")
            print(f"   Processed: {result['processed']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Recommendations:")
            print(f"     Promote to permanent: {result['summary']['promote_to_permanent']}")
            print(f"     Move to fleeting: {result['summary']['move_to_fleeting']}")
            print(f"     Needs improvement: {result['summary']['needs_improvement']}")
        else:
            print("Use --batch flag to process all inbox notes")
    
    elif args.command == "promote":
        print(f"📈 Promoting note: {args.note}")
        result = workflow.promote_note(args.note, args.type)
        
        if result.get("success"):
            print(f"✅ Successfully promoted to {result['type']}")
            print(f"   From: {result['source']}")
            print(f"   To: {result['target']}")
            if result.get("has_summary"):
                print(f"   Added AI summary")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    elif args.command == "report":
        print("📊 Generating workflow report...")
        report = workflow.generate_workflow_report()
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📄 Report saved to: {args.output}")
        else:
            # Display summary
            status = report["workflow_status"]
            print(f"\n🏥 Workflow Health: {status['health'].upper()}")
            print(f"📁 Directory Counts:")
            for dir_name, count in status["directory_counts"].items():
                print(f"   {dir_name}: {count}")
            
            ai_features = report["ai_features"]
            total = ai_features["total_analyzed"]
            if total > 0:
                print(f"\n🤖 AI Feature Usage:")
                print(f"   Notes with AI summaries: {ai_features['notes_with_ai_summaries']}/{total}")
                print(f"   Notes with AI processing: {ai_features['notes_with_ai_processing']}/{total}")
                print(f"   Notes with AI tags: {ai_features['notes_with_ai_tags']}/{total}")
            
            recommendations = report.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")


if __name__ == "__main__":
    main()
