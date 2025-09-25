#!/usr/bin/env python3
"""
Image Integrity Utilities - Extracted Modular Architecture
REFACTOR Phase: Production-ready utility classes for image preservation
"""

import logging
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ImageTrackingInfo:
    """Structured information about tracked images"""
    path: Path
    context: str
    registered_at: str
    exists_at_registration: bool
    current_status: bool = True


@dataclass
class WorkflowCheckpoint:
    """Structured information about workflow checkpoints"""
    name: str
    timestamp: str
    tracked_images_count: int
    image_integrity: Dict[str, bool]


class ImageRegistrationManager:
    """Utility class for managing image registration and tracking"""
    
    def __init__(self):
        self.tracked_images: Dict[str, ImageTrackingInfo] = {}
        logger.debug("ImageRegistrationManager initialized")
    
    def register_image(self, image_path: Path, context: str) -> str:
        """Register an image for tracking with structured metadata"""
        image_key = str(image_path)
        tracking_info = ImageTrackingInfo(
            path=image_path,
            context=context,
            registered_at=datetime.now().isoformat(),
            exists_at_registration=image_path.exists(),
            current_status=image_path.exists()
        )
        
        self.tracked_images[image_key] = tracking_info
        logger.debug(f"Registered image {image_path} with context: {context}")
        return image_key
    
    def register_multiple_images(self, images: List[Path], context_prefix: str) -> List[str]:
        """Register multiple images with consistent context"""
        registered_keys = []
        for i, image in enumerate(images):
            context = f"{context_prefix}_{i}" if len(images) > 1 else context_prefix
            key = self.register_image(image, context)
            registered_keys.append(key)
        
        logger.debug(f"Registered {len(images)} images with context prefix: {context_prefix}")
        return registered_keys
    
    def update_image_status(self, image_key: str) -> bool:
        """Update current status of tracked image"""
        if image_key in self.tracked_images:
            tracking_info = self.tracked_images[image_key]
            tracking_info.current_status = tracking_info.path.exists()
            return tracking_info.current_status
        return False
    
    def get_missing_images(self) -> List[Path]:
        """Get list of images that no longer exist"""
        missing = []
        for key, info in self.tracked_images.items():
            self.update_image_status(key)
            if not info.current_status:
                missing.append(info.path)
        return missing


class WorkflowStepTracker:
    """Utility class for tracking workflow steps and checkpoints"""
    
    def __init__(self):
        self.workflow_steps: List[Dict] = []
        self.current_workflow: Optional[str] = None
        self.workflow_start_time: Optional[datetime] = None
        logger.debug("WorkflowStepTracker initialized")
    
    def start_workflow(self, workflow_name: str):
        """Start tracking a new workflow"""
        self.current_workflow = workflow_name
        self.workflow_start_time = datetime.now()
        
        step_info = {
            'step_type': 'workflow_start',
            'workflow_name': workflow_name,
            'timestamp': self.workflow_start_time.isoformat()
        }
        self.workflow_steps.append(step_info)
        logger.debug(f"Started tracking workflow: {workflow_name}")
    
    def track_step(self, step_name: str, images: List[Path]) -> Dict:
        """Track a workflow step with associated images"""
        step_info = {
            'step_type': 'processing_step',
            'step_name': step_name,
            'workflow': self.current_workflow or 'unknown',
            'timestamp': datetime.now().isoformat(),
            'images': [str(img) for img in images],
            'image_states': {str(img): img.exists() for img in images}
        }
        
        self.workflow_steps.append(step_info)
        logger.debug(f"Tracked workflow step: {step_name} with {len(images)} images")
        return step_info
    
    def create_checkpoint(self, checkpoint_name: str, registration_manager: 'ImageRegistrationManager') -> WorkflowCheckpoint:
        """Create a workflow checkpoint with current image integrity"""
        checkpoint = WorkflowCheckpoint(
            name=checkpoint_name,
            timestamp=datetime.now().isoformat(),
            tracked_images_count=len(registration_manager.tracked_images),
            image_integrity={key: info.path.exists() 
                           for key, info in registration_manager.tracked_images.items()}
        )
        
        checkpoint_info = {
            'step_type': 'checkpoint',
            'name': checkpoint_name,
            'timestamp': checkpoint.timestamp,
            'tracked_images_count': checkpoint.tracked_images_count,
            'image_integrity': checkpoint.image_integrity
        }
        
        self.workflow_steps.append(checkpoint_info)
        logger.debug(f"Created checkpoint: {checkpoint_name}")
        return checkpoint


