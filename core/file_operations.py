import os
import shutil
import mimetypes
import magic
from pathlib import Path
from typing import List, Dict, Tuple
import pandas as pd
import logging

class FileOperations:
    def __init__(self, logger: logging.Logger):
        """
        Initialize file operations handler with multiple file detection methods
        """
        self.logger = logger
        mimetypes.init()
        
        # Try to initialize both magic and mimetypes as fallback
        self.mime_detector = None
        try:
            self.mime_detector = magic.Magic(mime=True)
            self.logger.info("Using python-magic for file type detection")
        except ImportError:
            self.logger.warning("python-magic not available, using mimetypes as fallback")
        except Exception as e:
            self.logger.error(f"Failed to initialize magic: {e}, using mimetypes")

    def get_file_type(self, file_path: str) -> str:
        """
        Determine file type using the best available method
        """
        try:
            if self.mime_detector:
                return self.mime_detector.from_file(file_path)
            else:
                mime_type, _ = mimetypes.guess_type(file_path)
                return mime_type or "application/octet-stream"
        except Exception as e:
            self.logger.error(f"Error determining file type for {file_path}: {e}")
            return "unknown"

    def scan_directory(self, directory: str) -> List[Dict]:
        """
        Scan a directory and return comprehensive file information
        Returns list of dictionaries with file metadata
        """
        files = []
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    try:
                        file_type = self.get_file_type(entry.path)
                        files.append({
                            "name": entry.name,
                            "path": entry.path,
                            "size": entry.stat().st_size,
                            "modified": entry.stat().st_mtime,
                            "created": entry.stat().st_ctime,
                            "type": file_type,
                            "extension": Path(entry.name).suffix.lower()
                        })
                    except Exception as e:
                        self.logger.error(f"Error processing file {entry.path}: {e}")
            return files
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {e}")
            return []

    def organize_files(
        self, 
        files: List[Dict], 
        rules: Dict, 
        dest_dir: str, 
        keep_originals: bool = False
    ) -> Tuple[int, int]:
        """
        Organize files based on rules with option to keep originals
        Returns tuple of (success_count, failure_count)
        """
        success = 0
        failures = 0
        
        for file in files:
            try:
                # Determine target folder based on rules
                target_folder = self._determine_target_folder(file, rules)
                
                # Create target directory if needed
                target_path = Path(dest_dir) / target_folder
                target_path.mkdir(parents=True, exist_ok=True)
                
                # Perform file operation based on keep_originals setting
                if keep_originals:
                    shutil.copy2(file['path'], target_path / file['name'])
                    action = "Copied"
                else:
                    shutil.move(file['path'], target_path / file['name'])
                    action = "Moved"
                
                self.logger.debug(f"{action} {file['name']} to {target_folder}")
                success += 1
            except Exception as e:
                self.logger.error(f"Failed to organize {file.get('name', 'unknown')}: {e}")
                failures += 1
        
        return success, failures

    def _determine_target_folder(self, file: Dict, rules: Dict) -> str:
        """
        Determine the target folder for a file based on categorization rules
        """
        # First try extension-based matching
        file_ext = file.get('extension', '')
        for category, extensions in rules['file_types'].items():
            if file_ext in extensions:
                return category
        
        # Fallback to type-based categorization if available
        file_type = file.get('type', '').split('/')[0]
        if file_type in ['image', 'video', 'audio', 'text']:
            return file_type + 's'  # pluralize
        
        return 'others'

    def generate_report(self, files: List[Dict], output_path: str) -> bool:
        """
        Generate a CSV report of file operations
        Returns True if successful
        """
        try:
            df = pd.DataFrame(files)
            df['size_mb'] = df['size'] / (1024 * 1024)
            
            report_columns = [
                'name', 'extension', 'type', 
                'size_mb', 'modified', 'created'
            ]
            
            df[report_columns].to_csv(output_path, index=False)
            return True
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return False

    def cleanup_empty_dirs(self, directory: str) -> int:
        """
        Remove empty directories after organization
        Returns count of removed directories
        """
        removed = 0
        try:
            for root, dirs, _ in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):
                            dir_path.rmdir()
                            removed += 1
                    except Exception as e:
                        self.logger.error(f"Error checking {dir_path}: {e}")
            return removed
        except Exception as e:
            self.logger.error(f"Error during directory cleanup: {e}")
            return removed