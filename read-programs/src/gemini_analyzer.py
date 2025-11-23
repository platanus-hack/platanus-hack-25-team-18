"""
Módulo para análisis de texto usando la API de Google Gemini.
"""
import logging
import json
import time
from typing import Optional, Dict
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL, MAX_TOKENS_OUTPUT_CHUNK
from src.prompts import CHUNK_ANALYSIS_PROMPT, METADATA_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Analizador de texto usando Google Gemini."""

    def __init__(self, api_key: str = GEMINI_API_KEY, model: str = GEMINI_MODEL):
        """
        Inicializa el analizador.

        Args:
            api_key: API key de Google
            model: Nombre del modelo a usar
        """
        genai.configure(api_key=api_key)

        # Configuración de generación
        self.generation_config = {
            "temperature": 0,
            "max_output_tokens": MAX_TOKENS_OUTPUT_CHUNK,
            "response_mime_type": "application/json",
        }

        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config=self.generation_config,
        )

        self.model_name = model
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

        prompt = f"""{CHUNK_ANALYSIS_PROMPT}

Fragmento {chunk_number}/{total_chunks} del programa:

{chunk_text}
"""

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)

                # Registrar uso de tokens si está disponible
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    self.total_input_tokens += response.usage_metadata.prompt_token_count
                    self.total_output_tokens += response.usage_metadata.candidates_token_count

                    self.logger.debug(
                        f"Tokens - Input: {response.usage_metadata.prompt_token_count}, "
                        f"Output: {response.usage_metadata.candidates_token_count}"
                    )

                # Extraer texto de la respuesta
                response_text = response.text.strip()

                # Intentar parsear el JSON
                try:
                    analysis = json.loads(response_text)
                    self.logger.info(
                        f"✓ Chunk {chunk_number} analizado: "
                        f"{len(analysis.get('categorias_encontradas', []))} categorías encontradas"
                    )
                    return analysis

                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parseando JSON del chunk {chunk_number}: {e}")
                    self.logger.warning(f"Respuesta recibida (primeros 1000 chars): {response_text[:1000]}...")

                    # Intentar con otro intento
                    if attempt < max_retries - 1:
                        self.logger.info(f"Reintentando chunk {chunk_number}... (intento {attempt + 2}/{max_retries})")
                        time.sleep(2)
                        continue
                    else:
                        # En el último intento, retornar None para que falle
                        self.logger.error(f"No se pudo parsear JSON después de {max_retries} intentos")
                        return None

            except Exception as e:
                error_str = str(e)

                # Manejar rate limits
                if "429" in error_str or "quota" in error_str.lower():
                    wait_time = 2 ** attempt
                    self.logger.warning(
                        f"Rate limit alcanzado. Esperando {wait_time}s... "
                        f"(intento {attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error analizando chunk {chunk_number}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    else:
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

            response = self.model.generate_content(prompt)

            # Registrar tokens
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                self.total_input_tokens += response.usage_metadata.prompt_token_count
                self.total_output_tokens += response.usage_metadata.candidates_token_count

            # Parsear respuesta
            response_text = response.text.strip()
            metadata = json.loads(response_text)

            # Si Gemini devolvió una lista con un dict, extraer el primer elemento
            if isinstance(metadata, list) and len(metadata) > 0 and isinstance(metadata[0], dict):
                self.logger.warning(f"Metadata devuelta como lista, extrayendo primer elemento")
                metadata = metadata[0]

            # Validar que sea un diccionario
            if not isinstance(metadata, dict):
                self.logger.error(f"Metadata no es un diccionario, es {type(metadata)}: {metadata}")
                return {
                    "candidato": "No especificado",
                    "partido_coalicion": "No especificado",
                    "año": "No especificado"
                }

            self.logger.info(f"✓ Metadata extraída: {metadata.get('candidato', 'N/A')}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error extrayendo metadata: {e}")
            self.logger.debug(f"Response text: {response_text[:500] if 'response_text' in locals() else 'N/A'}")
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
        Precios de Gemini 2.0 Flash (verificar precios actuales).

        Returns:
            Costo estimado en USD
        """
        # Precios aproximados de Gemini 2.0 Flash (verificar en https://ai.google.dev/pricing)
        # Para prompts <= 128K tokens
        INPUT_COST_PER_1M = 0.00  # Gratis hasta cierto límite
        OUTPUT_COST_PER_1M = 0.00  # Gratis hasta cierto límite

        # Si supera el límite gratuito, usar precios reales
        # INPUT_COST_PER_1M = 0.10  # USD por millón de tokens de input
        # OUTPUT_COST_PER_1M = 0.40  # USD por millón de tokens de output

        input_cost = (self.total_input_tokens / 1_000_000) * INPUT_COST_PER_1M
        output_cost = (self.total_output_tokens / 1_000_000) * OUTPUT_COST_PER_1M

        return input_cost + output_cost
