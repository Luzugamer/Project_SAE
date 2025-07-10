class ChatManager {
    constructor(comunidadId, usuarioId) {
        this.comunidadId = comunidadId;
        this.usuarioId = usuarioId;
        this.lastMessageId = this.getLastMessageId();
        this.isConnected = true;
        this.typingTimer = null;
        this.typingUsers = new Set();
        
        this.initializeEventListeners();
        this.startPolling();
        this.loadMembers();
        this.updateConnectionStatus();
        
        // Auto-scroll al final
        this.scrollToBottom();
    }
    
    initializeEventListeners() {
        const messageForm = document.getElementById('messageForm');
        const messageInput = document.getElementById('messageInput');
        
        // Envío de mensajes
        messageForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });
        
        // Auto-resize del textarea
        messageInput.addEventListener('input', () => {
            this.autoResizeTextarea(messageInput);
        });
        
        // Enter para enviar (Shift+Enter para nueva línea)
        messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Indicador de escritura
        messageInput.addEventListener('input', () => {
            this.handleTyping();
        });
        
        // Actualizar estado de conexión periódicamente
        setInterval(() => {
            this.updateConnectionStatus();
        }, 30000);
        
        // Limpiar al salir de la página
        window.addEventListener('beforeunload', () => {
            this.disconnect();
        });
    }
    
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const contenido = messageInput.value.trim();
        
        if (!contenido) return;
        
        // Deshabilitar el formulario
        sendButton.disabled = true;
        messageInput.disabled = true;
        
        try {
            const formData = new FormData();
            formData.append('contenido', contenido);
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            const response = await fetch(`/comunidad/${this.comunidadId}/enviar-mensaje/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                messageInput.value = '';
                this.autoResizeTextarea(messageInput);
                this.addMessage(data.mensaje);
                this.scrollToBottom();
            } else {
                this.showNotification('Error al enviar mensaje', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error de conexión', 'error');
        } finally {
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
    }
    
    async loadNewMessages() {
        try {
            const response = await fetch(`/comunidad/${this.comunidadId}/obtener-mensajes/?ultimo_id=${this.lastMessageId}`);
            const data = await response.json();
            
            if (data.hay_nuevos) {
                data.mensajes.forEach(mensaje => {
                    this.addMessage(mensaje);
                    this.lastMessageId = Math.max(this.lastMessageId, mensaje.id);
                });
                this.scrollToBottom();
            }
            
            this.isConnected = true;
            this.updateConnectionIndicator();
        } catch (error) {
            console.error('Error loading messages:', error);
            this.isConnected = false;
            this.updateConnectionIndicator();
        }
    }
    
    async loadMembers() {
        try {
            const response = await fetch(`/comunidad/${this.comunidadId}/miembros-en-linea/`);
            const data = await response.json();
            
            this.updateMembersList(data.miembros);
        } catch (error) {
            console.error('Error loading members:', error);
        }
    }
    
    updateMembersList(miembros) {
        const membersList = document.getElementById('membersList');
        const membersCount = document.getElementById('membersCount');
        
        membersList.innerHTML = '';
        membersCount.textContent = miembros.length;
        
        miembros.forEach(miembro => {
            const memberElement = document.createElement('div');
            memberElement.className = `member-item ${miembro.es_yo ? 'own' : ''} online`;
            memberElement.innerHTML = `
                <div class="member-avatar">
                    ${miembro.avatar ? `<img src="${miembro.avatar}" alt="${miembro.nombre}">` : miembro.nombre.charAt(0).toUpperCase()}
                </div>
                <div class="member-info">
                    <div class="member-name">${miembro.nombre}${miembro.es_yo ? ' (Tú)' : ''}</div>
                    <div class="member-role">${miembro.rol}</div>
                </div>
            `;
            
            if (!miembro.es_yo) {
                memberElement.addEventListener('click', () => {
                    this.openPrivateChat(miembro.id, miembro.nombre);
                });
            }
            
            membersList.appendChild(memberElement);
        });
    }
    
    addMessage(mensaje) {
        const messagesContainer = document.getElementById('messagesContainer');
        const emptyMessages = document.getElementById('emptyMessages');
        
        if (emptyMessages) {
            emptyMessages.remove();
        }
        
        const messageElement = document.createElement('div');
        messageElement.className = `message ${mensaje.es_autor ? 'own' : (mensaje.tipo === 'sistema' ? 'system' : 'other')}`;
        messageElement.setAttribute('data-message-id', mensaje.id);
        
        if (mensaje.tipo !== 'sistema') {
            messageElement.innerHTML = `
                <div class="message-header">
                    <span class="message-author">${mensaje.autor}</span>
                    <span class="message-time">${mensaje.timestamp}</span>
                </div>
                <div class="message-content">${mensaje.contenido.replace(/\n/g, '<br>')}</div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="message-content">${mensaje.contenido}</div>
            `;
        }
        
        messagesContainer.appendChild(messageElement);
    }
    
    async updateConnectionStatus() {
        try {
            const formData = new FormData();
            formData.append('csrfmiddlewaretoken', this.getCSRFToken());
            
            await fetch(`/comunidad/${this.comunidadId}/actualizar-conexion/`, {
                method: 'POST',
                body: formData
            });
        } catch (error) {
            console.error('Error updating connection:', error);
        }
    }
    
    updateConnectionIndicator() {
        const connectionStatus = document.getElementById('connectionStatus');
        if (this.isConnected) {
            connectionStatus.textContent = '🟢 Conectado al chat';
            connectionStatus.className = 'connection-status';
        } else {
            connectionStatus.textContent = '🔴 Desconectado - Reintentando...';
            connectionStatus.className = 'connection-status disconnected';
        }
    }
    
    startPolling() {
        // Cargar mensajes cada 2 segundos
        setInterval(() => {
            this.loadNewMessages();
        }, 2000);
        
        // Actualizar miembros cada 10 segundos
        setInterval(() => {
            this.loadMembers();
        }, 10000);
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    getLastMessageId() {
        const messages = document.querySelectorAll('[data-message-id]');
        let maxId = 0;
        messages.forEach(msg => {
            const id = parseInt(msg.getAttribute('data-message-id'));
            if (id > maxId) maxId = id;
        });
        return maxId;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification ${type} show`;
        
        setTimeout(() => {
            notification.className = notification.className.replace('show', '');
        }, 3000);
    }
    
    handleTyping() {
        // Implementar indicador de escritura si es necesario
        clearTimeout(this.typingTimer);
        this.typingTimer = setTimeout(() => {
            // Lógica para detener indicador de escritura
        }, 1000);
    }
    
    openPrivateChat(userId, userName) {
        // Implementar chat privado si es necesario
        this.showNotification(`Chat privado con ${userName} - Funcionalidad en desarrollo`);
    }
    
    disconnect() {
        // Limpiar recursos al desconectar
        this.isConnected = false;
    }
}

// Auto-scroll a los mensajes más recientes
const messagesContainer = document.querySelector('.messages-container');
if (messagesContainer) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Auto-resize del textarea
const textarea = document.querySelector('.message-input');
if (textarea) {
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

// Auto-hide messages después de 5 segundos
setTimeout(() => {
    const messages = document.querySelectorAll('[style*="position: fixed"]');
    messages.forEach(msg => {
        msg.style.transition = 'all 0.5s ease';
        msg.style.transform = 'translateX(100%)';
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 500);
    });
}, 5000);