class AuditReportGenerator:
    """Utility class for generating comprehensive audit reports"""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        logger.debug(f"AuditReportGenerator initialized for vault: {vault_path}")
    
    def generate_basic_report(self, registration_manager: 'ImageRegistrationManager', 
                            step_tracker: 'WorkflowStepTracker') -> Dict:
        """Generate basic audit report with current state"""
        report = {
            'vault_path': str(self.vault_path),
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_tracked_images': len(registration_manager.tracked_images),
                'workflow_steps': len(step_tracker.workflow_steps),
                'current_workflow': step_tracker.current_workflow,
                'missing_images': len(registration_manager.get_missing_images())
            },
            'tracked_images': {
                key: {
                    'path': str(info.path),
                    'context': info.context,
                    'registered_at': info.registered_at,
                    'exists_at_registration': info.exists_at_registration,
                    'current_status': info.current_status
                }
                for key, info in registration_manager.tracked_images.items()
            },
            'workflow_history': step_tracker.workflow_steps
        }
        
        logger.debug(f"Generated basic audit report with {len(registration_manager.tracked_images)} images")
        return report
    
    def generate_detailed_report(self, registration_manager: 'ImageRegistrationManager',
                               step_tracker: 'WorkflowStepTracker') -> Dict:
        """Generate detailed audit report with analysis"""
        basic_report = self.generate_basic_report(registration_manager, step_tracker)
        
        # Add detailed analysis
        missing_images = registration_manager.get_missing_images()
        integrity_analysis = self._analyze_integrity_trends(step_tracker.workflow_steps)
        
        detailed_report = {
            **basic_report,
            'analysis': {
                'integrity_score': 1.0 - (len(missing_images) / max(1, len(registration_manager.tracked_images))),
                'missing_images': [str(img) for img in missing_images],
                'integrity_trends': integrity_analysis,
                'risk_assessment': self._assess_risk_level(missing_images, registration_manager),
                'recommendations': self._generate_recommendations(missing_images, integrity_analysis)
            }
        }
        
        logger.debug("Generated detailed audit report with analysis")
        return detailed_report
    
    def _analyze_integrity_trends(self, workflow_steps: List[Dict]) -> Dict:
        """Analyze image integrity trends across workflow steps"""
        checkpoints = [step for step in workflow_steps if step.get('step_type') == 'checkpoint']
        
        if not checkpoints:
            return {'trend': 'insufficient_data', 'checkpoints_analyzed': 0}
        
        integrity_scores = []
        for checkpoint in checkpoints:
            image_integrity = checkpoint.get('image_integrity', {})
            if image_integrity:
                preserved_count = sum(1 for exists in image_integrity.values() if exists)
                total_count = len(image_integrity)
                score = preserved_count / max(1, total_count)
                integrity_scores.append(score)
        
        if len(integrity_scores) >= 2:
            trend = 'improving' if integrity_scores[-1] > integrity_scores[0] else 'degrading'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'checkpoints_analyzed': len(checkpoints),
            'integrity_scores': integrity_scores,
            'average_integrity': sum(integrity_scores) / max(1, len(integrity_scores))
        }
    
    def _assess_risk_level(self, missing_images: List[Path], 
                          registration_manager: 'ImageRegistrationManager') -> str:
        """Assess risk level based on missing images"""
        total_images = len(registration_manager.tracked_images)
        missing_count = len(missing_images)
        
        if total_images == 0:
            return 'unknown'
        
        missing_ratio = missing_count / total_images
        
        if missing_ratio == 0:
            return 'low'
        elif missing_ratio < 0.1:
            return 'moderate'
        elif missing_ratio < 0.25:
            return 'high'
        else:
            return 'critical'
    
    def _generate_recommendations(self, missing_images: List[Path], 
                                integrity_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        if missing_images:
            recommendations.append(f"Investigate {len(missing_images)} missing images immediately")
            recommendations.append("Review AI workflow processes for image handling")
            recommendations.append("Implement backup/recovery procedures for missing images")
        
        trend = integrity_analysis.get('trend', 'unknown')
        if trend == 'degrading':
            recommendations.append("Image integrity is degrading - review recent workflow changes")
        elif trend == 'improving':
            recommendations.append("Image integrity is improving - maintain current practices")
        
        if not recommendations:
            recommendations.append("Image integrity is stable - continue monitoring")
        
        return recommendations


class IntegrityValidationEngine:
    """Utility class for comprehensive integrity validation"""
    
    def __init__(self):
        logger.debug("IntegrityValidationEngine initialized")
    
    def validate_workflow_integrity(self, registration_manager: 'ImageRegistrationManager',
                                  step_tracker: 'WorkflowStepTracker') -> 'WorkflowIntegrityResult':
        """Perform comprehensive workflow integrity validation"""
        missing_images = registration_manager.get_missing_images()
        all_preserved = len(missing_images) == 0
        
        # Extract workflow step names for result
        workflow_steps = []
        for step in step_tracker.workflow_steps:
            if step.get('step_type') == 'checkpoint':
                workflow_steps.append(step.get('name', 'unnamed_checkpoint'))
            elif step.get('step_type') == 'processing_step':
                workflow_steps.append(step.get('step_name', 'unnamed_step'))
        
        # Create audit trail from checkpoints
        audit_trail = {}
        for step in step_tracker.workflow_steps:
            if step.get('step_type') == 'checkpoint':
                name = step.get('name', 'unnamed')
                timestamp = step.get('timestamp', '')
                audit_trail[name] = timestamp
        
        from .image_integrity_monitor import WorkflowIntegrityResult
        result = WorkflowIntegrityResult(
            all_images_preserved=all_preserved,
            missing_images=missing_images,
            workflow_steps=workflow_steps,
            audit_trail=audit_trail
        )
        
        logger.debug(f"Workflow integrity validation: preserved={all_preserved}, missing={len(missing_images)}")
        return result
    
    def validate_single_image(self, image_path: Path) -> bool:
        """Validate existence of a single image"""
        exists = image_path.exists()
        logger.debug(f"Single image validation {image_path}: {exists}")
        return exists
    
    def validate_image_set(self, images: List[Path]) -> Dict[str, bool]:
        """Validate existence of a set of images"""
        results = {str(img): img.exists() for img in images}
        missing_count = sum(1 for exists in results.values() if not exists)
        logger.debug(f"Image set validation: {len(images)} total, {missing_count} missing")
        return results


class PerformanceOptimizer:
    """Utility class for optimizing image integrity monitoring performance"""
    
    def __init__(self):
        self.cached_existence: Dict[str, tuple] = {}  # path -> (timestamp, exists)
        self.cache_duration = 5.0  # seconds
        logger.debug("PerformanceOptimizer initialized")
    
    def check_existence_cached(self, image_path: Path) -> bool:
        """Check image existence with caching for performance"""
        path_str = str(image_path)
        current_time = datetime.now().timestamp()
        
        # Check cache first
        if path_str in self.cached_existence:
            cached_time, cached_exists = self.cached_existence[path_str]
            if current_time - cached_time < self.cache_duration:
                logger.debug(f"Cache hit for {image_path}: {cached_exists}")
                return cached_exists
        
        # Cache miss or expired - check actual existence
        exists = image_path.exists()
        self.cached_existence[path_str] = (current_time, exists)
        logger.debug(f"Cache miss for {image_path}: {exists}")
        return exists
    
    def batch_existence_check(self, images: List[Path]) -> Dict[str, bool]:
        """Batch check existence for multiple images"""
        results = {}
        cache_hits = 0
        
        for image in images:
            exists = self.check_existence_cached(image)
            results[str(image)] = exists
            if str(image) in self.cached_existence:
                cache_hits += 1
        
        logger.debug(f"Batch existence check: {len(images)} images, {cache_hits} cache hits")
        return results
    
    def clear_cache(self):
        """Clear the existence cache"""
        self.cached_existence.clear()
        logger.debug("Existence cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'cached_entries': len(self.cached_existence),
            'cache_duration': self.cache_duration,
            'last_cleared': datetime.now().isoformat()
        }
