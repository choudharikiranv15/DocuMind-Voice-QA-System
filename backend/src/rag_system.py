# src/rag_system.py
import os
import logging
from typing import List, Dict, Any
from .pdf_processor import PDFProcessor
# Use ChromaDB for persistent vector storage with proper embeddings
from .chroma_vector_store import ChromaVectorStore as VectorStore
from .retriever import SmartRetriever
from .llm_handler import LLMHandler
from .redis_cache import RedisCacheManager
from .gemini_vision_handler import GeminiVisionHandler


class RAGSystem:
    def __init__(self, config):
        self.config = config
        self.logger = self._setup_logging()

        # Initialize components
        self.pdf_processor = PDFProcessor(config)
        self.vector_store = VectorStore(config)
        self.retriever = SmartRetriever(self.vector_store, config)
        self.llm_handler = LLMHandler(config)
        self.gemini_vision = GeminiVisionHandler(config)

        # Initialize Redis cache (dual support: Upstash + local)
        self.cache = RedisCacheManager(config)

        self.logger.info("RAG System initialized successfully")
        if self.cache.enabled:
            self.logger.info(f"Redis cache enabled: {self.cache.mode}")

    def add_document(self, pdf_path: str, user_id: str = None) -> Dict[str, Any]:
        """Add a PDF document to the knowledge base with optional user_id"""
        try:
            # Extract document name
            doc_name = os.path.basename(pdf_path).replace('.pdf', '')

            self.logger.info(f"Processing document: {doc_name} (user: {user_id})")

            # Process PDF
            chunks = self.pdf_processor.extract_content(pdf_path)

            if not chunks:
                return {'success': False, 'message': 'No content extracted from PDF'}

            # Add to vector store with user_id
            self.vector_store.add_documents(chunks, doc_name, user_id=user_id)

            # Get statistics
            stats = {
                'total_chunks': len(chunks),
                'text_chunks': len([c for c in chunks if c.chunk_type == 'text']),
                'table_chunks': len([c for c in chunks if c.chunk_type == 'table']),
                'image_chunks': len([c for c in chunks if c.chunk_type == 'image'])
            }

            self.logger.info(f"Successfully added {doc_name}: {stats}")

            return {
                'success': True,
                'document_name': doc_name,
                'statistics': stats
            }

        except Exception as e:
            self.logger.error(f"Error processing document {pdf_path}: {e}")
            return {'success': False, 'message': str(e)}

    def _needs_image_extraction(self, question: str) -> bool:
        """Detect if question requires image/figure extraction"""
        image_keywords = [
            'image', 'figure', 'diagram', 'picture', 'illustration', 'graph', 'chart',
            'structure', 'reaction', 'equation', 'formula', 'mechanism', 'scheme',
            'drawing', 'sketch', 'plot', 'table', 'list all', 'show me'
        ]
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in image_keywords)

    def _enrich_with_images(self, retrieval_results: Dict[str, Any], document_name: str = None, user_id: str = None) -> Dict[str, Any]:
        """Extract and analyze images from relevant pages using Gemini Vision"""
        try:
            import fitz  # PyMuPDF

            # Check if Gemini Vision is available
            if not self.gemini_vision.is_available():
                self.logger.warning("Gemini Vision not available - skipping image analysis")
                return retrieval_results

            # Get unique pages from retrieval results
            pages_to_extract = set()
            for result in retrieval_results['results']:
                page_number = result['metadata'].get('page_number', 1)
                # Ensure page_number is an integer
                page_num = int(page_number) - 1  # Convert to 0-indexed
                pages_to_extract.add(page_num)
                # Also extract adjacent pages (images might be on nearby pages)
                pages_to_extract.add(max(0, page_num - 1))
                pages_to_extract.add(page_num + 1)

            self.logger.info(f"🖼️ Extracting and analyzing images from pages: {sorted(pages_to_extract)}")

            # Find the PDF file
            pdf_path = self._find_pdf_path(document_name, user_id)
            if not pdf_path:
                self.logger.warning("Could not find PDF file for image extraction")
                return retrieval_results

            # Extract and analyze images from those specific pages
            doc = fitz.open(pdf_path)
            image_analyses = []

            for page_num in sorted(pages_to_extract):
                if page_num >= len(doc):
                    continue

                page = doc[page_num]
                images = page.get_images(full=True)

                if images:
                    self.logger.info(f"📸 Found {len(images)} images on page {page_num + 1} - analyzing with Gemini Vision...")

                    for img_idx, img in enumerate(images):
                        try:
                            # Extract image data
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]

                            # Analyze with Gemini Vision
                            description = self.gemini_vision.describe_image(
                                image_bytes,
                                prompt=f"Analyze this image from page {page_num + 1} of an educational document. Describe all visible content including diagrams, chemical structures, equations, charts, graphs, or text."
                            )

                            if description:
                                image_analyses.append(f"""
📷 **Figure on Page {page_num + 1} (Image {img_idx + 1})**:
{description}
""")
                                self.logger.info(f"✅ Successfully analyzed image {img_idx + 1} on page {page_num + 1}")
                            else:
                                image_analyses.append(f"\n📷 **Image on Page {page_num + 1}**: Present but could not be analyzed")

                        except Exception as e:
                            self.logger.warning(f"Could not analyze image {img_idx} on page {page_num + 1}: {e}")
                            continue

            doc.close()

            # Add image analyses to the results
            if image_analyses and retrieval_results['results']:
                image_info = "\n".join(image_analyses)
                # Create a new result entry specifically for images
                image_result = {
                    'content': f"## Visual Content Found\n\n{image_info}",
                    'score': 0.95,  # High score for image results
                    'metadata': {
                        'chunk_type': 'image_analysis',
                        'page_number': 'multiple',
                        'source': 'gemini_vision'
                    }
                }
                # Insert at the beginning so LLM sees it first
                retrieval_results['results'].insert(0, image_result)
                self.logger.info(f"✅ Added {len(image_analyses)} image analyses to retrieval results")

            return retrieval_results

        except Exception as e:
            self.logger.error(f"Error extracting images: {e}", exc_info=True)
            return retrieval_results

    def _find_pdf_path(self, document_name: str = None, user_id: str = None) -> str:
        """Find the PDF file path from uploaded documents"""
        try:
            upload_folder = self.config.UPLOAD_FOLDER
            if not os.path.exists(upload_folder):
                return None

            # If document_name is provided, look for that specific file
            if document_name:
                pdf_name = f"{document_name}.pdf"
                pdf_path = os.path.join(upload_folder, pdf_name)
                if os.path.exists(pdf_path):
                    return pdf_path

            # Otherwise, get the most recent PDF
            pdf_files = [f for f in os.listdir(upload_folder) if f.endswith('.pdf')]
            if pdf_files:
                # Get most recently modified PDF
                pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(upload_folder, x)), reverse=True)
                return os.path.join(upload_folder, pdf_files[0])

            return None
        except Exception as e:
            self.logger.error(f"Error finding PDF path: {e}")
            return None

    def query(self, question: str, conversation_history: List[str] = None, document_name: str = None, user_id: str = None) -> Dict[str, Any]:
        """Query the RAG system with optional document filtering, user filtering, and caching"""
        try:
            self.logger.info(f"Processing query: {question} (user: {user_id})")
            if document_name:
                self.logger.info(f"Filtering to document: {document_name}")

            # Build cache key with user_id
            cache_key_suffix = f"_{user_id}" if user_id else ""

            # Check cache first (if enabled)
            cached_result = self.cache.get_cached_query_result(question, document_name, suffix=cache_key_suffix)
            if cached_result:
                self.logger.info("Returning cached result")
                cached_result['cached'] = True
                return cached_result

            # Retrieve relevant documents with user filtering
            retrieval_results = self.retriever.retrieve(
                question, conversation_history, document_filter=document_name, user_id=user_id)

            if not retrieval_results['results']:
                return {
                    'answer': "I couldn't find relevant information in the documents to answer your question.",
                    'sources_used': 0,
                    'query_type': retrieval_results['query_type'],
                    'confidence': 0.0,
                    'cached': False
                }

            # ON-DEMAND IMAGE EXTRACTION: If question asks about images/figures, extract them now
            if self._needs_image_extraction(question):
                self.logger.info("🖼️ Image-related query detected - extracting images on-demand")
                retrieval_results = self._enrich_with_images(retrieval_results, document_name, user_id)

            # Generate response
            response = self.llm_handler.generate_response(
                question,
                retrieval_results['results'],
                conversation_history
            )

            # Add retrieval info
            response['query_type'] = retrieval_results['query_type']
            response['retrieval_stats'] = {
                'total_found': retrieval_results['total_found'],
                'used_for_generation': len(retrieval_results['results'])
            }
            response['cached'] = False

            # Cache the result (if enabled) with user_id suffix
            self.cache.cache_query_result(question, document_name, response, ttl=self.config.QUERY_CACHE_TTL, suffix=cache_key_suffix)

            return response

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return {
                'answer': "I encountered an error while processing your question. Please try again.",
                'sources_used': 0,
                'query_type': 'error',
                'confidence': 0.0
            }

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics including cache stats"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            cache_stats = self.cache.get_cache_stats()

            return {
                'vector_store': vector_stats,
                'models': {
                    'embedding_model': self.config.EMBEDDING_MODEL,
                    'llm_model': self.config.LLM_MODEL
                },
                'cache': cache_stats
            }
        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}

    def delete_document(self, document_name: str, user_id: str = None) -> Dict[str, Any]:
        """Delete a specific document from the vector store, optionally filtered by user"""
        try:
            result = self.vector_store.delete_document(document_name, user_id=user_id)
            return result
        except Exception as e:
            self.logger.error(f"Error deleting document: {e}")
            return {'success': False, 'error': str(e)}

    def clear_all_documents(self) -> Dict[str, Any]:
        """Clear all documents from the vector store"""
        try:
            result = self.vector_store.clear_all()
            return result
        except Exception as e:
            self.logger.error(f"Error clearing documents: {e}")
            return {'success': False, 'error': str(e)}

    def list_documents(self, user_id: str = None) -> List[Dict[str, Any]]:
        """List all documents with statistics, optionally filtered by user"""
        try:
            return self.vector_store.list_documents(user_id=user_id)
        except Exception as e:
            self.logger.error(f"Error listing documents: {e}")
            return []

    def clear_conversation_history(self):
        """Clear conversation history"""
        self.llm_handler.clear_history()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
