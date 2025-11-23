"""
Sistema de Análisis de Programas Presidenciales.

Este paquete proporciona herramientas para extraer, analizar y sintetizar
información de programas presidenciales en formato PDF.
"""

__version__ = "1.0.0"
__author__ = "Data Presidentes"

from src.pdf_extractor import PDFExtractor, extract_pdf_text
from src.text_chunker import TextChunker, chunk_text_smart
from src.llm_analyzer import LLMAnalyzer
from src.synthesizer import AnalysisSynthesizer

__all__ = [
    "PDFExtractor",
    "extract_pdf_text",
    "TextChunker",
    "chunk_text_smart",
    "LLMAnalyzer",
    "AnalysisSynthesizer",
]
