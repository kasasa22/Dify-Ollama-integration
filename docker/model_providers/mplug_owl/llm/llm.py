import json
import logging
from typing import Optional, List, Dict, Any, Union
from requests.exceptions import HTTPError, Timeout
import aiohttp
import base64
from io import BytesIO

from core.model_runtime.errors.validate import CredentialsValidateFailedError
from core.model_runtime.entities.llm_entities import LLMMode, LLMResult
from core.model_runtime.entities.message_entities import AssistantMessage, UserMessage, MessageType
from core.model_runtime.model_providers.__base.large_language_model import BaseLargeLanguageModel

from .mplug_owl_helper import MPLUGOWLHelper, validate_server_url

logger = logging.getLogger(__name__)

class MPLUGOWLLargeLanguageModel(BaseLargeLanguageModel):
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Validate model credentials
        """
        if not validate_server_url(credentials):
            raise CredentialsValidateFailedError("Server URL is required")

        try:
            # Test connection and get model parameters
            MPLUGOWLHelper.get_model_parameters(credentials["server_url"])
        except Exception as ex:
            raise CredentialsValidateFailedError(f"Failed to validate credentials: {str(ex)}")

    def _get_model_mode(self) -> LLMMode:
        """
        Get model mode
        """
        return LLMMode.CHAT

    async def _process_image(self, image_url: str, session: aiohttp.ClientSession) -> bytes:
        """Process image URL and return bytes"""
        if image_url.startswith('data:image'):
            # Handle base64 encoded images
            header, encoded = image_url.split(",", 1)
            return base64.b64decode(encoded)
        else:
            # Handle regular URLs
            async with session.get(image_url) as response:
                response.raise_for_status()
                return await response.read()

    async def _generate(
        self, 
        messages: List[Union[AssistantMessage, UserMessage]], 
        model: str,
        credentials: dict,
        model_parameters: dict,
        tools: Optional[List[Dict]] = None,
        stop: Optional[List[str]] = None,
        stream: bool = False,
        user: Optional[str] = None
    ) -> LLMResult:
        """
        Generate text based on messages
        """
        server_url = credentials["server_url"].rstrip('/')
        endpoint = f"{server_url}/v1/chat/completions"

        timeout = aiohttp.ClientTimeout(
            total=float(credentials.get("invoke_timeout", 240))
        )

        formatted_messages = []
        last_user_message = None

        # Process messages
        for message in messages:
            if isinstance(message, UserMessage):
                last_user_message = {
                    "role": "user",
                    "content": message.content
                }
                
                # Handle image if present
                if message.message_type == MessageType.MULTIMODAL:
                    image_url = message.images[0] if message.images else None
                    if image_url:
                        last_user_message["media_url"] = image_url

            elif isinstance(message, AssistantMessage):
                formatted_messages.append({
                    "role": "assistant",
                    "content": message.content
                })

        # Add the last user message
        if last_user_message:
            formatted_messages.append(last_user_message)

        request_body = MPLUGOWLHelper.format_chat_completion_request(
            messages=formatted_messages,
            model=model,
            temperature=float(model_parameters.get("temperature", 0.7)),
            max_tokens=int(model_parameters.get("max_tokens", 1000))
        )

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint, json=request_body) as response:
                    response.raise_for_status()
                    result = await response.json()

                    if result.get("error_code", 0) != 0:
                        raise Exception(result.get("error", {}).get("message", "Unknown error"))

                    response_data = result.get("data", {})
                    choices = response_data.get("choices", [])
                    
                    if not choices:
                        raise Exception("No response choices available")

                    first_choice = choices[0]
                    message = first_choice.get("message", {})
                    usage = response_data.get("usage", {})

                    return LLMResult(
                        model=model,
                        prompt_tokens=usage.get("prompt_tokens", 0),
                        completion_tokens=usage.get("completion_tokens", 0),
                        total_tokens=usage.get("total_tokens", 0),
                        system_fingerprint=None,
                        content=message.get("content", ""),
                        stop_reason=first_choice.get("finish_reason")
                    )

        except HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise e
        except Timeout as e:
            logger.error(f"Request timed out: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise e

    async def _generate_stream(
        self,
        messages: List[Union[AssistantMessage, UserMessage]],
        model: str,
        credentials: dict,
        model_parameters: dict,
        tools: Optional[List[Dict]] = None,
        stop: Optional[List[str]] = None,
        user: Optional[str] = None
    ) -> LLMResult:
        """
        Streaming is not supported for mPlugOWL currently
        Fallback to regular generation
        """
        return await self._generate(
            messages=messages,
            model=model,
            credentials=credentials,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=False,
            user=user
        )

    def get_num_tokens(self, prompt: str, model_name: str) -> int:
        """
        Get number of tokens in prompt
        Simple implementation - can be improved with actual tokenizer
        """
        return len(prompt.split())