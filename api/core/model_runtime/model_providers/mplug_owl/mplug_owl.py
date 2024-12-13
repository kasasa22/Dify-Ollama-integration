import os
import yaml
from typing import Optional

from core.model_runtime.model_providers.__base.model_provider import ModelProvider
from core.model_runtime.entities.model_entities import ModelType
from core.model_runtime.entities.provider_entities import ProviderEntity

class MplugOwlProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """Validate provider credentials"""
        pass

    def get_provider_schema(self) -> ProviderEntity:
        """Get provider schema"""
        # Get the directory containing this file
        dir_path = os.path.dirname(os.path.abspath(__file__))
        
        # Read the YAML file
        yaml_path = os.path.join(dir_path, "mplug_owl.yaml")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
            
        return ProviderEntity.parse_obj(yaml_data)

    def get_model_schema(self, model_type: ModelType, model: str):
        """Get model schema"""
        return super().get_model_schema(model_type, model)

    @property
    def is_chat_model(self) -> bool:
        """Is chat model"""
        return True

    @property
    def is_llm_model(self) -> bool:
        """Is LLM model"""
        return True

    @property
    def is_vision_model(self) -> bool:
        """Is vision model"""
        return True
