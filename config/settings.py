"""
Configuration settings for the LinkedIn Automation Tool
"""

import os
from typing import Dict, Any, List

# Simple settings class that works without pydantic
class Settings:
    def __init__(self):
        # Load from environment or use defaults
        
        # Ollama Configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3:8b")
        
        # Database Configuration
        self.database_path = os.getenv("DATABASE_PATH", "data/linkedin_tool.db")
        
        # LinkedIn API Configuration (for future use)
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        
        # Content Generation Settings
        self.max_post_length = int(os.getenv("MAX_POST_LENGTH", "3000"))
        self.default_hashtags = ["#LinkedInPost", "#PersonaForgeAI"]
        
        # Scheduling Settings
        self.posting_schedule = {
            "mini_projects": {"frequency": "every_15_days", "enabled": True},
            "main_projects": {"frequency": "monthly", "enabled": True},
            "capstone_project": {"frequency": "quarterly", "enabled": True}
        }
        
        # Image Generation Settings
        self.image_width = int(os.getenv("IMAGE_WIDTH", "1200"))
        self.image_height = int(os.getenv("IMAGE_HEIGHT", "630"))
        self.image_quality = int(os.getenv("IMAGE_QUALITY", "95"))
        
        # AI Image Generation Settings
        self.stable_diffusion_model = os.getenv("STABLE_DIFFUSION_MODEL", "runwayml/stable-diffusion-v1-5")
        self.ai_image_steps = int(os.getenv("AI_IMAGE_STEPS", "20"))
        self.ai_image_guidance = float(os.getenv("AI_IMAGE_GUIDANCE", "7.5"))
        
        # Google Gemini Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        self.gemini_max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "8192"))
        
        # Data Privacy Settings
        self.local_storage_only = os.getenv("LOCAL_STORAGE_ONLY", "true").lower() == "true"
        self.encrypt_data = os.getenv("ENCRYPT_DATA", "true").lower() == "true"
        
        # Ollama Timeout Settings
        self.ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "600"))  # 10 minutes
        self.ollama_max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        
        # Application Settings
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "data/app.log")
        self.app_name = os.getenv("APP_NAME", "PersonaForge.AI")
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Global settings instance
settings = Settings()