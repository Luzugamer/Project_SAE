import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Inicializar cliente Cerebras (compatible con OpenAI SDK)
client = openai.OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.getenv("CEREBRAS_API_KEY")
)

def generar_respuesta(prompt_usuario, modelo="llama-3.3-70b", temperatura=0.7):
    """
    Envía un prompt al modelo LLaMA 3.3 70B y devuelve la respuesta generada.

    :param prompt_usuario: Instrucción o contenido del usuario.
    :param modelo: Modelo de Cerebras (por defecto: llama-3.3-70b).
    :param temperatura: Controla la creatividad (0.0 = muy precisa, 1.0 = más creativa).
    :return: Texto de respuesta generado por la IA.
    """
    try:
        respuesta = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=temperatura,
        )
        return respuesta.choices[0].message.content.strip()

    except Exception as e:
        print(f"[ERROR IA]: {e}")
        return "Lo siento, ocurrió un error al generar la respuesta."

if __name__ == "__main__":
    prompt = "Explica el teorema de Bayes en lenguaje sencillo"
    resultado = generar_respuesta(prompt)
    print("[Respuesta]:", resultado)