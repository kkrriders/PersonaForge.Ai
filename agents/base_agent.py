

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json
import requests
import time
from config.settings import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, agent_name: str, model: str = None):
        self.agent_name = agent_name
        self.model = model or settings.ollama_model
        # Connect to Ollama - use settings value
        self.ollama_host = settings.ollama_host
        
        # Ensure proper URL format
        if not self.ollama_host.startswith('http'):
            self.ollama_host = f"http://{self.ollama_host}"
            
        logger.info(f"Initialized {agent_name} with model {self.model} at host {self.ollama_host}")
    
    async def call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """
        Make an async call to Ollama API with retry logic
        """
        # Fix URL formatting issue
        host = self.ollama_host.rstrip('/')
        if not host.startswith('http'):
            host = f"http://{host}"
        
        url = f"{host}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        # Retry logic
        for attempt in range(settings.ollama_max_retries):
            try:
                logger.info(f"Calling Ollama (attempt {attempt + 1}/{settings.ollama_max_retries}) at: {url} with model: {self.model}")
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=settings.ollama_timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "")
                    logger.info(f"Ollama response received: {len(generated_text)} characters")
                    return generated_text
                else:
                    logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                    if attempt < settings.ollama_max_retries - 1:
                        logger.info(f"Retrying in 5 seconds...")
                        time.sleep(5)
                        continue
                    return ""
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Cannot connect to Ollama. Is it running? Error: {str(e)}")
                if attempt < settings.ollama_max_retries - 1:
                    logger.info(f"Retrying connection in 10 seconds...")
                    time.sleep(10)
                    continue
                return ""
            except requests.exceptions.Timeout as e:
                logger.error(f"Ollama request timeout (attempt {attempt + 1}): {str(e)}")
                if attempt < settings.ollama_max_retries - 1:
                    logger.info(f"Retrying with longer timeout in 5 seconds...")
                    time.sleep(5)
                    continue
                logger.error(f"All {settings.ollama_max_retries} attempts failed. Please check if Ollama is running and the model is loaded.")
                return ""
            except Exception as e:
                logger.error(f"Error calling Ollama (attempt {attempt + 1}): {str(e)}")
                if attempt < settings.ollama_max_retries - 1:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                return ""
        
        return ""
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        """
        pass
    
    def validate_input(self, input_data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that input contains required fields
        """
        for field in required_fields:
            if field not in input_data:
                logger.error(f"Missing required field: {field}")
                return False
        return True