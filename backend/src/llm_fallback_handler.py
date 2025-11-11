"""
LLM Fallback Handler with Multi-Provider Support
Supports: Groq, SambaNova, OpenRouter, Together AI
Includes: Text and Vision models
"""
import os
import logging
from typing import Dict, Any, Optional, List
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMFallbackHandler:
    """
    Handles LLM requests with automatic fallback across multiple providers
    Cascade: Groq → SambaNova → OpenRouter → Together AI
    """

    def __init__(self, config):
        """Initialize all LLM providers"""
        self.config = config
        self.providers = []
        self.current_provider_index = 0

        # Initialize providers in order of preference
        self._init_groq()
        self._init_sambanova()
        self._init_openrouter()
        self._init_huggingface()

        logger.info(f"LLM Fallback Handler initialized with {len(self.providers)} providers")
        for i, p in enumerate(self.providers):
            logger.info(f"  {i+1}. {p['name']} ({p['text_model']})")

    def _init_groq(self):
        """Initialize Groq (Primary)"""
        try:
            if hasattr(self.config, 'GROQ_API_KEY') and self.config.GROQ_API_KEY:
                client = OpenAI(
                    api_key=self.config.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                self.providers.append({
                    'name': 'Groq',
                    'client': client,
                    'text_model': 'llama-3.1-8b-instant',
                    'vision_model': None,  # Groq doesn't have vision models yet
                    'max_tokens': 8000,
                    'temperature': 0.7,
                    'quota_per_day': 14400
                })
                logger.info("[OK] Groq initialized (Primary)")
        except Exception as e:
            logger.warning(f"Groq initialization failed: {e}")

    def _init_sambanova(self):
        """Initialize SambaNova (Fallback 1)"""
        try:
            if hasattr(self.config, 'SAMBANOVA_API_KEY') and self.config.SAMBANOVA_API_KEY:
                client = OpenAI(
                    api_key=self.config.SAMBANOVA_API_KEY,
                    base_url="https://api.sambanova.ai/v1"
                )
                self.providers.append({
                    'name': 'SambaNova',
                    'client': client,
                    'text_model': 'Meta-Llama-3.1-8B-Instruct',
                    'vision_model': 'Llama-3.2-11B-Vision-Instruct',
                    'max_tokens': 8000,
                    'temperature': 0.7,
                    'quota_per_day': 30000  # $5 credit spread over 3 months
                })
                logger.info("[OK] SambaNova initialized (Fallback 1)")
        except Exception as e:
            logger.warning(f"SambaNova initialization failed: {e}")

    def _init_openrouter(self):
        """Initialize OpenRouter (Fallback 2)"""
        try:
            if hasattr(self.config, 'OPENROUTER_API_KEY') and self.config.OPENROUTER_API_KEY:
                client = OpenAI(
                    api_key=self.config.OPENROUTER_API_KEY,
                    base_url="https://openrouter.ai/api/v1"
                )
                self.providers.append({
                    'name': 'OpenRouter',
                    'client': client,
                    'text_model': 'deepseek/deepseek-r1:free',  # Free reasoning model
                    'text_model_simple': 'mistralai/mistral-small-3.1-24b-instruct:free',  # For simple queries
                    'vision_model': 'meta-llama/llama-3.2-11b-vision-instruct:free',
                    'vision_model_large': 'qwen/qwen2.5-vl-72b-instruct:free',
                    'max_tokens': 8000,
                    'temperature': 0.7,
                    'quota_per_day': 20000  # Estimated, rate-limited
                })
                logger.info("[OK] OpenRouter initialized (Fallback 2)")
        except Exception as e:
            logger.warning(f"OpenRouter initialization failed: {e}")

    def _init_huggingface(self):
        """Initialize Hugging Face Inference API (Fallback 3)"""
        try:
            if hasattr(self.config, 'HUGGINGFACE_API_TOKEN') and self.config.HUGGINGFACE_API_TOKEN:
                # Hugging Face uses a different API format, we'll use requests directly
                # For now, add as placeholder - will implement custom handler if needed
                client = OpenAI(
                    api_key=self.config.HUGGINGFACE_API_TOKEN,
                    base_url="https://api-inference.huggingface.co/v1"  # Note: HF might not have OpenAI-compatible endpoint
                )
                self.providers.append({
                    'name': 'Hugging Face',
                    'client': client,
                    'text_model': 'meta-llama/Meta-Llama-3.1-8B-Instruct',
                    'vision_model': 'meta-llama/Llama-3.2-11B-Vision-Instruct',
                    'max_tokens': 8000,
                    'temperature': 0.7,
                    'quota_per_day': 1000,  # Rate limited by requests/hour
                    'note': 'Free tier with rate limits'
                })
                logger.info("[OK] Hugging Face initialized (Fallback 3)")
        except Exception as e:
            logger.warning(f"Hugging Face initialization failed: {e}")

    def _is_complex_query(self, question: str) -> bool:
        """Determine if query is complex (needs reasoning model)"""
        complex_keywords = [
            'explain', 'why', 'how', 'analyze', 'compare', 'evaluate',
            'detailed', 'comprehensive', 'step by step', 'methodology'
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in complex_keywords)

    def _build_messages(self, question: str, conversation_history: List[str],
                       system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
        """Build message array for OpenAI-compatible API"""
        messages = []

        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": "You are a helpful AI assistant that answers questions based on the provided context. Be concise and accurate."
            })

        # Add conversation history (if any)
        if conversation_history:
            for i, msg in enumerate(conversation_history):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({"role": role, "content": msg})

        # Add current question
        messages.append({"role": "user", "content": question})

        return messages

    def query_text(self, question: str, conversation_history: List[str] = None,
                   system_prompt: Optional[str] = None,
                   max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Query with automatic fallback across providers

        Args:
            question: User question
            conversation_history: Previous conversation messages
            system_prompt: Custom system prompt
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with 'answer', 'provider', 'model', 'success'
        """
        if conversation_history is None:
            conversation_history = []

        # Try each provider in order
        for i, provider in enumerate(self.providers):
            try:
                logger.info(f"Trying {provider['name']}...")

                # Build messages
                messages = self._build_messages(question, conversation_history, system_prompt)

                # Choose model based on query complexity (for OpenRouter)
                if provider['name'] == 'OpenRouter' and 'text_model_simple' in provider:
                    model = provider['text_model_simple'] if not self._is_complex_query(question) else provider['text_model']
                else:
                    model = provider['text_model']

                # Make API call
                response = provider['client'].chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=provider['temperature']
                )

                answer = response.choices[0].message.content

                logger.info(f"[SUCCESS] {provider['name']} responded ({len(answer)} chars)")

                return {
                    'success': True,
                    'answer': answer,
                    'provider': provider['name'],
                    'model': model,
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
                }

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"{provider['name']} failed: {error_msg}")

                # Check if it's a quota error
                if 'rate' in error_msg.lower() or 'quota' in error_msg.lower() or '429' in error_msg:
                    logger.warning(f"{provider['name']} quota exceeded, trying next provider...")
                    continue
                elif i == len(self.providers) - 1:
                    # Last provider also failed
                    logger.error("All providers failed!")
                    return {
                        'success': False,
                        'answer': "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                        'provider': 'None',
                        'model': 'None',
                        'error': error_msg
                    }
                else:
                    # Try next provider
                    continue

        # Should not reach here, but just in case
        return {
            'success': False,
            'answer': "Service temporarily unavailable. Please try again later.",
            'provider': 'None',
            'model': 'None'
        }

    def query_vision(self, question: str, image_data: Any,
                    conversation_history: List[str] = None,
                    system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Query vision models with automatic fallback

        Args:
            question: User question about the image
            image_data: Image data (base64 or URL)
            conversation_history: Previous conversation
            system_prompt: Custom system prompt

        Returns:
            Dict with 'answer', 'provider', 'model', 'success'
        """
        if conversation_history is None:
            conversation_history = []

        # Filter providers that have vision models
        vision_providers = [p for p in self.providers if p.get('vision_model')]

        if not vision_providers:
            logger.warning("No vision providers available, falling back to text-only")
            return {
                'success': False,
                'answer': "Vision analysis is temporarily unavailable.",
                'provider': 'None',
                'model': 'None'
            }

        # Try each vision provider
        for i, provider in enumerate(vision_providers):
            try:
                logger.info(f"Trying {provider['name']} vision...")

                # Choose vision model
                if provider['name'] == 'OpenRouter' and 'vision_model_large' in provider:
                    # Use larger model for complex vision tasks
                    model = provider['vision_model_large'] if self._is_complex_query(question) else provider['vision_model']
                else:
                    model = provider['vision_model']

                # Build multimodal messages
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})

                # Add image message
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {"url": image_data}  # Can be base64 or URL
                        }
                    ]
                })

                # Make API call
                response = provider['client'].chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=2000
                )

                answer = response.choices[0].message.content

                logger.info(f"[SUCCESS] {provider['name']} vision responded")

                return {
                    'success': True,
                    'answer': answer,
                    'provider': provider['name'],
                    'model': model,
                    'tokens_used': response.usage.total_tokens if hasattr(response, 'usage') else 0
                }

            except Exception as e:
                error_msg = str(e)
                logger.warning(f"{provider['name']} vision failed: {error_msg}")

                if i == len(vision_providers) - 1:
                    # Last provider failed
                    return {
                        'success': False,
                        'answer': "Vision analysis failed. Please try again.",
                        'provider': 'None',
                        'model': 'None',
                        'error': error_msg
                    }
                else:
                    continue

        return {
            'success': False,
            'answer': "Vision analysis unavailable.",
            'provider': 'None',
            'model': 'None'
        }

    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all providers"""
        status = {
            'total_providers': len(self.providers),
            'providers': []
        }

        for provider in self.providers:
            status['providers'].append({
                'name': provider['name'],
                'text_model': provider['text_model'],
                'vision_model': provider.get('vision_model', 'None'),
                'quota_per_day': provider.get('quota_per_day', 'Unknown')
            })

        return status
