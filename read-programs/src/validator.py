"""
Módulo para validar completitud del análisis y re-analizar categorías faltantes.
"""
import logging
from typing import Dict, List, Set
from src.config import CATEGORIAS, ENABLE_VALIDATION, REANALYZE_MISSING_CATEGORIES

logger = logging.getLogger(__name__)


class AnalysisValidator:
    """Validador de completitud de análisis de programas presidenciales."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.expected_categories = set(CATEGORIAS)

    def validate_completeness(self, synthesis: Dict) -> Dict[str, any]:
        """
        Valida que el análisis incluya las 16 categorías.

        Args:
            synthesis: Síntesis consolidada del análisis

        Returns:
            Diccionario con resultados de validación
        """
        if not ENABLE_VALIDATION:
            self.logger.info("Validación deshabilitada en configuración")
            return {
                "is_complete": True,
                "found_categories": set(),
                "missing_categories": set(),
                "coverage_percentage": 100.0
            }

        # Extraer categorías encontradas
        found_categories = set()
        for cat_data in synthesis.get('categorias', []):
            cat_name = cat_data.get('categoria')
            is_present = cat_data.get('presente', True)

            if cat_name and is_present:
                found_categories.add(cat_name)

        # Identificar categorías faltantes
        missing_categories = self.expected_categories - found_categories

        # Calcular cobertura
        coverage = (len(found_categories) / len(self.expected_categories)) * 100

        # Logging
        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info("VALIDACIÓN DE COMPLETITUD")
        self.logger.info("=" * 60)
        self.logger.info(f"Categorías encontradas: {len(found_categories)}/16 ({coverage:.1f}%)")

        if missing_categories:
            self.logger.warning(f"Categorías faltantes ({len(missing_categories)}):")
            for cat in sorted(missing_categories):
                self.logger.warning(f"  ✗ {cat}")
        else:
            self.logger.info("✓ Análisis completo - todas las categorías presentes")

        self.logger.info(f"Categorías encontradas:")
        for cat in sorted(found_categories):
            self.logger.info(f"  ✓ {cat}")
        self.logger.info("=" * 60)
        self.logger.info("")

        return {
            "is_complete": len(missing_categories) == 0,
            "found_categories": found_categories,
            "missing_categories": missing_categories,
            "coverage_percentage": coverage
        }

    def should_reanalyze(self, validation_result: Dict) -> bool:
        """
        Determina si se debe re-analizar para buscar categorías faltantes.

        Args:
            validation_result: Resultado de validate_completeness

        Returns:
            True si se debe re-analizar
        """
        if not REANALYZE_MISSING_CATEGORIES:
            return False

        missing = validation_result.get('missing_categories', set())

        # Re-analizar si faltan categorías pero no si faltan demasiadas
        # (probablemente el programa no las cubre)
        if 0 < len(missing) <= 8:  # Re-analizar si faltan 1-8 categorías
            self.logger.info(
                f"Re-análisis recomendado para {len(missing)} categorías faltantes"
            )
            return True
        elif len(missing) > 8:
            self.logger.info(
                f"No se re-analiza: {len(missing)} categorías faltantes "
                f"(probablemente el programa no las cubre)"
            )
            return False

        return False

    def merge_reanalysis(
        self,
        original_synthesis: Dict,
        reanalysis_results: List[Dict]
    ) -> Dict:
        """
        Integra resultados de re-análisis en la síntesis original.

        Args:
            original_synthesis: Síntesis original
            reanalysis_results: Resultados del re-análisis

        Returns:
            Síntesis actualizada
        """
        self.logger.info("Integrando resultados de re-análisis...")

        # Crear mapa de categorías existentes
        categories_map = {}
        for cat_data in original_synthesis.get('categorias', []):
            cat_name = cat_data.get('categoria')
            if cat_name:
                categories_map[cat_name] = cat_data

        # Integrar nuevas categorías del re-análisis
        added_count = 0
        for reanalysis in reanalysis_results:
            for cat_data in reanalysis.get('categorias_encontradas', []):
                cat_name = cat_data.get('categoria')

                if cat_name and cat_name not in categories_map:
                    # Agregar nueva categoría
                    new_category = {
                        "categoria": cat_name,
                        "presente": True,
                        "analisis_perspectiva": cat_data.get('analisis_perspectiva', {}),
                        "propuestas_clave": cat_data.get('propuestas_clave', []),
                        "citas_textuales": cat_data.get('citas_textuales', [])
                    }
                    categories_map[cat_name] = new_category
                    added_count += 1
                    self.logger.info(f"  ✓ Agregada categoría: {cat_name}")

        # Reconstruir lista de categorías
        original_synthesis['categorias'] = list(categories_map.values())

        # Asegurar que todas las 16 estén presentes
        for expected_cat in CATEGORIAS:
            if expected_cat not in categories_map:
                # Agregar categoría vacía
                original_synthesis['categorias'].append({
                    "categoria": expected_cat,
                    "presente": False,
                    "analisis_perspectiva": {},
                    "propuestas_clave": [],
                    "citas_textuales": []
                })

        self.logger.info(f"Re-análisis completado: {added_count} nuevas categorías agregadas")

        return original_synthesis

    def log_final_summary(self, synthesis: Dict, pdf_name: str):
        """
        Genera un resumen final del análisis para logging.

        Args:
            synthesis: Síntesis final
            pdf_name: Nombre del PDF analizado
        """
        self.logger.info("")
        self.logger.info("*" * 70)
        self.logger.info(f"RESUMEN FINAL: {pdf_name}")
        self.logger.info("*" * 70)

        metadata = synthesis.get('metadata', {})
        self.logger.info(f"Candidato: {metadata.get('candidato', 'No especificado')}")
        self.logger.info(f"Partido: {metadata.get('partido_coalicion', 'No especificado')}")
        self.logger.info(f"Año: {metadata.get('año', 'No especificado')}")
        self.logger.info("")

        # Contar propuestas y citas por categoría
        total_propuestas = 0
        total_citas = 0
        categorias_con_contenido = 0

        for cat_data in synthesis.get('categorias', []):
            if cat_data.get('presente', True):
                categorias_con_contenido += 1
                propuestas = len(cat_data.get('propuestas_clave', []))
                citas = len(cat_data.get('citas_textuales', []))
                total_propuestas += propuestas
                total_citas += citas

                if propuestas > 0 or citas > 0:
                    self.logger.info(
                        f"✓ {cat_data['categoria']}: "
                        f"{propuestas} propuestas, {citas} citas"
                    )

        self.logger.info("")
        self.logger.info(f"Total categorías con contenido: {categorias_con_contenido}/16")
        self.logger.info(f"Total propuestas extraídas: {total_propuestas}")
        self.logger.info(f"Total citas textuales: {total_citas}")
        self.logger.info("*" * 70)
        self.logger.info("")


def validate_analysis(synthesis: Dict, pdf_name: str = "") -> Dict:
    """
    Función auxiliar para validar un análisis.

    Args:
        synthesis: Síntesis a validar
        pdf_name: Nombre del PDF (opcional, para logging)

    Returns:
        Resultado de validación
    """
    validator = AnalysisValidator()
    result = validator.validate_completeness(synthesis)

    if pdf_name:
        validator.log_final_summary(synthesis, pdf_name)

    return result
