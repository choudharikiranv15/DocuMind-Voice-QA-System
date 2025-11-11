# src/gemini_vision_handler.py
import google.generativeai as genai
from PIL import Image
import io
import logging
from typing import List, Dict, Any, Optional
import base64
from src.llm_fallback_handler import LLMFallbackHandler


class GeminiVisionHandler:
    """Handler for Google Gemini Vision API with fallback to other vision models"""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.fallback_handler = None

        # Initialize Gemini API (Primary)
        if config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(config.GEMINI_VISION_MODEL)
                self.logger.info(f"✅ Gemini Vision initialized (Primary): {config.GEMINI_VISION_MODEL}")
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini Vision: {e}")
                self.model = None
        else:
            self.logger.warning("⚠️ GEMINI_API_KEY not set")

        # Initialize fallback vision models
        try:
            self.fallback_handler = LLMFallbackHandler(config)
            # Check if any fallback has vision models
            vision_providers = [p for p in self.fallback_handler.providers if p.get('vision_model')]
            if vision_providers:
                self.logger.info(f"✅ Vision fallbacks available: {len(vision_providers)} providers")
            else:
                self.logger.warning("⚠️ No vision fallback models available")
                self.fallback_handler = None
        except Exception as e:
            self.logger.warning(f"Failed to initialize vision fallbacks: {e}")
            self.fallback_handler = None

    def is_available(self) -> bool:
        """Check if Gemini Vision is available"""
        return self.model is not None

    def describe_image(self, image_data: bytes, prompt: str = None) -> Optional[str]:
        """
        Describe an image using Gemini Vision with fallback to other vision models

        Args:
            image_data: Raw image bytes (PNG, JPEG, etc.)
            prompt: Optional custom prompt for the image analysis

        Returns:
            Text description of the image or None if failed
        """
        # Default prompt if not provided
        if not prompt:
            prompt = """Analyze this image from a scientific/educational document. Provide:
1. What type of content is this (diagram, graph, chart, chemical structure, equation, etc.)?
2. Detailed description of all visible elements
3. Any text, labels, or annotations present
4. The main concepts or information conveyed

Be thorough and precise. This is for educational Q&A purposes."""

        # Try Gemini first (Primary)
        if self.is_available():
            try:
                # Load image from bytes
                image = Image.open(io.BytesIO(image_data))

                # Generate description
                response = self.model.generate_content([prompt, image])

                if response and response.text:
                    self.logger.info("✅ Image described by Gemini Vision (Primary)")
                    return response.text
                else:
                    self.logger.warning("Gemini Vision returned empty response, trying fallbacks...")
            except Exception as e:
                self.logger.warning(f"Gemini Vision failed: {e}, trying fallbacks...")
        else:
            self.logger.warning("Gemini Vision not available, trying fallbacks...")

        # Try fallback vision models (SambaNova, OpenRouter, Together AI)
        if self.fallback_handler:
            try:
                # Convert image to base64 for fallback APIs
                img_base64 = base64.b64encode(image_data).decode('utf-8')
                # Create data URL
                image_url = f"data:image/png;base64,{img_base64}"

                result = self.fallback_handler.query_vision(
                    question=prompt,
                    image_data=image_url
                )

                if result['success']:
                    self.logger.info(f"✅ Image described by {result['provider']} vision model (Fallback)")
                    return result['answer']
                else:
                    self.logger.error(f"All vision models failed: {result.get('error', 'Unknown')}")
                    return None

            except Exception as e:
                self.logger.error(f"Vision fallback failed: {e}")
                return None
        else:
            self.logger.error("No vision models available (Gemini and fallbacks all failed)")
            return None

    def describe_multiple_images(self, images_data: List[bytes], context: str = None) -> Optional[str]:
        """
        Describe multiple images together with context

        Args:
            images_data: List of raw image bytes
            context: Optional context about the images (page numbers, document info, etc.)

        Returns:
            Combined description of all images
        """
        if not self.is_available():
            return None

        try:
            # Load all images
            images = [Image.open(io.BytesIO(img_data)) for img_data in images_data]

            # Build prompt
            prompt = f"""Analyze these {len(images)} images from an educational document.
{f"Context: {context}" if context else ""}

For each image, provide:
1. Image type (diagram, chart, chemical structure, etc.)
2. Detailed description
3. Any text or labels
4. Key concepts

Then provide an overall summary of how these images relate to each other."""

            # Generate description (Gemini can handle multiple images)
            content = [prompt] + images
            response = self.model.generate_content(content)

            if response and response.text:
                self.logger.info(f"✅ Successfully described {len(images)} images")
                return response.text
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error describing multiple images: {e}")
            return None

    def answer_image_question(self, image_data: bytes, question: str) -> Optional[str]:
        """
        Answer a specific question about an image

        Args:
            image_data: Raw image bytes
            question: Specific question about the image

        Returns:
            Answer to the question based on image content
        """
        if not self.is_available():
            return None

        try:
            image = Image.open(io.BytesIO(image_data))

            # Build focused prompt
            prompt = f"""Answer this question about the image: {question}

Provide a clear, accurate answer based ONLY on what you see in the image.
If the image doesn't contain information to answer the question, say so."""

            response = self.model.generate_content([prompt, image])

            if response and response.text:
                self.logger.info("✅ Answered image question with Gemini Vision")
                return response.text
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error answering image question: {e}")
            return None

    def extract_structured_data(self, image_data: bytes, data_type: str = "table") -> Optional[str]:
        """
        Extract structured data from images (tables, charts, diagrams)

        Args:
            image_data: Raw image bytes
            data_type: Type of data to extract (table, chart, diagram, equation)

        Returns:
            Structured representation of the data
        """
        if not self.is_available():
            return None

        try:
            image = Image.open(io.BytesIO(image_data))

            # Specialized prompts based on data type
            prompts = {
                "table": "Extract all data from this table. Format as markdown table with proper headers and rows.",
                "chart": "Describe this chart/graph. Include: type, axes labels, data series, key values, and trends.",
                "diagram": "Describe this diagram. Include all labeled components, connections, and relationships.",
                "equation": "Extract all mathematical/chemical equations or formulas. Use proper notation.",
                "chemical_structure": "Describe this chemical structure. Include: compound name (if visible), functional groups, bonds, atoms, and any stereochemistry."
            }

            prompt = prompts.get(data_type, prompts["diagram"])

            response = self.model.generate_content([prompt, image])

            if response and response.text:
                self.logger.info(f"✅ Extracted {data_type} data from image")
                return response.text
            else:
                return None

        except Exception as e:
            self.logger.error(f"Error extracting structured data: {e}")
            return None
