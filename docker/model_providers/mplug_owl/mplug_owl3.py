import logging
from typing import Optional
from core.model_runtime.model_providers.__base.model_provider import ModelProvider

logger = logging.getLogger(__name__)

class MPLUGOWLProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate the credentials for the provider.
        This is a minimal implementation since we validate per model.
        """
        pass