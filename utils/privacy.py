"""
Privacy and Security Manager - Ensures local data privacy and encryption
"""

import os
import json
import hashlib
import logging
import time
from datetime import datetime
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    print("⚠️  Cryptography not installed. Encryption features will be disabled.")
    Fernet = hashes = PBKDF2HMAC = None
    CRYPTOGRAPHY_AVAILABLE = False
import base64
from typing import Dict, Any, Optional, List
from config.settings import settings

logger = logging.getLogger(__name__)

class PrivacyManager:
    def __init__(self):
        self.encryption_enabled = settings.encrypt_data and CRYPTOGRAPHY_AVAILABLE
        self.local_storage_only = settings.local_storage_only
        self.key_file = "data/.encryption_key"
        self._cipher_suite = None
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        if self.encryption_enabled:
            self._setup_encryption()
        elif settings.encrypt_data and not CRYPTOGRAPHY_AVAILABLE:
            logger.warning("Encryption requested but cryptography package not available")
    
    def _setup_encryption(self):
        """Set up encryption for sensitive data"""
        try:
            if os.path.exists(self.key_file):
                # Load existing key
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            else:
                # Generate new key
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                # Set file permissions to read-only for owner
                os.chmod(self.key_file, 0o600)
            
            self._cipher_suite = Fernet(key)
            logger.info("Encryption setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up encryption: {str(e)}")
            self.encryption_enabled = False
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not self.encryption_enabled or not self._cipher_suite:
            return data
        
        try:
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {str(e)}")
            return data
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not self.encryption_enabled or not self._cipher_suite:
            return encrypted_data
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self._cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {str(e)}")
            return encrypted_data
    
    def hash_sensitive_info(self, data: str) -> str:
        """Create a hash of sensitive information for identification without storing raw data"""
        return hashlib.sha256(data.encode()).hexdigest()[:16]  # First 16 chars for brevity
    
    def sanitize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize user data before storage"""
        sanitized_data = user_data.copy()
        
        # Fields that should be encrypted
        sensitive_fields = ['name', 'current_work', 'career_goals']
        
        for field in sensitive_fields:
            if field in sanitized_data and sanitized_data[field]:
                sanitized_data[field] = self.encrypt_data(str(sanitized_data[field]))
        
        # Convert lists and dicts to JSON strings before encryption
        if 'skills' in sanitized_data:
            skills_json = json.dumps(sanitized_data['skills'])
            sanitized_data['skills'] = self.encrypt_data(skills_json)
        
        if 'preferences' in sanitized_data:
            prefs_json = json.dumps(sanitized_data['preferences'])
            sanitized_data['preferences'] = self.encrypt_data(prefs_json)
        
        return sanitized_data
    
    def desanitize_user_data(self, sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore user data after retrieval from storage"""
        if not sanitized_data:
            return {}
        
        restored_data = sanitized_data.copy()
        
        # Fields that were encrypted
        sensitive_fields = ['name', 'current_work', 'career_goals']
        
        for field in sensitive_fields:
            if field in restored_data and restored_data[field]:
                restored_data[field] = self.decrypt_data(restored_data[field])
        
        # Restore JSON fields
        if 'skills' in restored_data and restored_data['skills']:
            try:
                skills_decrypted = self.decrypt_data(restored_data['skills'])
                restored_data['skills'] = json.loads(skills_decrypted)
            except:
                restored_data['skills'] = []
        
        if 'preferences' in restored_data and restored_data['preferences']:
            try:
                prefs_decrypted = self.decrypt_data(restored_data['preferences'])
                restored_data['preferences'] = json.loads(prefs_decrypted)
            except:
                restored_data['preferences'] = {}
        
        return restored_data
    
    def sanitize_post_content(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize post content before storage"""
        sanitized_data = post_data.copy()
        
        # Encrypt content if it contains sensitive information
        if 'content' in sanitized_data:
            content = sanitized_data['content']
            # Check if content might contain sensitive info (basic heuristic)
            if self._contains_sensitive_info(content):
                sanitized_data['content'] = self.encrypt_data(content)
                sanitized_data['_encrypted_content'] = True
        
        return sanitized_data
    
    def desanitize_post_content(self, sanitized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Restore post content after retrieval"""
        if not sanitized_data:
            return {}
        
        restored_data = sanitized_data.copy()
        
        # Decrypt content if it was encrypted
        if restored_data.get('_encrypted_content', False) and 'content' in restored_data:
            restored_data['content'] = self.decrypt_data(restored_data['content'])
            del restored_data['_encrypted_content']
        
        return restored_data
    
    def _contains_sensitive_info(self, content: str) -> bool:
        """Basic check if content might contain sensitive information"""
        sensitive_keywords = [
            'salary', 'personal', 'private', 'confidential', 
            'internal', 'proprietary', 'ssn', 'social security'
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in sensitive_keywords)
    
    def secure_file_cleanup(self, file_path: str) -> bool:
        """Securely delete a file"""
        try:
            if os.path.exists(file_path):
                # Overwrite file with random data before deletion
                file_size = os.path.getsize(file_path)
                with open(file_path, 'rb+') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                
                # Delete the file
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"Error securely deleting file {file_path}: {str(e)}")
            return False
    
    def validate_local_storage(self) -> Dict[str, Any]:
        """Validate that all data is stored locally and securely"""
        validation_results = {
            'local_storage_only': self.local_storage_only,
            'encryption_enabled': self.encryption_enabled,
            'key_file_exists': os.path.exists(self.key_file),
            'data_directory_permissions': {},
            'file_count': 0,
            'total_size_mb': 0
        }
        
        try:
            # Check data directory
            data_dir = "data"
            if os.path.exists(data_dir):
                # Check permissions
                stat_info = os.stat(data_dir)
                validation_results['data_directory_permissions'] = {
                    'owner_read': bool(stat_info.st_mode & 0o400),
                    'owner_write': bool(stat_info.st_mode & 0o200),
                    'group_access': bool(stat_info.st_mode & 0o040),
                    'other_access': bool(stat_info.st_mode & 0o004)
                }
                
                # Count files and calculate total size
                total_size = 0
                file_count = 0
                for root, dirs, files in os.walk(data_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            pass
                
                validation_results['file_count'] = file_count
                validation_results['total_size_mb'] = round(total_size / (1024 * 1024), 2)
        
        except Exception as e:
            logger.error(f"Error validating local storage: {str(e)}")
            validation_results['error'] = str(e)
        
        return validation_results
    
    def export_user_data(self, user_id: str = 'default') -> Dict[str, Any]:
        """Export user data for backup (encrypted)"""
        try:
            from utils.database import DatabaseManager
            db_manager = DatabaseManager()
            
            # This would be implemented to export all user data
            # For now, return a placeholder structure
            export_data = {
                'export_timestamp': str(datetime.now()),
                'user_id': user_id,
                'encryption_used': self.encryption_enabled,
                'data_note': 'User data export functionality - implementation would fetch from database'
            }
            
            if self.encryption_enabled:
                export_json = json.dumps(export_data)
                export_data = {
                    'encrypted_export': self.encrypt_data(export_json),
                    'encryption_note': 'Data is encrypted for security'
                }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting user data: {str(e)}")
            return {'error': str(e)}
    
    def get_privacy_settings(self) -> Dict[str, Any]:
        """Get current privacy and security settings"""
        return {
            'local_storage_only': self.local_storage_only,
            'encryption_enabled': self.encryption_enabled,
            'data_location': os.path.abspath('data'),
            'key_file_secured': os.path.exists(self.key_file),
            'privacy_features': [
                'All data stored locally on your machine',
                'No cloud storage or external APIs for data',
                'Optional encryption for sensitive information',
                'Secure file deletion capabilities',
                'User data export functionality'
            ],
            'recommendations': self._get_privacy_recommendations()
        }
    
    def _get_privacy_recommendations(self) -> List[str]:
        """Get privacy and security recommendations"""
        recommendations = []
        
        if not self.encryption_enabled:
            recommendations.append("Enable encryption for sensitive data in settings")
        
        if not self.local_storage_only:
            recommendations.append("Ensure local storage only mode is enabled")
        
        # Check file permissions
        if os.path.exists(self.key_file):
            stat_info = os.stat(self.key_file)
            if stat_info.st_mode & 0o077:  # Check if group or others have access
                recommendations.append("Secure encryption key file permissions")
        
        recommendations.extend([
            "Regularly backup your data directory",
            "Keep your system updated for security",
            "Use strong system passwords",
            "Consider full disk encryption for additional security"
        ])
        
        return recommendations
    
    def cleanup_temporary_files(self) -> int:
        """Clean up temporary files and return count of files cleaned"""
        cleaned_count = 0
        
        try:
            # Clean up temporary image files older than 7 days
            images_dir = "data/images"
            if os.path.exists(images_dir):
                current_time = time.time()
                for filename in os.listdir(images_dir):
                    file_path = os.path.join(images_dir, filename)
                    if os.path.isfile(file_path):
                        # Check if file is older than 7 days
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 7 * 24 * 3600:  # 7 days in seconds
                            if self.secure_file_cleanup(file_path):
                                cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            
        except Exception as e:
            logger.error(f"Error cleaning temporary files: {str(e)}")
        
        return cleaned_count