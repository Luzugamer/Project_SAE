import re
from typing import Dict, Any
from sympy import symbols, integrate, sympify
from sympy.integrals.manualintegrate import integral_steps
from sympy.printing.latex import latex

class MathSolver:
    """
    Servicio para análisis y clasificación de problemas matemáticos
    """
    
    PATRONES_CATEGORIA = {
        'algebra': [
            r'ecuación', r'incógnita', r'variable', r'x\s*=', r'despejar',
            r'sistema.*ecuaciones', r'polinomio', r'factorizar'
        ],
        'calculo': [
            r'derivada', r'integral', r'límite', r'continuidad',
            r'dx', r'dy', r'∫', r'∂', r'lim'
        ],
        'geometria': [
            r'área', r'perímetro', r'volumen', r'triángulo', r'círculo',
            r'rectángulo', r'teorema.*pitágoras', r'coordenadas'
        ],
        'trigonometria': [
            r'seno', r'coseno', r'tangente', r'sin', r'cos', r'tan',
            r'ángulo', r'radianes', r'grados'
        ],
        'estadistica': [
            r'media', r'mediana', r'moda', r'desviación', r'probabilidad',
            r'correlación', r'regresión', r'muestra'
        ]
    }
    def __init__(self):
        self.x = symbols('x')  # puedes adaptar más variables

    def resolver_integral(self, expresion: str) -> dict:
        try:
            expr = sympify(expresion)
            pasos = integral_steps(expr, self.x)
            resultado = integrate(expr, self.x)

            return {
                'pasos': str(pasos),
                'resultado': str(resultado),
                'latex': latex(resultado)
            }

        except Exception as e:
            return {
                'error': f"Error al resolver la integral: {str(e)}"
            }

    def analizar_problema(self, texto: str) -> Dict[str, Any]:
        """
        Analiza un problema matemático para clasificarlo
        """
        texto_lower = texto.lower()
        
        return {
            'categoria': self._detectar_categoria(texto_lower),
            'nivel': self._detectar_nivel(texto_lower),
            'dificultad': self._estimar_dificultad(texto_lower),
            'requiere_grafico': self._requiere_grafico(texto_lower)
        }
    
    def _detectar_categoria(self, texto: str) -> str:
        """
        Detecta la categoría del problema matemático
        """
        scores = {}
        
        for categoria, patrones in self.PATRONES_CATEGORIA.items():
            score = 0
            for patron in patrones:
                if re.search(patron, texto):
                    score += 1
            scores[categoria] = score
        
        if not scores or max(scores.values()) == 0:
            return 'otro'
        
        return max(scores, key=scores.get)
    
    def _detectar_nivel(self, texto: str) -> str:
        """
        Detecta el nivel académico del problema
        """
        patrones_universitario = [
            r'integral', r'derivada', r'límite', r'serie', r'transformada',
            r'matriz', r'determinante', r'ecuación diferencial'
        ]
        
        for patron in patrones_universitario:
            if re.search(patron, texto):
                return 'universitario'
        
        return 'secundaria'
    
    def _estimar_dificultad(self, texto: str) -> int:
        """
        Estima la dificultad del problema (1-5)
        """
        factores_dificultad = [
            r'sistema.*ecuaciones',
            r'ecuación.*grado\s*[3-9]',
            r'integral.*doble|triple',
            r'derivada.*parcial',
            r'límite.*infinito',
            r'serie.*convergencia'
        ]
        
        dificultad = 1
        for patron in factores_dificultad:
            if re.search(patron, texto):
                dificultad += 1
        
        return min(dificultad, 5)
    
    def _requiere_grafico(self, texto: str) -> bool:
        """
        Determina si el problema requiere gráfico
        """
        patrones_grafico = [
            r'gráfica', r'graficar', r'coordenadas', r'plano',
            r'función.*x', r'parábola', r'recta'
        ]
        
        return any(re.search(patron, texto) for patron in patrones_grafico)