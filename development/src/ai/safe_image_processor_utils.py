#!/usr/bin/env python3
"""
Safe Image Processor Utilities - Extracted Modular Architecture
REFACTOR Phase: Production-ready utility classes for atomic image operations
"""

import logging
import shutil
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class BackupMetadata:
    """Structured information about backup operations"""
    session_id: str
    operation_name: str
    backup_path: Path
    images_backed_up: int
    created_at: datetime
    is_valid: bool = True


@dataclass
class AtomicOperationResult:
    """Result of atomic operation execution"""
    success: bool
    operation_id: str
    files_affected: List[Path]
    backup_session_id: str
    execution_time: float
    error_details: Optional[str] = None


class ImageBackupManager:
    """Utility class for managing image backups with rollback capability"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.backup_root = vault_path / ".image_backups"
        logger.debug("ImageBackupManager initialized")

    def create_session_backup(self, session_id: str, images: List[Path]) -> BackupMetadata:
        """Create backup for a specific session with comprehensive metadata"""
        backup_dir = self.backup_root / session_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        backed_up_images = {}
        images_count = 0

        for image_path in images:
            if image_path.exists():
                try:
                    backup_path = backup_dir / image_path.name
                    # Handle name collisions
                    counter = 1
                    original_backup_path = backup_path
                    while backup_path.exists():
                        stem = original_backup_path.stem
                        suffix = original_backup_path.suffix
                        backup_path = backup_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                    shutil.copy2(image_path, backup_path)
                    backed_up_images[str(image_path)] = backup_path
                    images_count += 1
                    logger.debug(f"Backed up {image_path} to {backup_path}")
                except Exception as e:
                    logger.error(f"Failed to backup {image_path}: {e}")

        metadata = BackupMetadata(
            session_id=session_id,
            operation_name="session_backup",
            backup_path=backup_dir,
            images_backed_up=images_count,
            created_at=datetime.now(),
            is_valid=backup_dir.exists() and images_count > 0
        )

        # Store backup mapping for restoration
        self._store_backup_mapping(session_id, backed_up_images)

        logger.info(f"Created session backup: {session_id}, {images_count} images")
        return metadata

    def restore_from_backup(self, session_id: str) -> bool:
        """Restore images from backup session"""
        backup_mapping = self._load_backup_mapping(session_id)
        if not backup_mapping:
            logger.error(f"No backup mapping found for session: {session_id}")
            return False

        restored_count = 0
        for original_path, backup_path in backup_mapping.items():
            try:
                if backup_path.exists():
                    original = Path(original_path)
                    if original.parent.exists():
                        shutil.copy2(backup_path, original)
                        restored_count += 1
                        logger.debug(f"Restored {original} from {backup_path}")
            except Exception as e:
                logger.error(f"Failed to restore {original_path}: {e}")

        logger.info(f"Restored {restored_count} images for session: {session_id}")
        return restored_count > 0

    def cleanup_backup(self, session_id: str) -> bool:
        """Clean up backup directory after successful operation"""
        backup_dir = self.backup_root / session_id
        if backup_dir.exists():
            try:
                shutil.rmtree(backup_dir)
                self._remove_backup_mapping(session_id)
                logger.debug(f"Cleaned up backup for session: {session_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to cleanup backup {session_id}: {e}")
        return False

    def validate_backup_integrity(self, session_id: str) -> bool:
        """Validate backup integrity for session"""
        backup_dir = self.backup_root / session_id
        backup_mapping = self._load_backup_mapping(session_id)

        if not backup_dir.exists() or not backup_mapping:
            return False

        # Check if all backup files exist
        for backup_path in backup_mapping.values():
            if not backup_path.exists():
                return False

        return True

    def _store_backup_mapping(self, session_id: str, mapping: Dict[str, Path]):
        """Store backup mapping for session"""
        mapping_file = self.backup_root / f"{session_id}_mapping.json"
        try:
            import json
            # Convert Path objects to strings for JSON serialization
            serializable_mapping = {k: str(v) for k, v in mapping.items()}
            mapping_file.write_text(json.dumps(serializable_mapping, indent=2))
        except Exception as e:
            logger.error(f"Failed to store backup mapping: {e}")

    def _load_backup_mapping(self, session_id: str) -> Dict[str, Path]:
        """Load backup mapping for session"""
        mapping_file = self.backup_root / f"{session_id}_mapping.json"
        if not mapping_file.exists():
            return {}

        try:
            import json
            data = json.loads(mapping_file.read_text())
            # Convert strings back to Path objects
            return {k: Path(v) for k, v in data.items()}
        except Exception as e:
            logger.error(f"Failed to load backup mapping: {e}")
            return {}

    def _remove_backup_mapping(self, session_id: str):
        """Remove backup mapping file"""
        mapping_file = self.backup_root / f"{session_id}_mapping.json"
        if mapping_file.exists():
            try:
                mapping_file.unlink()
            except Exception as e:
                logger.error(f"Failed to remove backup mapping: {e}")


class AtomicOperationEngine:
    """Utility class for executing atomic operations with guaranteed rollback"""

    def __init__(self, backup_manager: ImageBackupManager):
        self.backup_manager = backup_manager
        self.operation_history: List[AtomicOperationResult] = []
        logger.debug("AtomicOperationEngine initialized")

    def execute_atomic_operation(
        self,
        operation_name: str,
        images: List[Path],
        operation_func: Callable,
        *args, **kwargs
    ) -> AtomicOperationResult:
        """Execute operation atomically with automatic rollback on failure"""
        start_time = datetime.now()
        operation_id = str(uuid.uuid4())
        session_id = f"{operation_name}_{operation_id[:8]}"

        try:
            # Create backup
            backup_metadata = self.backup_manager.create_session_backup(session_id, images)
            if not backup_metadata.is_valid:
                raise RuntimeError("Failed to create valid backup")

            # Execute operation
            operation_result = operation_func(*args, **kwargs)

            # Check if operation succeeded
            if self._validate_operation_success(operation_result, images):
                # Success - cleanup backup
                self.backup_manager.cleanup_backup(session_id)
                execution_time = (datetime.now() - start_time).total_seconds()

                result = AtomicOperationResult(
                    success=True,
                    operation_id=operation_id,
                    files_affected=images,
                    backup_session_id=session_id,
                    execution_time=execution_time
                )
                self.operation_history.append(result)
                return result
            else:
                raise RuntimeError("Operation validation failed")

        except Exception as e:
            # Failure - rollback
            self.backup_manager.restore_from_backup(session_id)
            execution_time = (datetime.now() - start_time).total_seconds()

            result = AtomicOperationResult(
                success=False,
                operation_id=operation_id,
                files_affected=images,
                backup_session_id=session_id,
                execution_time=execution_time,
                error_details=str(e)
            )
            self.operation_history.append(result)
            return result

    def _validate_operation_success(self, operation_result, images: List[Path]) -> bool:
        """Validate that operation completed successfully"""
        # Check if operation result indicates success
        if hasattr(operation_result, 'success'):
            if not operation_result.success:
                return False
        elif isinstance(operation_result, dict):
            if not operation_result.get('success', True):
                return False

        # Check if all images still exist
        for image in images:
            if not image.exists():
                logger.warning(f"Image {image} missing after operation")
                return False

        return True

    def get_operation_stats(self) -> Dict:
        """Get statistics about atomic operations"""
        total_ops = len(self.operation_history)
        successful_ops = sum(1 for op in self.operation_history if op.success)
        failed_ops = total_ops - successful_ops

        if total_ops > 0:
            avg_execution_time = sum(op.execution_time for op in self.operation_history) / total_ops
        else:
            avg_execution_time = 0.0

        return {
            'total_operations': total_ops,
            'successful_operations': successful_ops,
            'failed_operations': failed_ops,
            'success_rate': successful_ops / total_ops if total_ops > 0 else 0.0,
            'average_execution_time': avg_execution_time
        }


class ImageExtractor:
    """Utility class for extracting image references from note content"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.tiff'}
        logger.debug("ImageExtractor initialized")

    def extract_images_from_note(self, note_path: Path) -> List[Path]:
        """Extract all image references from note content with comprehensive pattern matching"""
        if not note_path.exists():
            return []

        try:
            content = note_path.read_text(encoding='utf-8')
            return self._parse_image_references(content)
        except Exception as e:
            logger.error(f"Failed to extract images from {note_path}: {e}")
            return []

    def extract_images_from_content(self, content: str) -> List[Path]:
        """Extract images from raw content string"""
        return self._parse_image_references(content)

    def _parse_image_references(self, content: str) -> List[Path]:
        """Parse image references using comprehensive regex patterns"""
        images = []

        # Pattern 1: ![alt](path) - Standard markdown
        markdown_pattern = r'!\[.*?\]\(([^)]+)\)'
        markdown_matches = re.findall(markdown_pattern, content)

        # Pattern 2: ![[path]] - Wiki-style links
        wiki_pattern = r'!\[\[([^\]]+)\]\]'
        wiki_matches = re.findall(wiki_pattern, content)

        # Pattern 3: <img src="path"> - HTML tags
        html_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        html_matches = re.findall(html_pattern, content, re.IGNORECASE)

        # Combine all matches
        all_matches = markdown_matches + wiki_matches + html_matches

        for match in all_matches:
            # Clean up the path
            image_ref = match.strip()

            # Skip data URLs and external URLs
            if image_ref.startswith(('data:', 'http://', 'https://')):
                continue

            # Convert to absolute path
            image_path = self._resolve_image_path(image_ref)

            if image_path and self._is_valid_image(image_path):
                images.append(image_path)

        logger.debug(f"Extracted {len(images)} valid images from content")
        return images

    def _resolve_image_path(self, image_ref: str) -> Optional[Path]:
        """Resolve image reference to absolute path"""
        try:
            # Handle absolute paths
            if image_ref.startswith('/'):
                return Path(image_ref)

            # Handle relative paths
            # Try relative to vault root first
            vault_relative = self.vault_path / image_ref
            if vault_relative.exists():
                return vault_relative

            # Try common media directories
            media_dirs = ['Media', 'Images', 'Assets', 'attachments']
            for media_dir in media_dirs:
                media_path = self.vault_path / media_dir / image_ref
                if media_path.exists():
                    return media_path

            # If file doesn't exist but path is valid, return it anyway
            # (file might be created during processing)
            return vault_relative

        except Exception as e:
            logger.debug(f"Failed to resolve image path {image_ref}: {e}")
            return None

    def _is_valid_image(self, image_path: Path) -> bool:
        """Check if path represents a valid image file"""
        if image_path.suffix.lower() not in self.image_extensions:
            return False

        # Additional checks can be added here (file size, image format validation, etc.)
        return True


