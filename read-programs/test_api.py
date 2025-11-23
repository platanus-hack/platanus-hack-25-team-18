#!/usr/bin/env python3
"""
Script de prueba para verificar modelos disponibles.
"""
from dotenv import load_dotenv
import os
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key configurada: {api_key[:20]}..." if api_key else "NO CONFIGURADA")

# Modelos comunes a probar
models_to_test = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307",
    "claude-3-opus-20240229",
]

client = Anthropic(api_key=api_key)

print("\nProbando modelos disponibles...\n")

for model in models_to_test:
    try:
        response = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✓ {model} - DISPONIBLE")
        print(f"  Respuesta: {response.content[0].text}")
        break  # Si funciona uno, usamos ese
    except Exception as e:
        error_msg = str(e)
        if "not_found_error" in error_msg:
            print(f"✗ {model} - NO DISPONIBLE (404)")
        elif "credit" in error_msg.lower() or "balance" in error_msg.lower():
            print(f"⚠ {model} - EXISTE pero sin créditos")
        else:
            print(f"✗ {model} - ERROR: {error_msg[:100]}")

print("\nVerificación completa.")
