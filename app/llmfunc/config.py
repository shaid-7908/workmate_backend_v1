"""
Configuration settings for LangGraph functionality.
"""

import os
from typing import Dict, Any

class LangGraphConfig:
    """Configuration class for LangGraph settings."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "test_7908")
        self.langsmith_tracing = os.getenv("LANGCHAIN_TRACING_V2", "true")
        
        # Model configurations
        self.default_model = "gpt-4o-mini"
        self.advanced_model = "gpt-4o"
        
        # Agent configurations
        self.max_iterations = 10
        self.temperature = 0.1
        
    def get_llm_config(self, model_name: str = None) -> Dict[str, Any]:
        """Get LLM configuration."""
        return {
            "model": model_name or self.default_model,
            "temperature": self.temperature,
            "api_key": self.openai_api_key
        }
    
    def validate_config(self) -> bool:
        """Validate that required configurations are set."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return True

# Global config instance
config = LangGraphConfig() 