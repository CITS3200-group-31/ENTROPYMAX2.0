"""
Temporary file manager for EntropyMax analysis.
Manages session-based temporary files and cleanup.
"""

import os
import sys
import uuid
import shutil
import atexit
import platform
from pathlib import Path
from typing import Dict
import logging

logger = logging.getLogger(__name__)

from .cache_paths import ensure_cache_root, resolve_cache_root


class TempFileManager:
    """Manage temporary files during EntropyMax analysis"""
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.base_dir = ensure_cache_root()
        self.binary_dir = self.base_dir / "binary"
        self.cache_dir = self.base_dir / "cache"
        self.session_dir = self.cache_dir / f"session_{self.session_id}"
        self.files: Dict[str, Path] = {}
        self._setup()
        
    def _setup(self):
        """Create session directory"""
        try:
            # Create binary and cache/session directories
            self.binary_dir.mkdir(parents=True, exist_ok=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.session_dir.mkdir(parents=True, exist_ok=True)
            
            # Create lock file
            lock_file = self.session_dir / ".lock"
            lock_file.touch()
            self.files['lock'] = lock_file
            
            # Register cleanup on exit
            atexit.register(self.cleanup)
            logger.info(f"Created session directory: {self.session_dir}")
            logger.info(f"Binary directory: {self.binary_dir}")
        except Exception as e:
            logger.error(f"Failed to setup temp directory: {e}")
            raise
            
    def get_path(self, file_type: str) -> Path:
        """Get path for specific file type"""
        filenames = {
            'cli_output': 'analysis_output.csv',
            'parquet': 'analysis_output.parquet',
            'lock': '.lock',
            'log': 'session.log'
        }
        
        filename = filenames.get(file_type, file_type)
        path = self.session_dir / filename
        self.files[file_type] = path
        return path
        
    def cleanup(self, keep_exports: bool = False):
        """Clean up temporary files"""
        try:
            if keep_exports:
                # Delete only intermediate files
                for file_type in ['lock', 'log']:
                    if file_type in self.files and self.files[file_type].exists():
                        self.files[file_type].unlink(missing_ok=True)
                logger.info(f"Cleaned intermediate files from session {self.session_id}")
            else:
                # Delete entire session directory
                if self.session_dir.exists():
                    shutil.rmtree(self.session_dir, ignore_errors=True)
                logger.info(f"Removed session directory: {self.session_dir}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            
    def export_to(self, file_type: str, destination: Path):
        """Export file to user-specified location"""
        if file_type not in self.files:
            raise KeyError(f"File type '{file_type}' not found in session")
            
        source = self.files[file_type]
        if not source.exists():
            raise FileNotFoundError(f"Source file does not exist: {source}")
            
        try:
            shutil.copy2(source, destination)
            logger.info(f"Exported {file_type} to {destination}")
        except Exception as e:
            logger.error(f"Failed to export {file_type}: {e}")
            raise
            
    def file_exists(self, file_type: str) -> bool:
        """Check if file exists"""
        if file_type in self.files:
            return self.files[file_type].exists()
        return False
        
    def get_session_info(self) -> Dict:
        """Get session information"""
        return {
            'session_id': self.session_id,
            'session_dir': str(self.session_dir),
            'binary_dir': str(self.binary_dir),
            'files': {k: str(v) for k, v in self.files.items()},
            'dir_exists': self.session_dir.exists()
        }
    
    
    def setup_binary_from_bundle(self, binary_name: str = "run_entropymax") -> Path:
        """Setup binary file from PyInstaller bundle or source directory.
        
        Always copies and overwrites to ensure integrity.
        
        Args:
            binary_name: Name of the binary file (without extension)
            
        Returns:
            Path to the binary in cache directory
            
        Raises:
            FileNotFoundError: If source binary not found
            PermissionError: If cannot set executable permissions
        """
        # Add .exe extension on Windows
        if platform.system() == "Windows" and not binary_name.endswith(".exe"):
            binary_name = f"{binary_name}.exe"
        
        # Determine source path
        if getattr(sys, 'frozen', False):
            # Running in PyInstaller bundle
            source_path = Path(sys._MEIPASS) / binary_name
        else:
            # Running as script - binary should be in frontend directory
            source_path = Path(__file__).parent.parent / binary_name
        
        if not source_path.exists():
            raise FileNotFoundError(f"Binary not found at source: {source_path}")
        
        # Destination path in cache
        dest_path = self.binary_dir / binary_name
        
        try:
            # Always copy to ensure integrity (overwrite if exists)
            shutil.copy2(source_path, dest_path)
            logger.info(f"Copied binary from {source_path} to {dest_path}")
            
            # Set executable permissions (not needed on Windows)
            if platform.system() != "Windows":
                os.chmod(dest_path, 0o755)
                logger.info(f"Set executable permissions on {dest_path}")
            
            # On macOS, try to remove quarantine attribute (may fail, that's ok)
            if platform.system() == "Darwin":
                try:
                    import subprocess
                    subprocess.run(
                        ['xattr', '-d', 'com.apple.quarantine', str(dest_path)],
                        capture_output=True,
                        timeout=5
                    )
                    logger.info(f"Removed quarantine attribute from {dest_path}")
                except Exception as e:
                    logger.debug(f"Could not remove quarantine attribute: {e}")
            
            return dest_path
            
        except Exception as e:
            logger.error(f"Failed to setup binary: {e}")
            raise
        
    @classmethod
    def cleanup_entire_cache(cls):
        """Clean up cache directory only (preserve binary) on app exit"""
        cache_dir = resolve_cache_root() / "cache"
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir, ignore_errors=True)
                logger.info(f"Removed cache directory: {cache_dir} (preserved binary)")
            except Exception as e:
                logger.error(f"Failed to remove cache directory {cache_dir}: {e}")
