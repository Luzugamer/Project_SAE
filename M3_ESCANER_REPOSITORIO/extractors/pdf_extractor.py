import fitz  # pip install PyMuPDF

def extraer_texto_pdf(ruta_pdf):
    texto_total = ""
    with fitz.open(ruta_pdf) as doc:
        for pagina in doc:
            texto_total += pagina.get_text()
    return texto_total