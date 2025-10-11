#!/usr/bin/env python3
"""
Safe Workflow Formatter - Display formatting for safe workflow reports

Extracted from safe_workflow_cli.py to maintain single responsibility and keep CLI under 400 LOC.
Handles all display formatting for safe workflow operations.
"""

from pathlib import Path
from typing import Dict, Any


class SafeWorkflowFormatter:
    """
    Formatter for safe workflow operation reports
    
    Responsibilities:
    - Format processing results for console display
    - Format reports to markdown for export
    - Consistent section formatting
    """
    
    def format_process_inbox_result(self, result: Dict[str, Any]) -> str:
        """
        Format inbox processing result for console display.
        
        Args:
            result: Processing result dictionary
            
        Returns:
            Formatted string for console output
        """
        lines = []
        
        if result.get("success"):
            processing_result = result.get("result", {})
            lines.append(f"   ✅ Processed: {processing_result.get('successful_notes', 0)}/{processing_result.get('total_notes', 0)} notes")
            lines.append(f"   🖼️ Images preserved: {processing_result.get('total_images_preserved', 0)}")
        else:
            lines.append(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        return "\n".join(lines)
    
    def format_batch_process_result(self, result: Dict[str, Any]) -> str:
        """
        Format batch processing result for console display.
        
        Args:
            result: Batch processing result dictionary
            
        Returns:
            Formatted string for console output
        """
        lines = []
        
        if result.get("success"):
            batch_result = result.get("result", {})
            lines.append(f"   ✅ Total files processed: {batch_result.get('total_files', 0)}")
            lines.append(f"   🖼️ Images preserved: {batch_result.get('images_preserved_total', 0)}")
        else:
            lines.append(f"   ❌ Error: {result.get('error', 'Unknown error')}")
        
        return "\n".join(lines)
    
    def format_performance_report(self, result: Dict[str, Any]) -> str:
        """
        Format performance report for console display.
        
        Args:
            result: Performance report dictionary
            
        Returns:
            Formatted string for console output
        """
        if result.get("success"):
            return result.get("result", "Report generated successfully")
        else:
            return f"   ❌ Error: {result.get('error', 'Unknown error')}"
    
    def format_integrity_report(self, result: Dict[str, Any]) -> str:
        """
        Format integrity report for console display.
        
        Args:
            result: Integrity report dictionary
            
        Returns:
            Formatted string for console output
        """
        if result.get("success"):
            return result.get("result", "Report generated successfully")
        else:
            return f"   ❌ Error: {result.get('error', 'Unknown error')}"
    
    def format_backup_created(self, result: Dict[str, Any]) -> str:
        """
        Format backup creation result for console display.
        
        Args:
            result: Backup result dictionary
            
        Returns:
            Formatted string for console output
        """
        lines = []
        lines.append(f"   ✅ Backup successful")
        lines.append(f"   📂 Location: {result.get('backup_path', 'Unknown')}")
        return "\n".join(lines)
    
    def format_backup_list(self, result: Dict[str, Any]) -> str:
        """
        Format backup list for console display.
        
        Args:
            result: Backup list dictionary
            
        Returns:
            Formatted string for console output
        """
        lines = []
        backups = result.get("backups", [])
        
        if backups:
            lines.append(f"   📁 Found {len(backups)} backup(s):\n")
            for i, backup in enumerate(backups, 1):
                lines.append(f"   {i:2d}. {backup['name']}")
                lines.append(f"       📂 Path: {backup['path']}\n")
        else:
            lines.append("   📁 No backups found")
        
        return "\n".join(lines)
