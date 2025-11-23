"""
Módulo para sintetizar múltiples análisis parciales en un resultado consolidado.
"""
import logging
import json
import time
from typing import List, Dict
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, MODEL_NAME, MAX_TOKENS_OUTPUT_SYNTHESIS, CATEGORIAS
from src.prompts import SYNTHESIS_PROMPT

logger = logging.getLogger(__name__)


class AnalysisSynthesizer:
    """Sintetiza análisis parciales en un resultado consolidado."""

    def __init__(self, api_key: str = ANTHROPIC_API_KEY, model: str = MODEL_NAME):
        """
        Inicializa el sintetizador.

        Args:
            api_key: API key de Anthropic
            model: Nombre del modelo a usar
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)

    def synthesize(
        self,
        partial_analyses: List[Dict],
        original_text_sample: str,
        metadata: Dict[str, str]
    ) -> Dict:
        """
        Sintetiza múltiples análisis parciales en uno consolidado.

        Args:
            partial_analyses: Lista de análisis parciales de chunks
            original_text_sample: Muestra del texto original (primeras páginas)
            metadata: Metadata ya extraída

        Returns:
            Análisis consolidado
        """
        self.logger.info(f"Sintetizando {len(partial_analyses)} análisis parciales...")

        # Filtrar análisis vacíos
        valid_analyses = [
            a for a in partial_analyses
            if a and a.get("categorias_encontradas")
        ]

        if not valid_analyses:
            self.logger.warning("No hay análisis válidos para sintetizar")
            return self._empty_result(metadata)

        # Preparar el prompt
        analyses_json = json.dumps(valid_analyses, ensure_ascii=False, indent=2)
        sample_text = original_text_sample[:5000]  # Primeros 5000 caracteres

        prompt_formatted = SYNTHESIS_PROMPT.replace(
            "{analisis_parciales}", analyses_json
        ).replace(
            "{texto_original}", sample_text
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS_OUTPUT_SYNTHESIS,
                temperature=0,
                system=prompt_formatted,
                messages=[
                    {
                        "role": "user",
                        "content": "Por favor, consolida todos los análisis parciales en un análisis completo siguiendo el formato JSON especificado."
                    }
                ]
            )

            # Parsear respuesta
            response_text = response.content[0].text.strip()

            try:
                synthesis = json.loads(response_text)

                # Validar estructura
                if "categorias" not in synthesis:
                    self.logger.error("La síntesis no tiene la estructura esperada")
                    return self._fallback_synthesis(valid_analyses, metadata)

                # Asegurar que metadata esté presente
                if "metadata" not in synthesis or not synthesis["metadata"]:
                    synthesis["metadata"] = metadata

                self.logger.info(
                    f"✓ Síntesis completada: {len(synthesis.get('categorias', []))} categorías"
                )

                # Rate limiting: esperar antes de siguiente llamada
                self.logger.debug("Esperando 15s para respetar rate limits...")
                time.sleep(15)

                return synthesis

            except json.JSONDecodeError as e:
                self.logger.error(f"Error parseando JSON de síntesis: {e}")
                self.logger.debug(f"Respuesta: {response_text[:500]}...")
                return self._fallback_synthesis(valid_analyses, metadata)

        except Exception as e:
            self.logger.error(f"Error en síntesis: {e}")
            return self._fallback_synthesis(valid_analyses, metadata)

    def _fallback_synthesis(
        self,
        partial_analyses: List[Dict],
        metadata: Dict[str, str]
    ) -> Dict:
        """
        Síntesis de respaldo (simple merge) si falla la síntesis por LLM.

        Args:
            partial_analyses: Análisis parciales
            metadata: Metadata del candidato

        Returns:
            Síntesis básica
        """
        self.logger.warning("Usando síntesis de respaldo (merge simple)")

        # Consolidar categorías
        categories_map = {}

        for analysis in partial_analyses:
            for cat_data in analysis.get("categorias_encontradas", []):
                cat_name = cat_data.get("categoria")

                if not cat_name:
                    continue

                if cat_name not in categories_map:
                    categories_map[cat_name] = {
                        "categoria": cat_name,
                        "analisis_perspectiva": cat_data.get("analisis_perspectiva", {}),
                        "propuestas_clave": [],
                        "citas_textuales": []
                    }

                # Agregar propuestas
                propuestas = cat_data.get("propuestas_clave", [])
                categories_map[cat_name]["propuestas_clave"].extend(propuestas)

                # Agregar citas
                citas = cat_data.get("citas_textuales", [])
                categories_map[cat_name]["citas_textuales"].extend(citas)

        # Eliminar duplicados en citas
        for cat in categories_map.values():
            cat["citas_textuales"] = list(set(cat["citas_textuales"]))[:5]
            cat["presente"] = True

        # Asegurar que todas las 16 categorías estén presentes
        for expected_cat in CATEGORIAS:
            if expected_cat not in categories_map:
                categories_map[expected_cat] = {
                    "categoria": expected_cat,
                    "presente": False,
                    "analisis_perspectiva": {},
                    "propuestas_clave": [],
                    "citas_textuales": []
                }

        return {
            "metadata": metadata,
            "categorias": list(categories_map.values())
        }

    def _empty_result(self, metadata: Dict[str, str]) -> Dict:
        """
        Resultado vacío con las 16 categorías marcadas como no presentes.

        Args:
            metadata: Metadata del candidato

        Returns:
            Resultado vacío
        """
        categorias = []
        for cat_name in CATEGORIAS:
            categorias.append({
                "categoria": cat_name,
                "presente": False,
                "analisis_perspectiva": {},
                "propuestas_clave": [],
                "citas_textuales": []
            })

        return {
            "metadata": metadata,
            "categorias": categorias
        }
