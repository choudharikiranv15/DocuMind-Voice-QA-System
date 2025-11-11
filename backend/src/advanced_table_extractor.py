# src/advanced_table_extractor.py
"""
Advanced table extraction using Camelot (lattice + stream) and Tabula as fallback.
Much better table detection and extraction than basic pdfplumber.
"""
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class ExtractedTable:
    """Represents an extracted table with metadata"""
    dataframe: pd.DataFrame
    page_number: int
    table_index: int
    method: str  # 'camelot-lattice', 'camelot-stream', 'tabula', 'pdfplumber'
    accuracy: float  # 0-100
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)

    @property
    def text_representation(self) -> str:
        """Get readable text representation of table"""
        return self.dataframe.to_string(index=False, na_rep='')

    @property
    def csv_representation(self) -> str:
        """Get CSV representation of table"""
        return self.dataframe.to_csv(index=False)

    @property
    def markdown_representation(self) -> str:
        """Get Markdown representation of table"""
        return self.dataframe.to_markdown(index=False)

    @property
    def natural_language_description(self) -> str:
        """Generate natural language description of table"""
        rows, cols = self.dataframe.shape
        headers = list(self.dataframe.columns) if self.dataframe.columns is not None else []

        desc = f"This is a table with {rows} rows and {cols} columns"
        if headers:
            desc += f". The columns are: {', '.join(str(h) for h in headers if h)}"
        desc += ".\n\n"

        # Add first few rows as example
        if rows > 0:
            desc += "Sample data:\n"
            desc += self.text_representation[:500]  # Limit to 500 chars

        return desc


