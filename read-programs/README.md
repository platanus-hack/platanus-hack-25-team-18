# Sistema de Análisis de Programas Presidenciales

Sistema automatizado en Python para analizar programas presidenciales (archivos PDF) usando Procesamiento de Lenguaje Natural con Claude de Anthropic.

## Características

- Extracción de texto de PDFs usando PyMuPDF (fitz)
- Análisis inteligente por chunks para documentos largos
- Clasificación en 16 categorías temáticas
- Extracción automática de metadata (candidato, partido, año)
- Análisis de perspectiva ideológica
- Identificación de propuestas clave
- Citas textuales del documento
- Síntesis consolidada de resultados

## Estructura del Proyecto

```
data-presidentes/
├── pdfs/                    # Archivos PDF a analizar
├── output/                  # Resultados en JSON
├── logs/                    # Logs de ejecución
├── src/
│   ├── __init__.py
│   ├── config.py           # Configuración central
│   ├── prompts.py          # System prompts para Claude
│   ├── pdf_extractor.py    # Extracción con PyMuPDF
│   ├── text_chunker.py     # División en chunks
│   ├── llm_analyzer.py     # Análisis con Claude
│   └── synthesizer.py      # Síntesis de resultados
├── main.py                 # Script principal
├── requirements.txt
├── .env                    # Configuración (crear desde .env.example)
└── README.md
```

## Instalación

### 1. Clonar o descargar el proyecto

```bash
cd data-presidentes
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar API Key de Anthropic

1. Obtén tu API key en: https://console.anthropic.com/settings/keys
2. Copia el archivo de ejemplo:
   ```bash
   cp .env.example .env
   ```
3. Edita `.env` y agrega tu API key:
   ```
   ANTHROPIC_API_KEY=tu-api-key-aqui
   ```

## Uso

### 1. Colocar PDFs

Coloca los archivos PDF de programas presidenciales en la carpeta `pdfs/`:

```bash
# Los PDFs ya existentes se moverán automáticamente
# O copia manualmente tus PDFs:
cp "programa_candidato.pdf" pdfs/
```

### 2. Ejecutar análisis

```bash
python main.py
```

El script:
- Encontrará todos los PDFs en `pdfs/`
- Extraerá el texto de cada uno
- Los dividirá en chunks inteligentes
- Analizará cada chunk con Claude
- Sintetizará los resultados
- Guardará todo en `output/analisis_consolidado.json`

### 3. Revisar resultados

Los resultados se guardan en `output/analisis_consolidado.json` con esta estructura:

```json
{
  "fecha_analisis": "2025-11-22T...",
  "total_candidatos": 2,
  "candidatos": [
    {
      "metadata": {
        "candidato": "Nombre del Candidato",
        "partido_coalicion": "Partido Político",
        "año": "2024"
      },
      "categorias": [
        {
          "categoria": "Economía y Desarrollo",
          "analisis_perspectiva": {
            "rol_del_estado": "Subsidiario",
            "enfoque_ideologico": "Liberal",
            "tono": "Técnico"
          },
          "propuestas_clave": [
            {
              "titulo": "Reducción de impuestos",
              "descripcion": "Bajar tasa de impuesto corporativo del 27% al 20%"
            }
          ],
          "citas_textuales": [
            "Promoveremos el crecimiento económico..."
          ]
        }
      ]
    }
  ]
}
```

## Categorías de Análisis

El sistema clasifica la información en 16 categorías:

1. Economía y Desarrollo
2. Seguridad Social
3. Salud
4. Educación
5. Vivienda y Urbanismo
6. Seguridad y Orden Público
7. Justicia, Derechos y Libertades
8. Medio Ambiente y Energía
9. Agricultura y Desarrollo Rural
10. Transporte e Infraestructura
11. Políticas Sociales y Comunidad
12. Gobernanza, Instituciones y Estado
13. Política Exterior
14. Innovación, Tecnología y Digitalización
15. Cultura, Ciencia y Sociedad
16. Perfil y Estilo Político del Candidato

Ver detalles en `topics.md`.

## Configuración Avanzada

### Variables de entorno (`.env`)

```bash
# API Key (obligatoria)
ANTHROPIC_API_KEY=sk-ant-api03-xxx

# Modelo a usar (opcional)
MODEL_NAME=claude-3-5-sonnet-20241022

# Configuración de chunks (opcional)
MAX_TOKENS_PER_CHUNK=40000
CHUNK_OVERLAP_TOKENS=1000
```

### Estrategia de Chunking

El sistema divide documentos largos en chunks de aproximadamente 40,000 tokens (~160,000 caracteres) con un overlap de 1,000 tokens para mantener contexto.

Para PDFs de 100+ páginas:
- Se crean múltiples chunks
- Cada chunk se analiza independientemente
- Los resultados se sintetizan al final
- El overlap previene pérdida de información en los límites

## Costos Estimados

El sistema usa Claude 3.5 Sonnet. Costos aproximados (verificar precios actuales):

- Input: $3.00 por millón de tokens
- Output: $15.00 por millón de tokens

Para un programa presidencial de 100 páginas (~250,000 tokens):
- Costo estimado: $2-5 USD por documento

El sistema muestra el uso de tokens y costo estimado al finalizar.

## Logs

Los logs se guardan en `logs/` con timestamp:
```
logs/analisis_20251122_143052.log
```

Niveles de logging:
- INFO: Progreso general
- DEBUG: Detalles de chunks y tokens
- ERROR: Errores y excepciones

## Troubleshooting

### Error: "ANTHROPIC_API_KEY no encontrada"
- Verifica que el archivo `.env` existe
- Verifica que contiene `ANTHROPIC_API_KEY=...`

### Error: "No se encontraron archivos PDF"
- Verifica que hay PDFs en la carpeta `pdfs/`
- Verifica que tienen extensión `.pdf`

### Error de rate limit
- El sistema incluye backoff exponencial automático
- Si persiste, reduce `MAX_TOKENS_PER_CHUNK` en `.env`

### JSON inválido en respuesta
- El sistema incluye fallback a síntesis simple
- Revisa los logs para detalles
- Puede ocurrir con PDFs muy complejos o mal formateados

## Stack Tecnológico

- **Lenguaje**: Python 3.10+
- **PDF Reading**: PyMuPDF (fitz)
- **LLM**: Claude 3.5 Sonnet (Anthropic API)
- **Data Format**: JSON
- **Logging**: Python logging + colorlog

## Desarrollo

### Estructura modular

Cada componente es independiente y testeable:

- `PDFExtractor`: Maneja extracción de PDFs
- `TextChunker`: División inteligente de texto
- `LLMAnalyzer`: Comunicación con API de Claude
- `AnalysisSynthesizer`: Consolidación de resultados

### Extender el sistema

Para agregar nuevas categorías:
1. Edita `src/config.py` → `CATEGORIAS`
2. Actualiza `topics.md`
3. Los prompts se ajustan automáticamente

## Licencia

Proyecto educativo/investigación.

## Contacto

Para reportar problemas o sugerencias, crear un issue en el repositorio.
