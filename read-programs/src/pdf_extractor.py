"""
Módulo para extracción de texto de archivos PDF usando PyMuPDF (fitz).
"""
import logging
from pathlib import Path
from typing import Optional, Dict
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extractor de texto de archivos PDF."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract_text(self, pdf_path: Path) -> Optional[str]:
        """
        Extrae todo el texto de un archivo PDF o TXT.

        Args:
            pdf_path: Ruta al archivo PDF o TXT

        Returns:
            Texto extraído o None si hay error
        """
        try:
            self.logger.info(f"Extrayendo texto de: {pdf_path.name}")

            # Si es archivo TXT, leer directamente
            if pdf_path.suffix.lower() == '.txt':
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    complete_text = f.read()

                self.logger.info(
                    f"✓ Extracción completada (TXT): "
                    f"{len(complete_text):,} caracteres"
                )
                return complete_text

            # Si es PDF, usar PyMuPDF
            # Abrir el PDF
            doc = fitz.open(pdf_path)

            # Extraer texto de todas las páginas
            full_text = []
            total_pages = len(doc)

            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text()

                if text.strip():  # Solo agregar si la página tiene texto
                    full_text.append(text)

                if (page_num + 1) % 10 == 0:
                    self.logger.debug(f"Procesadas {page_num + 1}/{total_pages} páginas")

            doc.close()

            # Unir todo el texto
            complete_text = "\n\n".join(full_text)

            self.logger.info(
                f"✓ Extracción completada: {total_pages} páginas, "
                f"{len(complete_text):,} caracteres"
            )

            return complete_text

        except Exception as e:
            self.logger.error(f"Error extrayendo texto de {pdf_path.name}: {str(e)}")
            return None

    def extract_metadata(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extrae metadata del PDF.

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Diccionario con metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "total_pages": len(doc),
                "file_size_mb": pdf_path.stat().st_size / (1024 * 1024)
            }
            doc.close()

            return metadata

        except Exception as e:
            self.logger.error(f"Error extrayendo metadata de {pdf_path.name}: {str(e)}")
            return {}

    def extract_first_pages(self, pdf_path: Path, num_pages: int = 3) -> Optional[str]:
        """
        Extrae el texto de las primeras N páginas (útil para metadata).
        Para archivos TXT, extrae los primeros 10000 caracteres.

        Args:
            pdf_path: Ruta al archivo PDF o TXT
            num_pages: Número de páginas a extraer (solo para PDF)

        Returns:
            Texto de las primeras páginas/caracteres o None si hay error
        """
        try:
            # Si es archivo TXT, retornar primeros 10000 caracteres
            if pdf_path.suffix.lower() == '.txt':
                with open(pdf_path, 'r', encoding='utf-8') as f:
                    text = f.read(10000)  # Primeros 10K caracteres
                return text

            # Si es PDF
            doc = fitz.open(pdf_path)

            first_pages_text = []
            pages_to_extract = min(num_pages, len(doc))

            for page_num in range(pages_to_extract):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    first_pages_text.append(text)

            doc.close()

            return "\n\n".join(first_pages_text)

        except Exception as e:
            self.logger.error(f"Error extrayendo primeras páginas de {pdf_path.name}: {str(e)}")
            return None


def extract_pdf_text(pdf_path: Path) -> Optional[str]:
    """
    Función auxiliar para extraer texto de un PDF.

    Args:
        pdf_path: Ruta al archivo PDF

    Returns:
        Texto extraído o None si hay error
    """
    extractor = PDFExtractor()
    return extractor.extract_text(pdf_path)
