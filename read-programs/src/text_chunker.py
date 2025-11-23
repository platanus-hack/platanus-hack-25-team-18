"""
Módulo para dividir texto largo en chunks manejables para el LLM.
"""
import logging
from typing import List
from src.config import MAX_CHARS_PER_CHUNK, CHUNK_OVERLAP_CHARS

logger = logging.getLogger(__name__)


class TextChunker:
    """Divide texto en chunks con overlap para mantener contexto."""

    def __init__(
        self,
        max_chars: int = MAX_CHARS_PER_CHUNK,
        overlap_chars: int = CHUNK_OVERLAP_CHARS
    ):
        """
        Inicializa el chunker.

        Args:
            max_chars: Máximo de caracteres por chunk
            overlap_chars: Caracteres de overlap entre chunks
        """
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars
        self.logger = logging.getLogger(self.__class__.__name__)

    def chunk_text(self, text: str) -> List[str]:
        """
        Divide el texto en chunks con overlap inteligente.

        Args:
            text: Texto completo a dividir

        Returns:
            Lista de chunks de texto
        """
        if len(text) <= self.max_chars:
            self.logger.info("Texto completo cabe en un solo chunk")
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # Calcular el final del chunk
            end = start + self.max_chars

            # Si no es el último chunk, buscar un buen punto de corte
            if end < len(text):
                # Buscar el último salto de párrafo en la ventana de overlap
                search_start = max(start, end - 500)
                last_paragraph = text.rfind("\n\n", search_start, end)

                # Si no hay párrafo, buscar un punto seguido
                if last_paragraph == -1:
                    last_sentence = text.rfind(". ", search_start, end)
                    if last_sentence != -1:
                        end = last_sentence + 1

                else:
                    end = last_paragraph + 2  # Incluir los dos \n

            # Extraer el chunk
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)
                self.logger.debug(
                    f"Chunk {len(chunks)}: {len(chunk):,} caracteres "
                    f"(posición {start:,} - {end:,})"
                )

            # Avanzar con overlap
            start = end - self.overlap_chars

            # Evitar loop infinito
            if start <= 0 and len(chunks) > 0:
                break

        self.logger.info(
            f"Texto dividido en {len(chunks)} chunks "
            f"(promedio: {sum(len(c) for c in chunks) // len(chunks):,} caracteres/chunk)"
        )

        return chunks

    def chunk_by_pages(self, text: str, chars_per_page: int = 3000) -> List[str]:
        """
        Divide el texto simulando páginas.

        Args:
            text: Texto completo
            chars_per_page: Caracteres aproximados por página

        Returns:
            Lista de chunks (agrupaciones de páginas)
        """
        # Dividir por saltos de página si existen
        if "\f" in text:  # Form feed character
            pages = text.split("\f")
        else:
            # Simular páginas por longitud
            pages = []
            for i in range(0, len(text), chars_per_page):
                pages.append(text[i:i + chars_per_page])

        # Agrupar páginas en chunks
        chunks = []
        current_chunk = []
        current_length = 0

        for page in pages:
            page_length = len(page)

            if current_length + page_length > self.max_chars and current_chunk:
                # Guardar chunk actual
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [page]
                current_length = page_length
            else:
                current_chunk.append(page)
                current_length += page_length

        # Agregar último chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        self.logger.info(f"Texto dividido en {len(chunks)} chunks por páginas")

        return chunks


def chunk_text_smart(text: str) -> List[str]:
    """
    Función auxiliar para dividir texto con configuración por defecto.

    Args:
        text: Texto a dividir

    Returns:
        Lista de chunks
    """
    chunker = TextChunker()
    return chunker.chunk_text(text)
