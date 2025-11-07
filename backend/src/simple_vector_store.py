# src/simple_vector_store.py
import numpy as np
from typing import List, Dict, Any
import logging
import pickle
import os

class SimpleVectorStore:
    """Simple in-memory vector store that works reliably with Streamlit"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.documents = []
        self.embeddings = []
        self.metadatas = []
        self.ids = []
        self.dim = 384
        
        self.logger.info("✅ Simple vector store initialized")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate simple hash-based embedding"""
        vec = [0.01] * self.dim
        if isinstance(text, str):
            words = text.lower().split()[:100]
            for i, word in enumerate(words):
                hash_val = abs(hash(word))
                idx = hash_val % self.dim
                vec[idx] += 1.0 / (i + 1)
            # Normalize
            norm = sum(v**2 for v in vec) ** 0.5
            if norm > 0:
                vec = [v / norm for v in vec]
        return vec
    
    def add_documents(self, chunks: List, document_name: str):
        """Add document chunks to vector store"""
        try:
            self.logger.info(f"Processing {len(chunks)} chunks for {document_name}")
            
            for i, chunk in enumerate(chunks):
                doc_id = f"{document_name}_{i}"
                
                # Generate embedding
                embedding = self._generate_embedding(chunk.content)
                
                # Store
                self.documents.append(chunk.content)
                self.embeddings.append(embedding)
                self.metadatas.append({
                    'document_name': document_name,
                    'chunk_type': getattr(chunk, 'chunk_type', 'text'),
                    'page_number': getattr(chunk, 'page_number', 1)
                })
                self.ids.append(doc_id)
            
            self.logger.info(f"✅ Added {len(chunks)} chunks from {document_name}")
            return {'success': True, 'count': len(chunks)}
            
        except Exception as e:
            self.logger.error(f"Failed to add documents: {e}")
            return {'success': False, 'error': str(e)}
    
    def search(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for relevant documents using cosine similarity"""
        try:
            if not self.documents:
                return {'documents': [], 'metadatas': [], 'distances': []}
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Calculate cosine similarities
            similarities = []
            for emb in self.embeddings:
                # Cosine similarity
                dot_product = sum(a * b for a, b in zip(query_embedding, emb))
                similarities.append(dot_product)
            
            # Get top k results
            top_indices = sorted(range(len(similarities)), 
                               key=lambda i: similarities[i], 
                               reverse=True)[:n_results]
            
            results = {
                'documents': [self.documents[i] for i in top_indices],
                'metadatas': [self.metadatas[i] for i in top_indices],
                'distances': [1.0 - similarities[i] for i in top_indices]  # Convert similarity to distance
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return {'documents': [], 'metadatas': [], 'distances': []}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        return {
            'total_documents': len(self.documents),
            'embedding_model': 'Simple Hash Embedder'
        }
