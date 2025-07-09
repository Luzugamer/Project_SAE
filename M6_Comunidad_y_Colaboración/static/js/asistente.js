class AsistenteIA {
    constructor() {
        this.form = document.getElementById('pregunta-form');
        this.mensajesContainer = document.getElementById('mensajes-container');
        this.loading = document.getElementById('loading');
        this.enviarBtn = document.getElementById('enviar-btn');
        this.preguntaInput = document.getElementById('pregunta');
        
        this.inicializarEventos();
    }
    
    inicializarEventos() {
        this.form.addEventListener('submit', (e) => this.enviarPregunta(e));
        
        // Auto-resize textarea
        this.preguntaInput.addEventListener('input', () => {
            this.preguntaInput.style.height = 'auto';
            this.preguntaInput.style.height = this.preguntaInput.scrollHeight + 'px';
        });
    }
    
    async enviarPregunta(e) {
        e.preventDefault();
        
        const pregunta = this.preguntaInput.value.trim();
        const nivel = document.getElementById('nivel').value;
        
        if (!pregunta) {
            alert('Por favor escribe una pregunta.');
            return;
        }
        
        // Mostrar mensaje del usuario
        this.mostrarMensaje(pregunta, 'usuario');
        
        // Limpiar formulario
        this.preguntaInput.value = '';
        this.preguntaInput.style.height = 'auto';
        
        // Mostrar loading
        this.mostrarLoading(true);
        this.enviarBtn.disabled = true;
        
        try {
            const response = await fetch('/api/procesar-pregunta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    pregunta: pregunta,
                    nivel: nivel,
                    session_id: conversacionId
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.mostrarMensaje(data.respuesta, 'ia');
                this.mostrarInfoAdicional(data);
            } else {
                this.mostrarError(data.error || 'Error al procesar la pregunta');
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.mostrarError('Error de conexión. Intenta nuevamente.');
        } finally {
            this.mostrarLoading(false);
            this.enviarBtn.disabled = false;
        }
    }
    
    mostrarMensaje(contenido, tipo) {
        const mensajeDiv = document.createElement('div');
        mensajeDiv.className = `mensaje ${tipo}`;
        
        const ahora = new Date();
        const tiempo = ahora.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        mensajeDiv.innerHTML = `
            <div class="mensaje-contenido">
                <div class="mensaje-texto">${this.formatearTexto(contenido)}</div>
                <div class="mensaje-tiempo">${tiempo}</div>
            </div>
        `;
        
        this.mensajesContainer.appendChild(mensajeDiv);
        this.scrollToBottom();
        
        // Renderizar matemáticas si es necesario
        if (tipo === 'ia' && window.MathJax) {
            MathJax.typesetPromise([mensajeDiv]).catch((err) => {
                console.log('Error renderizando matemáticas:', err);
            });
        }
    }
    
    formatearTexto(texto) {
        // Convertir saltos de línea a <br>
        texto = texto.replace(/\n/g, '<br>');
        
        // Resaltar fórmulas matemáticas (básico)
        texto = texto.replace(/\$\$([^$]+)\$\$/g, '<div class="formula">$$$$</div>');
        texto = texto.replace(/\$([^$]+)\$/g, '<span class="formula-inline">$$</span>');
        
        return texto;
    }
    
    mostrarInfoAdicional(data) {
        if (data.categoria || data.nivel || data.dificultad) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'info-adicional';
            infoDiv.innerHTML = `
                <small>
                    Categoría: ${data.categoria || 'N/A'} | 
                    Nivel: ${data.nivel || 'N/A'} | 
                    Dificultad: ${data.dificultad || 'N/A'}/5
                    ${data.tokens_utilizados ? `| Tokens: ${data.tokens_utilizados}` : ''}
                </small>
            `;
            this.mensajesContainer.appendChild(infoDiv);
        }
    }
    
    mostrarError(mensaje) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'mensaje error';
        errorDiv.innerHTML = `
            <div class="mensaje-contenido">
                <div class="mensaje-texto">Error: ${mensaje}</div>
            </div>
        `;
        this.mensajesContainer.appendChild(errorDiv);
        this.scrollToBottom();
    }
    
    mostrarLoading(mostrar) {
        this.loading.style.display = mostrar ? 'block' : 'none';
        if (mostrar) {
            this.scrollToBottom();
        }
    }
    
    scrollToBottom() {
        this.mensajesContainer.scrollTop = this.mensajesContainer.scrollHeight;
    }
}

// Funciones globales
function limpiarConversacion() {
    if (confirm('¿Estás seguro de que quieres iniciar una nueva conversación?')) {
        fetch('/api/limpiar-conversacion/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(() => {
            location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al limpiar la conversación');
        });
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new AsistenteIA();
});