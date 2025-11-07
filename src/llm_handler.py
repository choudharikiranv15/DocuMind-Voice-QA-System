# src/llm_handler.py
from groq import Groq
from typing import List, Dict, Any
import logging

class LLMHandler:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.conversation_history = []
        
        # Check if API key is available
        if not config.GROQ_API_KEY:
            self.logger.error("GROQ_API_KEY is not set. Please add your API key to the .env file.")
            self.client = None
        else:
            self.client = Groq(api_key=config.GROQ_API_KEY)
        
    def generate_response(self, query: str, context_docs: List[Dict[str, Any]], 
                         conversation_history: List[str] = None) -> Dict[str, Any]:
        """Generate response using retrieved context"""
        
        # Prepare context from retrieved documents
        context_text = self._prepare_context(context_docs)
        
        # Build conversation context
        conversation_context = self._build_conversation_context(conversation_history)
        
        # Create prompt
        prompt = self._create_prompt(query, context_text, conversation_context)
        
        try:
            # Check if client is initialized
            if self.client is None:
                error_message = "ERROR: Groq API key is not set or is invalid. Please add a valid API key to the .env file."
                self.logger.error(error_message)
                return {
                    'answer': error_message,
                    'sources_used': len(context_docs),
                    'context_types': list(set([doc['metadata']['chunk_type'] for doc in context_docs])),
                    'confidence': 0.0,
                    'error': True
                }
                
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                stream=False
            )
            
            answer = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append(f"User: {query}")
            self.conversation_history.append(f"Assistant: {answer}")
            
            return {
                'answer': answer,
                'sources_used': len(context_docs),
                'context_types': list(set([doc['metadata']['chunk_type'] for doc in context_docs])),
                'confidence': self._calculate_confidence(context_docs),
                'error': False
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                'answer': "I apologize, but I encountered an error while generating a response. Please try again.",
                'sources_used': 0,
                'context_types': [],
                'confidence': 0.0
            }
    
    def _prepare_context(self, context_docs: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        
        for i, doc in enumerate(context_docs, 1):
            content = doc['content']
            metadata = doc['metadata']
            
            context_part = f"""
            SOURCE {i} (Page {metadata['page_number']}, Type: {metadata['chunk_type']}):
            {content}
            """
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _build_conversation_context(self, conversation_history: List[str]) -> str:
        """Build conversation context"""
        if not conversation_history:
            return ""
        
        return "CONVERSATION HISTORY:\n" + "\n".join(conversation_history[-6:])  # Last 3 exchanges
    
    def _create_prompt(self, query: str, context_text: str, conversation_context: str) -> str:
        """Create the complete prompt"""
        prompt = f"""
        {conversation_context}
        
        CONTEXT FROM DOCUMENTS:
        {context_text}
        
        USER QUESTION: {query}
        
        INSTRUCTIONS:
        Provide a well-structured, ChatGPT-style response with:
        1. A brief introductory paragraph
        2. Clear section headers (## for main sections, ### for subsections)
        3. Bullet points for lists
        4. **Bold** for emphasis on key terms
        5. Proper spacing between sections
        6. Natural, conversational language
        7. Page citations where relevant
        
        Format your response in clean markdown. Make it easy to read and scan.
        """
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the LLM"""
        return """
        You are an intelligent document assistant similar to ChatGPT. You help users find information from PDF documents.
        You have access to content extracted from PDFs including text, tables, and images (via OCR).
        
        IMPORTANT - Response Formatting Rules:
        1. Structure your response like ChatGPT with clear sections:
           - Start with a brief introduction paragraph
           - Use ## for main section headers
           - Use ### for subsections
           - Use clear paragraphs between sections
           
        2. Formatting guidelines:
           - Use **bold** for key terms and emphasis
           - Use bullet points with • for lists
           - Use numbered lists (1., 2., 3.) for sequential steps
           - Leave blank lines between sections for readability
           - Use > for important notes or quotes
           
        3. Content presentation:
           - Write in a natural, conversational tone
           - Break complex information into digestible sections
           - If presenting data from tables, format as markdown tables
           - For images, note with 📷 "Information from image"
           - Cite page numbers naturally: "(Page 3)" or "as mentioned on page 5"
           
        4. Quality standards:
           - Be concise but comprehensive
           - Avoid repetition
           - Don't use excessive symbols or asterisks
           - Make responses scannable with good structure
           - End with a brief summary if the answer is long
        
        Example response structure:
        
        Based on the documents, here's what I found about [topic]:
        
        ## Main Finding
        
        [Clear paragraph explaining the main point]
        
        ## Key Details
        
        • **Point 1**: Description
        • **Point 2**: Description
        • **Point 3**: Description
        
        ## Additional Information
        
        [Supporting details in paragraph form]
        
        > Note: This information is from page X of the document.
        """
    
    def _calculate_confidence(self, context_docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on retrieved context"""
        if not context_docs:
            return 0.0
        
        # Base confidence on similarity scores and number of sources
        avg_score = sum([doc['score'] for doc in context_docs]) / len(context_docs)
        source_bonus = min(len(context_docs) / 5, 1.0)  # Bonus for multiple sources
        
        return min(avg_score * (1 + source_bonus * 0.2), 1.0)
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
