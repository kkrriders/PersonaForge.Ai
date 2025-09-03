"""
Configuration Manager - Handles application configuration and settings
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.config_file = "data/user_config.json"
        self.user_config = {}
        self._load_user_config()
    
    def _load_user_config(self):
        """Load user-specific configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.user_config = json.load(f)
                logger.info("User configuration loaded successfully")
            else:
                self.user_config = self._get_default_config()
                self._save_user_config()
                logger.info("Default configuration created")
        except Exception as e:
            logger.error(f"Error loading user config: {str(e)}")
            self.user_config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings"""
        return {
            "version": "1.0.0",
            "user_preferences": {
                "theme": "default",
                "notifications": True,
                "auto_save": True,
                "backup_frequency": "weekly"
            },
            "content_settings": {
                "default_post_type": "general",
                "auto_hashtag_generation": True,
                "image_generation_enabled": True,
                "engagement_predictions": True
            },
            "privacy_settings": {
                "data_retention_days": 365,
                "auto_cleanup_temp_files": True,
                "encryption_level": "standard"
            },
            "scheduling_settings": {
                "auto_scheduling": False,
                "preferred_posting_times": ["09:00", "12:00", "17:00"],
                "time_zone": "UTC",
                "weekend_posting": False
            },
            "ai_settings": {
                "creativity_level": "balanced",  # conservative, balanced, creative
                "content_length_preference": "medium",
                "tone_consistency": True,
                "learning_from_performance": True
            },
            "export_settings": {
                "default_format": "json",
                "include_images": True,
                "include_analytics": True
            },
            "advanced_settings": {
                "concurrent_generations": 1,
                "retry_attempts": 3,
                "cache_responses": True,
                "debug_mode": False
            }
        }
    
    def _save_user_config(self):
        """Save user configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.user_config, f, indent=2)
            logger.info("User configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving user config: {str(e)}")
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self.user_config.get(category, {}).get(key, default)
        except Exception as e:
            logger.error(f"Error getting setting {category}.{key}: {str(e)}")
            return default
    
    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """Update a specific setting"""
        try:
            if category not in self.user_config:
                self.user_config[category] = {}
            
            self.user_config[category][key] = value
            self._save_user_config()
            logger.info(f"Setting {category}.{key} updated successfully")
            return True
        except Exception as e:
            logger.error(f"Error updating setting {category}.{key}: {str(e)}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings"""
        return self.user_config.copy()
    
    def reset_category(self, category: str) -> bool:
        """Reset a category to default settings"""
        try:
            default_config = self._get_default_config()
            if category in default_config:
                self.user_config[category] = default_config[category].copy()
                self._save_user_config()
                logger.info(f"Category {category} reset to defaults")
                return True
            else:
                logger.warning(f"Category {category} not found in default config")
                return False
        except Exception as e:
            logger.error(f"Error resetting category {category}: {str(e)}")
            return False
    
    def reset_all_settings(self) -> bool:
        """Reset all settings to defaults"""
        try:
            self.user_config = self._get_default_config()
            self._save_user_config()
            logger.info("All settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting all settings: {str(e)}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """Export settings to a file"""
        try:
            export_data = {
                "export_timestamp": str(datetime.now()),
                "application": "PersonaForge.AI",
                "version": self.user_config.get("version", "1.0.0"),
                "settings": self.user_config
            }
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Settings exported to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting settings: {str(e)}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"Import file not found: {file_path}")
                return False
            
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            if "settings" in import_data:
                # Validate imported settings
                if self._validate_settings(import_data["settings"]):
                    self.user_config = import_data["settings"]
                    self._save_user_config()
                    logger.info(f"Settings imported from {file_path}")
                    return True
                else:
                    logger.error("Invalid settings format in import file")
                    return False
            else:
                logger.error("No settings found in import file")
                return False
                
        except Exception as e:
            logger.error(f"Error importing settings: {str(e)}")
            return False
    
    def _validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate settings structure"""
        try:
            default_config = self._get_default_config()
            
            # Check if all required top-level categories exist
            required_categories = set(default_config.keys())
            provided_categories = set(settings.keys())
            
            # Allow extra categories but ensure required ones exist
            if not required_categories.issubset(provided_categories):
                missing = required_categories - provided_categories
                logger.warning(f"Missing categories in import: {missing}")
                
                # Add missing categories with defaults
                for category in missing:
                    settings[category] = default_config[category]
            
            return True
        except Exception as e:
            logger.error(f"Error validating settings: {str(e)}")
            return False
    
    def get_display_config(self) -> Dict[str, Any]:
        """Get configuration formatted for display"""
        display_config = {}
        
        category_descriptions = {
            "user_preferences": "User Interface & Experience",
            "content_settings": "Content Generation",
            "privacy_settings": "Privacy & Security", 
            "scheduling_settings": "Post Scheduling",
            "ai_settings": "AI Behavior",
            "export_settings": "Data Export",
            "advanced_settings": "Advanced Options"
        }
        
        setting_descriptions = {
            "theme": "Application theme",
            "notifications": "Show notifications",
            "auto_save": "Automatically save drafts",
            "backup_frequency": "Backup frequency",
            "default_post_type": "Default post type",
            "auto_hashtag_generation": "Auto-generate hashtags",
            "image_generation_enabled": "Enable image generation",
            "engagement_predictions": "Show engagement predictions",
            "data_retention_days": "Data retention period (days)",
            "auto_cleanup_temp_files": "Auto cleanup temporary files",
            "encryption_level": "Encryption level",
            "auto_scheduling": "Enable auto-scheduling",
            "preferred_posting_times": "Preferred posting times",
            "time_zone": "Time zone",
            "weekend_posting": "Allow weekend posting",
            "creativity_level": "AI creativity level",
            "content_length_preference": "Content length preference",
            "tone_consistency": "Maintain tone consistency",
            "learning_from_performance": "Learn from post performance",
            "default_format": "Default export format",
            "include_images": "Include images in export",
            "include_analytics": "Include analytics in export",
            "concurrent_generations": "Concurrent generations",
            "retry_attempts": "Retry attempts on failure",
            "cache_responses": "Cache AI responses",
            "debug_mode": "Debug mode"
        }
        
        for category, settings_dict in self.user_config.items():
            if category == "version":
                continue
                
            category_name = category_descriptions.get(category, category.replace('_', ' ').title())
            display_config[category_name] = {}
            
            for key, value in settings_dict.items():
                setting_name = setting_descriptions.get(key, key.replace('_', ' ').title())
                display_config[category_name][setting_name] = {
                    "value": value,
                    "type": type(value).__name__,
                    "key": f"{category}.{key}"
                }
        
        return display_config
    
    def update_setting_by_key(self, setting_key: str, value: Any) -> bool:
        """Update setting using dot notation key (e.g., 'user_preferences.theme')"""
        try:
            category, key = setting_key.split('.', 1)
            return self.update_setting(category, key, value)
        except ValueError:
            logger.error(f"Invalid setting key format: {setting_key}")
            return False
        except Exception as e:
            logger.error(f"Error updating setting by key {setting_key}: {str(e)}")
            return False
    
    def get_environment_settings(self) -> Dict[str, Any]:
        """Get current environment settings from config/settings.py"""
        return {
            "Ollama Host": settings.ollama_host,
            "Ollama Model": settings.ollama_model,
            "Database Path": settings.database_path,
            "Max Post Length": settings.max_post_length,
            "Default Hashtags": settings.default_hashtags,
            "Image Width": settings.image_width,
            "Image Height": settings.image_height,
            "Image Quality": settings.image_quality,
            "Local Storage Only": settings.local_storage_only,
            "Encrypt Data": settings.encrypt_data,
            "Posting Schedule": settings.posting_schedule
        }
    
    def create_backup(self) -> str:
        """Create a timestamped backup of current settings"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"data/backups/settings_backup_{timestamp}.json"
            
            os.makedirs(os.path.dirname(backup_file), exist_ok=True)
            
            if self.export_settings(backup_file):
                logger.info(f"Settings backup created: {backup_file}")
                return backup_file
            else:
                return ""
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return ""
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available setting backups"""
        backups = []
        backup_dir = "data/backups"
        
        try:
            if os.path.exists(backup_dir):
                for filename in os.listdir(backup_dir):
                    if filename.startswith("settings_backup_") and filename.endswith(".json"):
                        file_path = os.path.join(backup_dir, filename)
                        stat = os.stat(file_path)
                        
                        backups.append({
                            "filename": filename,
                            "path": file_path,
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime),
                            "modified": datetime.fromtimestamp(stat.st_mtime)
                        })
                
                # Sort by creation time, newest first
                backups.sort(key=lambda x: x["created"], reverse=True)
        
        except Exception as e:
            logger.error(f"Error listing backups: {str(e)}")
        
        return backups
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore settings from a backup file"""
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Create current backup before restoring
            current_backup = self.create_backup()
            if current_backup:
                logger.info(f"Current settings backed up to: {current_backup}")
            
            # Import from backup
            if self.import_settings(backup_path):
                logger.info(f"Settings restored from backup: {backup_path}")
                return True
            else:
                logger.error(f"Failed to restore from backup: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error restoring from backup: {str(e)}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """Clean up old backup files, keeping only the specified number"""
        try:
            backups = self.list_backups()
            
            if len(backups) <= keep_count:
                return 0
            
            # Remove excess backups (oldest first)
            backups_to_remove = backups[keep_count:]
            removed_count = 0
            
            for backup in backups_to_remove:
                try:
                    os.remove(backup["path"])
                    removed_count += 1
                    logger.info(f"Removed old backup: {backup['filename']}")
                except Exception as e:
                    logger.error(f"Error removing backup {backup['filename']}: {str(e)}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up backups: {str(e)}")
            return 0