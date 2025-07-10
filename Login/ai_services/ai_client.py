import os
import openai
import re
import json
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

def corregir_institucion_y_ubicacion(nombre, departamento, provincia, distrito):
    prompt = f"""
Corrige la siguiente información institucional para almacenarla correctamente. Usa el contexto geográfico (departamento, provincia, distrito) para deducir la institución educativa más probable en esa ubicación.

Corrige errores ortográficos o de formato. No inventes nombres. Si la institución coincide con una existente en esa zona, usa el nombre correcto.

Datos a corregir:
- Nombre institución: {nombre}
- Departamento: {departamento}
- Provincia: {provincia}
- Distrito: {distrito}

Devuelve SOLO un JSON válido con las claves:
nombre_institucion, departamento, provincia, distrito.
""".strip()
    
    try:
        respuesta = client.chat.completions.create(
            model="llama-3.3-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        texto = respuesta.choices[0].message.content.strip()
        print("DEBUG IA Response:", texto)

        # ✅ Extraer contenido JSON entre llaves usando regex
        json_match = re.search(r"\{.*\}", texto, re.DOTALL)
        if not json_match:
            raise ValueError("No se encontró JSON válido en la respuesta de la IA.")

        texto_json = json_match.group(0)
        datos = json.loads(texto_json)
        return datos

    except Exception as e:
        print(f"[ERROR IA]: {e}")
        # Retornar lo que se ingresó si ocurre un fallo
        return {
            "nombre_institucion": nombre,
            "departamento": departamento,
            "provincia": provincia,
            "distrito": distrito,
        }
