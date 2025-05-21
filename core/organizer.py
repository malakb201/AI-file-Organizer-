from typing import Dict, List, Tuple
from pathlib import Path
from ai_functions.categorization import AICategorizer
from ai_functions.suggestions import AISuggester
from core.file_operations import FileOperations
import logging
import time

class FileOrganizer:
    def __init__(self, config: Dict, logger: logging.Logger):
        """
        Initialize the file organizer with configuration and dependencies
        """
        self.config = config
        self.logger = logger
        self.file_ops = FileOperations(logger)
        
        # Initialize AI components if configured
        self.ai_enabled = config['ai']['enable_suggestions'] and config['ai']['api_key']
        self.ai_categorizer = None
        self.ai_suggester = None
        
        if self.ai_enabled:
            try:
                self.ai_categorizer = AICategorizer(config['ai']['api_key'], logger)
                self.ai_suggester = AISuggester(config['ai']['api_key'], logger)
                self.logger.info("AI components initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize AI components: {e}")
                self.ai_enabled = False

    def organize(
        self,
        source_dir: str,
        dest_dir: str,
        use_ai: bool = False,
        keep_originals: bool = False
    ) -> Dict:
        """
        Main organization method with keep-originals support
        Returns dictionary with operation results
        """
        start_time = time.time()
        results = {
            "total_files": 0,
            "organized": 0,
            "failures": 0,
            "empty_dirs_removed": 0,
            "suggestions": [],
            "custom_categories": {},
            "execution_time": 0,
            "operation_mode": "copy" if keep_originals else "move"
        }

        try:
            # 1. Scan source directory
            files = self.file_ops.scan_directory(source_dir)
            results["total_files"] = len(files)
            
            if not files:
                self.logger.warning(f"No files found in {source_dir}")
                return results

            # 2. Get AI custom categories if enabled
            if use_ai and self.ai_enabled and len(files) > 0:
                try:
                    results["custom_categories"] = self._get_ai_categories(files)
                    self.logger.info("Received AI-generated categories")
                except Exception as e:
                    self.logger.error(f"AI categorization failed: {e}")

            # 3. Organize files
            organized, failures = self.file_ops.organize_files(
                files,
                self.config,
                dest_dir,
                keep_originals
            )
            results["organized"] = organized
            results["failures"] = failures

            # 4. Cleanup empty directories
            if not keep_originals:
                results["empty_dirs_removed"] = self.file_ops.cleanup_empty_dirs(source_dir)

            # 5. Get AI suggestions if enabled
            if use_ai and self.ai_enabled and len(files) > 0:
                try:
                    sample_files = files[:min(5, len(files))]
                    results["suggestions"] = self._get_ai_suggestions(sample_files, dest_dir)
                    self.logger.info("Received AI suggestions")
                except Exception as e:
                    self.logger.error(f"AI suggestions failed: {e}")

        except Exception as e:
            self.logger.error(f"Organization failed: {e}")
            raise
        finally:
            results["execution_time"] = round(time.time() - start_time, 2)
            self.logger.info(
                f"Organization completed in {results['execution_time']}s. "
                f"{organized}/{results['total_files']} files processed."
            )

        return results

    def _get_ai_categories(self, files: List[Dict]) -> Dict:
        """
        Get AI-generated custom categories for files
        """
        if not self.ai_categorizer:
            return {}
        
        # Limit to first 20 files to manage token usage
        sample_files = files[:20]
        return self.ai_categorizer.generate_categories(sample_files)

    def _get_ai_suggestions(self, files: List[Dict], dest_dir: str) -> List[str]:
        """
        Get AI suggestions for file organization
        """
        if not self.ai_suggester:
            return []
        
        return self.ai_suggester.get_suggestions(files, dest_dir)

    def generate_report(self, files: List[Dict], report_path: str) -> bool:
        """
        Generate a detailed report of files and their organization
        """
        try:
            return self.file_ops.generate_report(files, report_path)
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return False

    def validate_paths(self, source: str, dest: str) -> Tuple[bool, str]:
        """
        Validate source and destination paths before organization
        Returns (is_valid, error_message)
        """
        try:
            source_path = Path(source)
            dest_path = Path(dest)

            if not source_path.exists():
                return False, "Source directory does not exist"
            if not source_path.is_dir():
                return False, "Source path is not a directory"
            if not dest_path.exists():
                try:
                    dest_path.mkdir(parents=True)
                except Exception as e:
                    return False, f"Could not create destination directory: {e}"
            if source == dest:
                return False, "Source and destination cannot be the same"
            
            return True, ""
        except Exception as e:
            return False, f"Path validation error: {e}"