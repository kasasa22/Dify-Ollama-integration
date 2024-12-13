from threading import Lock
from time import time
from typing import Optional, Dict, Any
from requests.sessions import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, MissingSchema, Timeout

class MPLUGOWLModelExtraParameter:
    max_tokens: int = 1000
    temperature: float = 0.7
    support_vision: bool = True
    support_video: bool = True
    context_length: int = 2048

    def __init__(
        self,
        max_tokens: int,
        temperature: float,
        context_length: int,
        support_vision: bool = True,
        support_video: bool = True,
    ) -> None:
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.context_length = context_length
        self.support_vision = support_vision
        self.support_video = support_video

cache = {}
cache_lock = Lock()

class MPLUGOWLHelper:
    @staticmethod
    def get_model_parameters(server_url: str) -> MPLUGOWLModelExtraParameter:
        """Get model parameters from server"""
        MPLUGOWLHelper._clean_cache()
        
        cache_key = f"{server_url}"
        with cache_lock:
            if cache_key not in cache:
                cache[cache_key] = {
                    "expires": time() + 300,  # 5 minutes cache
                    "value": MPLUGOWLHelper._fetch_model_parameters(server_url),
                }
            return cache[cache_key]["value"]

    @staticmethod
    def _clean_cache() -> None:
        try:
            with cache_lock:
                expired_keys = [k for k, v in cache.items() if v["expires"] < time()]
                for k in expired_keys:
                    del cache[k]
        except RuntimeError:
            pass

    @staticmethod
    def _fetch_model_parameters(server_url: str) -> MPLUGOWLModelExtraParameter:
        """Fetch model parameters from server"""
        if not server_url or not server_url.strip():
            raise RuntimeError("server_url is empty")

        session = Session()
        session.mount("http://", HTTPAdapter(max_retries=3))
        session.mount("https://", HTTPAdapter(max_retries=3))

        try:
            response = session.get(f"{server_url}/health", timeout=10)
        except (MissingSchema, ConnectionError, Timeout) as e:
            raise RuntimeError(f"Failed to fetch model parameters: {e}")

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch model parameters. Status: {response.status_code}, Response: {response.text}")

        data = response.json()
        
        if not data.get("model_loaded", False):
            raise RuntimeError("Model is not loaded on the server")
            
        return MPLUGOWLModelExtraParameter(
            max_tokens=1000,  # Default from server
            temperature=0.7,  # Default from server
            context_length=2048,  # Default value
            support_vision=True,
            support_video=True
        )

    @staticmethod
    def format_chat_completion_request(
        messages: list,
        model: str = "mplug-owl3",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> Dict[str, Any]:
        """Format request for the chat completions endpoint"""
        return {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

def validate_server_url(credentials: dict) -> bool:
    """Validate the server URL in credentials"""
    server_url = credentials.get("server_url", "").strip()
    return bool(server_url)