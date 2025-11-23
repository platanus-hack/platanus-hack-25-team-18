"""
Módulo para análisis de texto usando la API de Anthropic (Claude).
"""
import logging
import json
import time
from typing import Optional, Dict, List
from anthropic import Anthropic, APIError, RateLimitError
from src.config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS_OUTPUT_CHUNK
from src.prompts import CHUNK_ANALYSIS_PROMPT, METADATA_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Analizador de texto usando Claude de Anthropic."""

    def __init__(self, api_key: str = ANTHROPIC_API_KEY, model: str = MODEL_NAME):
        """
        Inicializa el analizador.

        Args:
            api_key: API key de Anthropic
            model: Nombre del modelo a usar
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def analyze_chunk(
        self,
        chunk_text: str,
        chunk_number: int,
        total_chunks: int,
        max_retries: int = 3
    ) -> Optional[Dict]:
        """
        Analiza un chunk de texto y extrae información estructurada.

        Args:
            chunk_text: Texto del chunk a analizar
            chunk_number: Número del chunk actual
            total_chunks: Total de chunks
            max_retries: Intentos máximos en caso de error

        Returns:
            Diccionario con el análisis o None si hay error
        """
        self.logger.info(
            f"Analizando chunk {chunk_number}/{total_chunks} "
            f"({len(chunk_text):,} caracteres)"
        )

        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=MAX_TOKENS_OUTPUT_CHUNK,
                    temperature=0,
                    system=CHUNK_ANALYSIS_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Fragmento {chunk_number}/{total_chunks} del programa:\n\n{chunk_text}"
                        }
                    ]
                )

                # Registrar uso de tokens
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens

                self.logger.debug(
                    f"Tokens - Input: {response.usage.input_tokens}, "
                    f"Output: {response.usage.output_tokens}"
                )

                # Extraer y parsear respuesta
                response_text = response.content[0].text.strip()

                # Intentar parsear el JSON
                try:
                    analysis = json.loads(response_text)
                    self.logger.info(
                        f"✓ Chunk {chunk_number} analizado: "
                        f"{len(analysis.get('categorias_encontradas', []))} categorías encontradas"
                    )

                    # Rate limiting: esperar antes de siguiente llamada
                    self.logger.debug("Esperando 15s para respetar rate limits...")
                    time.sleep(15)

                    return analysis

                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parseando JSON del chunk {chunk_number}: {e}")
                    self.logger.debug(f"Respuesta recibida: {response_text[:500]}...")
                    return None

            except RateLimitError as e:
                wait_time = 2 ** attempt  # Backoff exponencial
                self.logger.warning(
                    f"Rate limit alcanzado. Esperando {wait_time}s... "
                    f"(intento {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)

            except APIError as e:
                self.logger.error(f"Error de API en chunk {chunk_number}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return None

            except Exception as e:
                self.logger.error(f"Error inesperado analizando chunk {chunk_number}: {e}")
                return None

        self.logger.error(f"Falló análisis del chunk {chunk_number} después de {max_retries} intentos")
        return None

    def extract_metadata(self, first_pages_text: str) -> Dict[str, str]:
        """
        Extrae metadata del candidato de las primeras páginas.

        Args:
            first_pages_text: Texto de las primeras páginas

        Returns:
            Diccionario con metadata
        """
        try:
            prompt = METADATA_EXTRACTION_PROMPT.format(texto=first_pages_text[:5000])

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Registrar tokens
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens

            # Parsear respuesta
            response_text = response.content[0].text.strip()
            metadata = json.loads(response_text)

            self.logger.info(f"✓ Metadata extraída: {metadata.get('candidato', 'N/A')}")

            # Rate limiting: esperar antes de siguiente llamada
            self.logger.debug("Esperando 15s para respetar rate limits...")
            time.sleep(15)

            return metadata

        except Exception as e:
            self.logger.error(f"Error extrayendo metadata: {e}")
            return {
                "candidato": "No especificado",
                "partido_coalicion": "No especificado",
                "año": "No especificado"
            }

    def get_token_usage(self) -> Dict[str, int]:
        """
        Retorna el uso total de tokens.

        Returns:
            Diccionario con uso de tokens
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }

    def estimate_cost(self) -> float:
        """
        Estima el costo en USD basado en el uso de tokens.
        Precios aproximados para Claude 3.5 Sonnet (verificar precios actuales).

        Returns:
            Costo estimado en USD
        """
        # Precios aproximados (verificar en https://www.anthropic.com/pricing)
        INPUT_COST_PER_1M = 3.00  # USD por millón de tokens de input
        OUTPUT_COST_PER_1M = 15.00  # USD por millón de tokens de output

        input_cost = (self.total_input_tokens / 1_000_000) * INPUT_COST_PER_1M
        output_cost = (self.total_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

        return input_cost + output_cost
