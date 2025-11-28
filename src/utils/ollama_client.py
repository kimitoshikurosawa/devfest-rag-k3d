"""
Ollama Client for LLM interactions
"""
import os
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client to interact with Ollama API"""
    
    def __init__(
        self,
        host: str = None,
        model: str = None
    ):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "gemma2:2b")
        self.api_url = f"{self.host}/api/generate"
        
        logger.info(f"OllamaClient initialized with host={self.host}, model={self.model}")
    
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Generate text from Ollama
        
        Args:
            prompt: User prompt
            system: System message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict with response and metadata
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            if system:
                payload["system"] = system
            
            logger.info(f"Sending request to Ollama: {prompt[:100]}...")
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "text": result.get("response", ""),
                "model": self.model,
                "done": result.get("done", False),
                "tokens": result.get("eval_count", 0)
            }
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return {
                "text": "Désolé, le modèle a mis trop de temps à répondre.",
                "error": "timeout"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return {
                "text": f"Erreur de communication avec le modèle: {str(e)}",
                "error": "request_failed"
            }
        except Exception as e:
            logger.error(f"Unexpected error in Ollama client: {e}")
            return {
                "text": f"Erreur inattendue: {str(e)}",
                "error": "unexpected"
            }
    
    def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            logger.info("Ollama health check: OK")
            return True
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