class AdvancedTableExtractor:
    """
    Advanced table extraction using multiple methods with fallbacks:
    1. Camelot (lattice mode) - Best for bordered tables
    2. Camelot (stream mode) - Best for borderless tables
    3. Tabula - Fallback for complex tables
    4. pdfplumber - Final fallback
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Check which libraries are available
        self.camelot_available = self._check_camelot()
        self.tabula_available = self._check_tabula()

        self._log_capabilities()

    def _check_camelot(self) -> bool:
        """Check if Camelot is installed and working"""
        try:
            import camelot
            self.logger.info("✓ Camelot is available")
            return True
        except ImportError:
            self.logger.warning("✗ Camelot not installed. Install with: pip install camelot-py[cv]")
            return False

    def _check_tabula(self) -> bool:
        """Check if Tabula is installed"""
        try:
            import tabula
            self.logger.info("✓ Tabula is available")
            return True
        except ImportError:
            self.logger.warning("✗ Tabula not installed. Install with: pip install tabula-py")
            return False

    def _log_capabilities(self):
        """Log available extraction methods"""
        methods = []
        if self.camelot_available:
            methods.append("Camelot (lattice + stream)")
        if self.tabula_available:
            methods.append("Tabula")
        methods.append("pdfplumber (basic)")

        self.logger.info(f"Table extraction methods available: {', '.join(methods)}")

    def extract_tables(self, pdf_path: str, page_num: int) -> List[ExtractedTable]:
        """
        Extract all tables from a specific page using best available method.

        Args:
            pdf_path: Path to PDF file
            page_num: Page number (0-indexed)

        Returns:
            List of ExtractedTable objects
        """
        tables = []

        # Try Camelot first (best quality)
        if self.camelot_available:
            tables.extend(self._extract_with_camelot(pdf_path, page_num))

        # If no tables found, try Tabula
        if not tables and self.tabula_available:
            tables.extend(self._extract_with_tabula(pdf_path, page_num))

        # If still no tables, use pdfplumber as final fallback
        if not tables:
            tables.extend(self._extract_with_pdfplumber(pdf_path, page_num))

        self.logger.info(f"Extracted {len(tables)} tables from page {page_num + 1}")
        return tables

    def _extract_with_camelot(self, pdf_path: str, page_num: int) -> List[ExtractedTable]:
        """Extract tables using Camelot (lattice + stream modes)"""
        try:
            import camelot

            tables = []
            page_str = str(page_num + 1)  # Camelot uses 1-indexed pages

            # Try lattice mode first (best for bordered tables)
            try:
                lattice_tables = camelot.read_pdf(
                    pdf_path,
                    pages=page_str,
                    flavor='lattice',
                    line_scale=40
                )

                for idx, table in enumerate(lattice_tables):
                    if table.parsing_report['accuracy'] > 50:  # Only high-confidence tables
                        tables.append(ExtractedTable(
                            dataframe=table.df,
                            page_number=page_num + 1,
                            table_index=idx,
                            method='camelot-lattice',
                            accuracy=table.parsing_report['accuracy'],
                            bbox=table._bbox if hasattr(table, '_bbox') else (0, 0, 0, 0)
                        ))
                        self.logger.debug(
                            f"Camelot lattice: Found table {idx} "
                            f"(accuracy: {table.parsing_report['accuracy']:.1f}%)"
                        )
            except Exception as e:
                self.logger.debug(f"Camelot lattice failed: {e}")

            # If no tables found with lattice, try stream mode (borderless tables)
            if not tables:
                try:
                    stream_tables = camelot.read_pdf(
                        pdf_path,
                        pages=page_str,
                        flavor='stream',
                        edge_tol=50
                    )

                    for idx, table in enumerate(stream_tables):
                        if table.parsing_report['accuracy'] > 40:  # Lower threshold for stream
                            tables.append(ExtractedTable(
                                dataframe=table.df,
                                page_number=page_num + 1,
                                table_index=idx,
                                method='camelot-stream',
                                accuracy=table.parsing_report['accuracy'],
                                bbox=table._bbox if hasattr(table, '_bbox') else (0, 0, 0, 0)
                            ))
                            self.logger.debug(
                                f"Camelot stream: Found table {idx} "
                                f"(accuracy: {table.parsing_report['accuracy']:.1f}%)"
                            )
                except Exception as e:
                    self.logger.debug(f"Camelot stream failed: {e}")

            return tables

        except Exception as e:
            self.logger.warning(f"Camelot extraction failed: {e}")
            return []

    def _extract_with_tabula(self, pdf_path: str, page_num: int) -> List[ExtractedTable]:
        """Extract tables using Tabula"""
        try:
            import tabula

            tables = []

            # Read tables from specific page
            dfs = tabula.read_pdf(
                pdf_path,
                pages=page_num + 1,  # Tabula uses 1-indexed pages
                multiple_tables=True,
                lattice=True,
                stream=True,
                guess=True
            )

            for idx, df in enumerate(dfs):
                if df is not None and not df.empty:
                    # Clean the dataframe
                    df = self._clean_dataframe(df)

                    if len(df) > 0 and len(df.columns) > 0:
                        tables.append(ExtractedTable(
                            dataframe=df,
                            page_number=page_num + 1,
                            table_index=idx,
                            method='tabula',
                            accuracy=75.0,  # Tabula doesn't provide accuracy scores
                            bbox=(0, 0, 0, 0)
                        ))
                        self.logger.debug(f"Tabula: Found table {idx} ({len(df)} rows)")

            return tables

        except Exception as e:
            self.logger.warning(f"Tabula extraction failed: {e}")
            return []

    def _extract_with_pdfplumber(self, pdf_path: str, page_num: int) -> List[ExtractedTable]:
        """Extract tables using pdfplumber (basic fallback)"""
        try:
            import pdfplumber

            tables = []

            with pdfplumber.open(pdf_path) as pdf:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    raw_tables = page.extract_tables()

                    for idx, table in enumerate(raw_tables):
                        if table and len(table) > 1:  # At least header + 1 row
                            # Convert to DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df = self._clean_dataframe(df)

                            if len(df) > 0:
                                tables.append(ExtractedTable(
                                    dataframe=df,
                                    page_number=page_num + 1,
                                    table_index=idx,
                                    method='pdfplumber',
                                    accuracy=60.0,  # Estimate
                                    bbox=(0, 0, 0, 0)
                                ))
                                self.logger.debug(f"pdfplumber: Found table {idx}")

            return tables

        except Exception as e:
            self.logger.warning(f"pdfplumber extraction failed: {e}")
            return []

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize DataFrame"""
        # Remove completely empty rows and columns
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')

        # Replace None with empty string
        df = df.fillna('')

        # Strip whitespace from all string cells
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

        # Remove rows that are all empty strings
        df = df[~(df.astype(str) == '').all(axis=1)]

        return df

    def extract_all_tables_from_pdf(self, pdf_path: str) -> Dict[int, List[ExtractedTable]]:
        """
        Extract all tables from entire PDF.

        Returns:
            Dictionary mapping page numbers to list of tables
        """
        import fitz

        all_tables = {}

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            doc.close()

            for page_num in range(total_pages):
                tables = self.extract_tables(pdf_path, page_num)
                if tables:
                    all_tables[page_num + 1] = tables

            total_tables = sum(len(t) for t in all_tables.values())
            self.logger.info(f"Extracted {total_tables} tables from {len(all_tables)} pages")

        except Exception as e:
            self.logger.error(f"Failed to extract tables from PDF: {e}")

        return all_tables
