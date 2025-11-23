#!/usr/bin/env python3
"""
Script principal para analizar programas presidenciales.

Uso:
    python main.py
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from src.config import PDFS_DIR, OUTPUT_FILE, LOGS_DIR, LOG_FORMAT, LOG_DATE_FORMAT, LLM_PROVIDER
from src.pdf_extractor import PDFExtractor
from src.text_chunker import TextChunker
from src.validator import AnalysisValidator

# Importar el analizador correcto según el proveedor
if LLM_PROVIDER == "gemini":
    from src.gemini_analyzer import GeminiAnalyzer as Analyzer
    from src.gemini_synthesizer import GeminiSynthesizer as Synthesizer
else:
    from src.llm_analyzer import LLMAnalyzer as Analyzer
    from src.synthesizer import AnalysisSynthesizer as Synthesizer


def setup_logging() -> logging.Logger:
    """Configura el sistema de logging."""
    # Crear nombre de archivo de log con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"analisis_{timestamp}.log"

    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("SISTEMA DE ANÁLISIS DE PROGRAMAS PRESIDENCIALES")
    logger.info(f"Proveedor LLM: {LLM_PROVIDER.upper()}")
    logger.info("=" * 80)
    logger.info(f"Log guardado en: {log_file}")

    return logger


def find_documents() -> list[Path]:
    """
    Encuentra todos los archivos PDF y TXT en la carpeta pdfs/.

    Returns:
        Lista de rutas a archivos de documentos
    """
    pdf_files = list(PDFS_DIR.glob("*.pdf"))
    txt_files = list(PDFS_DIR.glob("*.txt"))

    all_files = pdf_files + txt_files

    if not all_files:
        raise FileNotFoundError(
            f"No se encontraron archivos PDF o TXT en {PDFS_DIR}\n"
            f"Por favor, coloca los programas presidenciales en la carpeta 'pdfs/'"
        )

    return sorted(all_files)


def process_single_pdf(
    pdf_path: Path,
    extractor: PDFExtractor,
    chunker: TextChunker,
    analyzer: Analyzer,
    synthesizer: Synthesizer,
    validator: AnalysisValidator,
    logger: logging.Logger
) -> dict:
    """
    Procesa un solo PDF y retorna el análisis consolidado.

    Args:
        pdf_path: Ruta al archivo PDF
        extractor: Extractor de PDF
        chunker: Chunker de texto
        analyzer: Analizador LLM
        synthesizer: Sintetizador
        logger: Logger

    Returns:
        Análisis consolidado del PDF
    """
    logger.info("")
    logger.info("-" * 80)
    logger.info(f"Procesando: {pdf_path.name}")
    logger.info("-" * 80)

    # 1. Extraer texto del PDF
    text = extractor.extract_text(pdf_path)
    if not text:
        logger.error(f"No se pudo extraer texto de {pdf_path.name}")
        return None

    # 2. Extraer primeras páginas para metadata
    first_pages = extractor.extract_first_pages(pdf_path, num_pages=3)

    # 3. Dividir en chunks
    chunks = chunker.chunk_text(text)
    logger.info(f"Documento dividido en {len(chunks)} chunks")

    # 4. Analizar cada chunk
    partial_analyses = []

    with tqdm(total=len(chunks), desc=f"Analizando {pdf_path.name}", unit="chunk") as pbar:
        for i, chunk in enumerate(chunks, 1):
            analysis = analyzer.analyze_chunk(chunk, i, len(chunks))

            if analysis:
                partial_analyses.append(analysis)

            pbar.update(1)

    logger.info(f"Análisis parciales completados: {len(partial_analyses)}/{len(chunks)}")

    # 5. Extraer metadata
    metadata = analyzer.extract_metadata(first_pages)

    # 6. Sintetizar resultados
    final_analysis = synthesizer.synthesize(
        partial_analyses=partial_analyses,
        original_text_sample=first_pages,
        metadata=metadata
    )

    # 7. Validar completitud y generar resumen
    validation_result = validator.validate_completeness(final_analysis)
    validator.log_final_summary(final_analysis, pdf_path.name)

    # Agregar información del archivo
    final_analysis["pdf_filename"] = pdf_path.name
    final_analysis["processing_date"] = datetime.now().isoformat()

    return final_analysis


def main():
    """Función principal."""
    logger = setup_logging()

    try:
        # Encontrar documentos (PDF y TXT)
        document_files = find_documents()
        logger.info(f"Encontrados {len(document_files)} archivos:")
        for doc in document_files:
            logger.info(f"  - {doc.name}")

        # Inicializar componentes
        logger.info(f"Inicializando componentes con {LLM_PROVIDER.upper()}...")
        extractor = PDFExtractor()
        chunker = TextChunker()
        analyzer = Analyzer()
        synthesizer = Synthesizer()
        validator = AnalysisValidator()

        # Procesar cada documento
        all_results = []

        for document_path in document_files:
            result = process_single_pdf(
                pdf_path=document_path,
                extractor=extractor,
                chunker=chunker,
                analyzer=analyzer,
                synthesizer=synthesizer,
                validator=validator,
                logger=logger
            )

            if result:
                all_results.append(result)

        # Guardar resultados consolidados
        output_data = {
            "fecha_analisis": datetime.now().isoformat(),
            "total_candidatos": len(all_results),
            "candidatos": all_results
        }

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

        logger.info("")
        logger.info("=" * 80)
        logger.info("ANÁLISIS COMPLETADO")
        logger.info("=" * 80)
        logger.info(f"Resultados guardados en: {OUTPUT_FILE}")
        logger.info(f"Candidatos procesados: {len(all_results)}")

        # Mostrar uso de tokens y costo estimado
        token_usage = analyzer.get_token_usage()
        estimated_cost = analyzer.estimate_cost()

        logger.info("")
        logger.info("Uso de Tokens:")
        logger.info(f"  Input:  {token_usage['input_tokens']:,}")
        logger.info(f"  Output: {token_usage['output_tokens']:,}")
        logger.info(f"  Total:  {token_usage['total_tokens']:,}")
        logger.info(f"  Costo estimado: ${estimated_cost:.4f} USD")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error en el proceso principal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
