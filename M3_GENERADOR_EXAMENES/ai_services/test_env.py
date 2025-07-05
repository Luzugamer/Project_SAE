from dotenv import load_dotenv
import os

load_dotenv()
print("Clave Cerebras:", os.getenv("CEREBRAS_API_KEY"))