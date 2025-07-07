"""
OpenRouter API Client for generating AI descriptions
Updated to follow OpenRouter API v1 specifications
"""

import requests
import json
from typing import Optional, Dict, Any, List
from config import OPENROUTER_API_BASE, AI_DESCRIPTION_PROMPT


class OpenRouterClient:
    """Client for interacting with OpenRouter API following v1 specifications"""

    def __init__(self, api_key: str, model: str):
        """
        Initialize OpenRouter client

        Args:
            api_key: OpenRouter API key
            model: Model identifier (e.g., 'deepseek/deepseek-r1:free')
        """
        self.api_key = api_key
        self.model = model
        self.base_url = OPENROUTER_API_BASE
        self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """
        Get properly formatted headers according to OpenRouter API specs

        Returns:
            Dictionary of headers
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://llms-txt-generator.streamlit.app",  # Optional: for rankings
            "X-Title": "LLMS.txt Generator"  # Optional: for rankings
        }

    def _make_request(self, content: str) -> Optional[str]:
        """
        Make API request to OpenRouter following v1 specifications

        Args:
            content: Web page content to generate description for

        Returns:
            Generated description or None if failed
        """
        # Truncate content if too long (keep first 2000 chars for efficiency)
        truncated_content = content[:2000] if len(content) > 2000 else content

        prompt = AI_DESCRIPTION_PROMPT.format(content=truncated_content)

        # Payload following OpenRouter API v1 format
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 100,
            "temperature": 0.3,
            "top_p": 0.9
        }

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )

            # Handle different response status codes
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        description = choice["message"]["content"].strip()
                        # Clean up the description
                        description = description.replace("Description:", "").strip()
                        description = description.replace('"', '').strip()
                        return description[:150]  # Limit to 150 characters
            elif response.status_code == 400:
                error_data = response.json()
                print(f"OpenRouter API bad request: {error_data.get('error', {}).get('message', 'Unknown error')}")
            elif response.status_code == 401:
                print("OpenRouter API authentication failed: Invalid API key")
            elif response.status_code == 402:
                print("OpenRouter API payment required: Insufficient credits")
            elif response.status_code == 429:
                print("OpenRouter API rate limit exceeded")
            elif response.status_code >= 500:
                print(f"OpenRouter API server error: {response.status_code}")
            else:
                print(f"OpenRouter API unexpected status: {response.status_code}")

        except requests.exceptions.Timeout:
            print("OpenRouter API request timed out")
        except requests.exceptions.ConnectionError:
            print("OpenRouter API connection error")
        except Exception as e:
            print(f"OpenRouter API error: {e}")

        return None
    
    def generate_description(self, content: str, title: str = "") -> str:
        """
        Generate description for web page content with improved fallback logic

        Args:
            content: Main content of the web page
            title: Page title for context

        Returns:
            Generated description or fallback
        """
        if not content.strip():
            return "Resource information"

        # Try to generate AI description
        ai_description = self._make_request(content)

        if ai_description:
            return ai_description

        # Fallback to first sentence of content
        sentences = content.split('.')
        if sentences and len(sentences[0].strip()) > 10:
            first_sentence = sentences[0].strip()
            return first_sentence[:150] + ("..." if len(first_sentence) > 150 else "")

        return "Resource information"

    @staticmethod
    def validate_model_format(model: str) -> bool:
        """
        Validate model format according to OpenRouter specifications

        Args:
            model: Model string to validate

        Returns:
            True if format is valid (provider/model-name or provider/model-name:variant)
        """
        if not model or "/" not in model:
            return False

        # Check for invalid patterns
        if "//" in model or model.startswith("/") or model.endswith("/"):
            return False

        # Split by '/' to get provider and model parts
        parts = model.split("/", 1)  # Split only on first '/'
        if len(parts) != 2:
            return False

        provider, model_part = parts

        # Basic validation: no empty parts, reasonable length
        if not provider.strip() or not model_part.strip():
            return False

        if len(provider) > 50 or len(model_part) > 100:
            return False

        # Allow model variants (e.g., model-name:free, model-name:beta)
        if ":" in model_part:
            model_name, variant = model_part.split(":", 1)
            if not model_name.strip() or not variant.strip():
                return False

        return True

    def test_connection(self) -> tuple[bool, str]:
        """
        Test API connection and model availability with improved error handling

        Returns:
            Tuple of (success, message)
        """
        try:
            test_content = "This is a test page about API documentation."
            result = self._make_request(test_content)

            if result:
                return True, f"Connection successful! Model '{self.model}' is working."
            else:
                return False, f"Failed to get response from model '{self.model}'. Check model availability and credits."

        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Fetch list of available models from OpenRouter API

        Returns:
            List of model dictionaries or empty list if failed
        """
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                headers=self._get_headers(),
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                print(f"Failed to fetch models: HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model

        Args:
            model_id: Model identifier

        Returns:
            Model information dictionary or None if not found
        """
        models = self.get_available_models()
        for model in models:
            if model.get("id") == model_id:
                return model
        return None

    def is_model_free(self, model_id: str) -> bool:
        """
        Check if a model is free to use

        Args:
            model_id: Model identifier

        Returns:
            True if model is free, False otherwise
        """
        model_info = self.get_model_info(model_id)
        if model_info and "pricing" in model_info:
            prompt_price = float(model_info["pricing"].get("prompt", "0"))
            completion_price = float(model_info["pricing"].get("completion", "0"))
            return prompt_price == 0 and completion_price == 0
        return False