class SessionManager:
    """Utility class for managing multiple concurrent backup sessions"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_history: List[Dict] = []
        logger.debug("SessionManager initialized")

    def create_session(self, operation_name: str, metadata: Optional[Dict] = None) -> str:
        """Create new backup session with unique ID"""
        session_id = f"{operation_name}_{uuid.uuid4().hex[:8]}"

        session_info = {
            'session_id': session_id,
            'operation_name': operation_name,
            'created_at': datetime.now(),
            'status': 'created',
            'metadata': metadata or {}
        }

        self.active_sessions[session_id] = session_info
        logger.debug(f"Created session: {session_id}")
        return session_id

    def update_session_status(self, session_id: str, status: str, details: Optional[Dict] = None):
        """Update session status and details"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['status'] = status
            self.active_sessions[session_id]['updated_at'] = datetime.now()
            if details:
                self.active_sessions[session_id]['metadata'].update(details)

    def close_session(self, session_id: str, final_status: str = 'completed'):
        """Close session and move to history"""
        if session_id in self.active_sessions:
            session_info = self.active_sessions.pop(session_id)
            session_info['status'] = final_status
            session_info['closed_at'] = datetime.now()
            self.session_history.append(session_info)
            logger.debug(f"Closed session: {session_id}")

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about active session"""
        return self.active_sessions.get(session_id)

    def list_active_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self.active_sessions.keys())

    def get_session_stats(self) -> Dict:
        """Get statistics about session management"""
        return {
            'active_sessions': len(self.active_sessions),
            'total_sessions': len(self.session_history) + len(self.active_sessions),
            'completed_sessions': len([s for s in self.session_history if s['status'] == 'completed']),
            'failed_sessions': len([s for s in self.session_history if s['status'] == 'failed'])
        }


class ProcessingResultBuilder:
    """Utility class for building structured processing results"""

    def __init__(self):
        logger.debug("ProcessingResultBuilder initialized")

    def build_success_result(
        self,
        operation: str,
        note_path: Path,
        preserved_images: List[Path],
        processing_time: float,
        backup_session_id: str,
        additional_data: Optional[Dict] = None
    ):
        """Build successful processing result"""
        from . import safe_image_processor  # Avoid circular import

        result = safe_image_processor.ProcessingResult(
            success=True,
            operation=operation,
            note_path=note_path,
            preserved_images=preserved_images,
            processing_time=processing_time,
            backup_session_id=backup_session_id
        )

        if additional_data:
            # Add additional data as attributes
            for key, value in additional_data.items():
                setattr(result, key, value)

        return result

    def build_failure_result(
        self,
        operation: str,
        note_path: Path,
        processing_time: float,
        backup_session_id: str,
        error_message: str,
        preserved_images: Optional[List[Path]] = None
    ):
        """Build failed processing result"""
        from . import safe_image_processor  # Avoid circular import

        return safe_image_processor.ProcessingResult(
            success=False,
            operation=operation,
            note_path=note_path,
            preserved_images=preserved_images or [],
            processing_time=processing_time,
            backup_session_id=backup_session_id,
            error_message=error_message
        )

    def build_batch_results_summary(self, results: List) -> Dict:
        """Build summary of batch processing results"""
        total_results = len(results)
        successful_results = sum(1 for r in results if r.success)
        failed_results = total_results - successful_results

        total_processing_time = sum(r.processing_time for r in results)
        total_images_preserved = sum(len(r.preserved_images) for r in results)

        return {
            'total_notes_processed': total_results,
            'successful_operations': successful_results,
            'failed_operations': failed_results,
            'success_rate': successful_results / total_results if total_results > 0 else 0.0,
            'total_processing_time': total_processing_time,
            'average_processing_time': total_processing_time / total_results if total_results > 0 else 0.0,
            'total_images_preserved': total_images_preserved,
            'operations_requiring_rollback': failed_results
        }
