"""
Configuración central del sistema de análisis de programas presidenciales.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
PDFS_DIR = PROJECT_ROOT / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"

# Crear directorios si no existen
PDFS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de LLM Provider
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()  # "gemini" o "claude"

# Configuración de Anthropic API
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configuración de Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# Validar que al menos una API key esté configurada
if not ANTHROPIC_API_KEY and not GEMINI_API_KEY:
    raise ValueError(
        "Ni ANTHROPIC_API_KEY ni GEMINI_KEY encontradas. "
        "Por favor configura al menos una en tu archivo .env"
    )

# Configurar proveedor predeterminado basado en API keys disponibles
if LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
    if ANTHROPIC_API_KEY:
        LLM_PROVIDER = "claude"
        print("⚠️  GEMINI_KEY no encontrada, usando Claude")
    else:
        raise ValueError("LLM_PROVIDER configurado como 'gemini' pero GEMINI_KEY no encontrada")

if LLM_PROVIDER == "claude" and not ANTHROPIC_API_KEY:
    if GEMINI_API_KEY:
        LLM_PROVIDER = "gemini"
        print("⚠️  ANTHROPIC_API_KEY no encontrada, usando Gemini")
    else:
        raise ValueError("LLM_PROVIDER configurado como 'claude' pero ANTHROPIC_API_KEY no encontrada")

# Modelos por proveedor
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")  # Modelo más reciente y rápido

# Modelo activo según proveedor
if LLM_PROVIDER == "gemini":
    MODEL_NAME = GEMINI_MODEL
else:
    MODEL_NAME = CLAUDE_MODEL

# Configuración de chunking
MAX_TOKENS_PER_CHUNK = int(os.getenv("MAX_TOKENS_PER_CHUNK", "6000"))  # Ajustado para respetar rate limits (10K/min)
CHUNK_OVERLAP_TOKENS = int(os.getenv("CHUNK_OVERLAP_TOKENS", "600"))  # Reducido proporcionalmente

# Aproximación: 1 token ≈ 4 caracteres en español
CHARS_PER_TOKEN = 4
MAX_CHARS_PER_CHUNK = MAX_TOKENS_PER_CHUNK * CHARS_PER_TOKEN
CHUNK_OVERLAP_CHARS = CHUNK_OVERLAP_TOKENS * CHARS_PER_TOKEN

# Configuración de análisis LLM
# Ajustado para respetar rate limits (4K output/min) y evitar truncamiento JSON
if LLM_PROVIDER == "gemini":
    MAX_TOKENS_OUTPUT_CHUNK = int(os.getenv("MAX_TOKENS_OUTPUT_CHUNK", "3000"))
    MAX_TOKENS_OUTPUT_SYNTHESIS = int(os.getenv("MAX_TOKENS_OUTPUT_SYNTHESIS", "3000"))
else:
    MAX_TOKENS_OUTPUT_CHUNK = int(os.getenv("MAX_TOKENS_OUTPUT_CHUNK", "3000"))
    MAX_TOKENS_OUTPUT_SYNTHESIS = int(os.getenv("MAX_TOKENS_OUTPUT_SYNTHESIS", "3000"))

# Configuración de validación y re-análisis
ENABLE_VALIDATION = os.getenv("ENABLE_VALIDATION", "true").lower() == "true"
REANALYZE_MISSING_CATEGORIES = os.getenv("REANALYZE_MISSING_CATEGORIES", "true").lower() == "true"

# Categorías de análisis (basadas en topics.md)
CATEGORIAS = [
    "Economía y Desarrollo",
    "Seguridad Social",
    "Salud",
    "Educación",
    "Vivienda y Urbanismo",
    "Seguridad y Orden Público",
    "Justicia, Derechos y Libertades",
    "Medio Ambiente y Energía",
    "Agricultura y Desarrollo Rural",
    "Transporte e Infraestructura",
    "Políticas Sociales y Comunidad",
    "Gobernanza, Instituciones y Estado",
    "Política Exterior",
    "Innovación, Tecnología y Digitalización",
    "Cultura, Ciencia y Sociedad",
    "Perfil y Estilo Político del Candidato"
]

# Configuración de logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Archivo de salida
OUTPUT_FILE = OUTPUT_DIR / "analisis_consolidado.json"
