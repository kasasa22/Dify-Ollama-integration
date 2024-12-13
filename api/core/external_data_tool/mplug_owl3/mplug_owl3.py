from typing import Optional
import requests
import base64
from core.external_data_tool.base import ExternalDataTool

class MPLUGOwl3(ExternalDataTool):
    """
    mPLUG-Owl3 vision analysis tool for processing images and videos
    """
    name: str = "mplug_owl3"

    @classmethod
    def validate_config(cls, tenant_id: str, config: dict) -> None:
        """
        Validate the configuration when saving
        """
        if not config.get('api_base'):
            raise ValueError('API base URL is required')
            
        # Validate temperature is between 0 and 1
        temperature = config.get('temperature', 0.7)
        if not (0 <= float(temperature) <= 1):
            raise ValueError('Temperature must be between 0 and 1')
            
        # Validate max_tokens is positive
        max_tokens = config.get('max_tokens', 1000)
        if int(max_tokens) <= 0:
            raise ValueError('Max tokens must be positive')

    def query(self, inputs: dict, query: Optional[str] = None) -> str:
        """
        Process media through mPLUG-Owl3 API
        
        Args:
            inputs: Dict containing 'image' or 'video' data
            query: User's question about the media
        """
        try:
            # Get media data from inputs
            media_data = inputs.get('image') or inputs.get('video')
            if not media_data:
                return "No media file provided"

            # Convert media data to base64
            if isinstance(media_data, str) and media_data.startswith('data:'):
                # Already in base64 format
                media_url = media_data
            else:
                # Convert to base64
                media_type = "video/mp4" if inputs.get('video') else "image/jpeg"
                media_base64 = base64.b64encode(media_data).decode('utf-8')
                media_url = f"data:{media_type};base64,{media_base64}"

            # Prepare API call
            api_base = self.config.get('api_base').rstrip('/')
            temperature = float(self.config.get('temperature', 0.7))
            max_tokens = int(self.config.get('max_tokens', 1000))

            # Call mPLUG-Owl3 API
            response = requests.post(
                f"{api_base}/v1/chat/completions",
                json={
                    "model": "mplug-owl3",
                    "messages": [{
                        "role": "user",
                        "content": query or "Describe what you see in this media.",
                        "media_url": media_url
                    }],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            if result.get('error_code', 0) != 0:
                raise Exception(result.get('error', {}).get('message', 'Unknown error'))
                
            return result['data']['choices'][0]['message']['content']
            
        except Exception as e:
            return f"Error processing media: {str(e)}"