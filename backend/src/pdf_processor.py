# src/pdf_processor.py
# Optional PyMuPDF import (for image extraction)
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

import pdfplumber
import pytesseract
from PIL import Image
import pandas as pd
import numpy as np
import io
import re
from typing import List, Dict, Any, Tuple
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from .advanced_table_extractor import AdvancedTableExtractor

@dataclass
class DocumentChunk:
    content: str
    chunk_type: str  # 'text', 'table', 'image'
    page_number: int
    metadata: Dict[str, Any]
    
class PDFProcessor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.table_extractor = AdvancedTableExtractor()  # Use advanced table extraction
        
    def _process_single_page(self, pdf_path: str, page_num: int, total_pages: int) -> List[DocumentChunk]:
        """Process a single page (thread-safe)"""
        page_chunks = []

        try:
            # Open PDF in this thread (thread-safe)
            with pdfplumber.open(pdf_path) as pdf:
                page_plumber = pdf.pages[page_num]

                # Extract text chunks
                try:
                    text_chunks = self._extract_text_chunks(page_plumber, page_num)
                    page_chunks.extend(text_chunks)
                    self.logger.info(f"[{page_num + 1}/{total_pages}] Extracted {len(text_chunks)} text chunks")
                except Exception as e:
                    self.logger.error(f"Error extracting text from page {page_num + 1}: {e}")

        except Exception as e:
            self.logger.error(f"Error processing page {page_num + 1}: {e}")

        return page_chunks

    def extract_content(self, pdf_path: str) -> List[DocumentChunk]:
        """Extract all content types from PDF with parallel processing"""
        try:
            self.logger.info(f"Opening PDF: {pdf_path}")

            # Get total pages
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)

            self.logger.info(f"Processing {total_pages} pages in parallel (max 4 workers)")

            # Process pages in parallel (max 4 workers to avoid overwhelming CPU)
            all_chunks = []
            max_workers = min(4, total_pages)  # Don't use more workers than pages

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all page processing tasks
                future_to_page = {
                    executor.submit(self._process_single_page, pdf_path, page_num, total_pages): page_num
                    for page_num in range(total_pages)
                }

                # Collect results as they complete
                results = {}
                for future in as_completed(future_to_page):
                    page_num = future_to_page[future]
                    try:
                        page_chunks = future.result()
                        results[page_num] = page_chunks
                    except Exception as e:
                        self.logger.error(f"Page {page_num + 1} processing failed: {e}")
                        results[page_num] = []

                # Combine results in page order
                for page_num in sorted(results.keys()):
                    all_chunks.extend(results[page_num])

            self.logger.info(f"Total chunks extracted: {len(all_chunks)}")
            return all_chunks

        except Exception as e:
            self.logger.error(f"Critical error processing PDF {pdf_path}: {e}")
            raise
    
    def _extract_text_chunks(self, page, page_num: int) -> List[DocumentChunk]:
        """Extract and chunk text content"""
        text = page.extract_text()
        if not text:
            return []
            
        # Clean and normalize text
        text = self._clean_text(text)
        
        # Create chunks with overlap
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.config.CHUNK_SIZE - self.config.CHUNK_OVERLAP):
            chunk_words = words[i:i + self.config.CHUNK_SIZE]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) > 50:  # Only meaningful chunks
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    chunk_type='text',
                    page_number=page_num + 1,
                    metadata={
                        'word_count': len(chunk_words),
                        'char_count': len(chunk_text),
                        'chunk_index': len(chunks)
                    }
                ))
        
        return chunks
    
    def _extract_table_chunks_advanced(self, pdf_path: str, page_num: int) -> List[DocumentChunk]:
        """Extract table content using advanced multi-method extraction"""
        chunks = []

        try:
            # Use advanced table extractor (Camelot/Tabula/pdfplumber cascade)
            extracted_tables = self.table_extractor.extract_tables(pdf_path, page_num)

            for table in extracted_tables:
                # Create multiple representations of the table
                text_repr = table.text_representation
                csv_repr = table.csv_representation
                markdown_repr = table.markdown_representation
                nl_desc = table.natural_language_description

                # Create comprehensive content
                content = f"""TABLE {table.table_index + 1} (Extracted with {table.method}, Accuracy: {table.accuracy:.1f}%)

{nl_desc}

STRUCTURED DATA (Text Format):
{text_repr}

MARKDOWN FORMAT:
{markdown_repr}

CSV FORMAT:
{csv_repr}
"""

                chunks.append(DocumentChunk(
                    content=content,
                    chunk_type='table',
                    page_number=page_num + 1,
                    metadata={
                        'table_index': table.table_index,
                        'rows': len(table.dataframe),
                        'columns': len(table.dataframe.columns),
                        'extraction_method': table.method,
                        'accuracy': table.accuracy,
                        'bbox': table.bbox,
                        'has_headers': bool(list(table.dataframe.columns)),
                    }
                ))

            return chunks

        except Exception as e:
            self.logger.warning(f"Advanced table extraction failed: {e}, falling back to basic")
            # Fallback to basic pdfplumber extraction
            return []

    def _extract_table_chunks_fast(self, page, page_num: int) -> List[DocumentChunk]:
        """FAST table extraction using pdfplumber only (optimized for production speed)"""
        chunks = []

        try:
            # Extract tables using pdfplumber (10-50x faster than Camelot/Tabula)
            tables = page.extract_tables()

            if not tables:
                return []

            for table_idx, table_data in enumerate(tables):
                if not table_data or len(table_data) < 2:  # Skip empty or single-row tables
                    continue

                try:
                    # Convert to dataframe
                    df = pd.DataFrame(table_data[1:], columns=table_data[0])

                    # Clean the dataframe
                    df = df.dropna(how='all').fillna('')

                    if df.empty or len(df) == 0:
                        continue

                    # Create markdown representation (good for LLM)
                    markdown_repr = df.to_markdown(index=False) if hasattr(df, 'to_markdown') else df.to_string(index=False)

                    # Create simple natural language description
                    nl_desc = f"Table with {len(df)} rows and {len(df.columns)} columns"
                    if len(df.columns) > 0:
                        col_names = [str(col) for col in df.columns[:5]]
                        nl_desc += f". Columns: {', '.join(col_names)}"
                        if len(df.columns) > 5:
                            nl_desc += f" and {len(df.columns) - 5} more"

                    # Create content (simplified for speed)
                    content = f"""TABLE {table_idx + 1}

{nl_desc}

{markdown_repr}
"""

                    chunks.append(DocumentChunk(
                        content=content,
                        chunk_type='table',
                        page_number=page_num + 1,
                        metadata={
                            'table_index': table_idx,
                            'rows': len(df),
                            'columns': len(df.columns),
                            'extraction_method': 'pdfplumber-fast',
                        }
                    ))

                except Exception as e:
                    self.logger.debug(f"Skipped table {table_idx} on page {page_num + 1}: {e}")
                    continue

            return chunks

        except Exception as e:
            self.logger.error(f"Error in fast table extraction for page {page_num + 1}: {e}")
            return []

    def _extract_table_chunks(self, page, page_num: int) -> List[DocumentChunk]:
        """Extract table content (basic fallback method)"""
        tables = page.extract_tables()
        chunks = []

        for table_idx, table in enumerate(tables):
            if not table:
                continue

            # Convert table to DataFrame for better processing
            df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)

            # Create structured text representation
            table_text = self._table_to_text(df)

            # Also create CSV representation
            csv_repr = df.to_csv(index=False)

            chunks.append(DocumentChunk(
                content=f"TABLE DATA:\n{table_text}\n\nCSV FORMAT:\n{csv_repr}",
                chunk_type='table',
                page_number=page_num + 1,
                metadata={
                    'table_index': table_idx,
                    'rows': len(df),
                    'columns': len(df.columns) if df.columns is not None else 0,
                    'table_shape': df.shape,
                    'extraction_method': 'pdfplumber-basic'
                }
            ))

        return chunks
    
    def _extract_image_chunks(self, page, page_num: int) -> List[DocumentChunk]:
        """Extract and OCR image content"""
        chunks = []
        image_list = page.get_images()
        
        for img_idx, img in enumerate(image_list):
            try:
                # Extract image
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Resize if too large
                    if image.size[0] > self.config.MAX_IMAGE_SIZE[0] or image.size[1] > self.config.MAX_IMAGE_SIZE[1]:
                        image.thumbnail(self.config.MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
                    
                    # OCR the image
                    ocr_text = pytesseract.image_to_string(image)
                    
                    if len(ocr_text.strip()) > 20:  # Only if meaningful text found
                        chunks.append(DocumentChunk(
                            content=f"IMAGE CONTENT (OCR):\n{ocr_text}",
                            chunk_type='image',
                            page_number=page_num + 1,
                            metadata={
                                'image_index': img_idx,
                                'image_size': image.size,
                                'ocr_confidence': self._get_ocr_confidence(image)
                            }
                        ))
                
                pix = None
                
            except Exception as e:
                self.logger.warning(f"Could not process image {img_idx} on page {page_num}: {e}")
                continue
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\"\']+', '', text)
        return text.strip()
    
    def _table_to_text(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to readable text"""
        return df.to_string(index=False, na_rep='')
    
    def _get_ocr_confidence(self, image: Image.Image) -> float:
        """Get OCR confidence score"""
        try:
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            return np.mean(confidences) if confidences else 0.0
        except:
            return 0.0
