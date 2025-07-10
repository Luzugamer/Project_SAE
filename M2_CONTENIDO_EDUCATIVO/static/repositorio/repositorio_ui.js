// repositorio_ui.js

function expandCard(tarjeta) {
    const examenesContainer = tarjeta.querySelector('.examenes-container');
    if (!examenesContainer) return;

    tarjeta.classList.add('expanded');
    requestAnimationFrame(() => {
        const scrollHeight = examenesContainer.scrollHeight;
        examenesContainer.style.maxHeight = scrollHeight + 'px';
        examenesContainer.style.overflow = 'visible';
    });
}

function collapseCard(tarjeta) {
    const examenesContainer = tarjeta.querySelector('.examenes-container');
    if (!examenesContainer) return;

    const scrollHeight = examenesContainer.scrollHeight;
    examenesContainer.style.maxHeight = scrollHeight + 'px';
    examenesContainer.style.overflow = 'hidden';

    requestAnimationFrame(() => {
        tarjeta.classList.remove('expanded');
        examenesContainer.style.maxHeight = '0px';
    });
}

function removeUniversityCard(universidadId) {
    const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
    if (!tarjeta) return;

    tarjeta.style.pointerEvents = 'none';
    tarjeta.style.transition = 'all 0.3s ease';

    requestAnimationFrame(() => {
        tarjeta.style.opacity = '0';
        tarjeta.style.transform = 'translateX(100px)';
    });

    setTimeout(() => tarjeta.remove(), 300);
}

function showForm(form) {
    form.style.display = 'block';
    form.style.opacity = '0';
    setTimeout(() => {
        form.style.opacity = '1';
    }, 50);
}

function hideForm(form) {
    form.style.opacity = '0';
    setTimeout(() => {
        form.style.display = 'none';
    }, 200);
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showModal(modal) {
    modal.style.display = 'flex';
}

function hideModal(modal) {
    modal.style.display = 'none';
}

function addDynamicStyles() {
    const additionalStyles = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }
        .notification.show {
            transform: translateX(0);
        }
        .notification-success { background: #4CAF50; }
        .notification-error { background: #f44336; }
        .search-container.focused input {
            box-shadow: 0 8px 25px rgba(126, 212, 173, 0.3);
        }
        .btn-cancel {
            background: #f44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        .formulario-examen {
            transition: all 0.3s ease;
        }
        .tarjeta .examenes-container {
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            max-height: 0;
            overflow: hidden;
        }
        .tarjeta.expanded .examenes-container {
            overflow: visible;
        }
    `;

    if (!document.getElementById('repositorio-dynamic-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'repositorio-dynamic-styles';
        styleSheet.textContent = additionalStyles;
        document.head.appendChild(styleSheet);
    }
}

// Inicialización de estilos
document.addEventListener('DOMContentLoaded', function() {
    addDynamicStyles();
    
    // Configuración de eventos de foco en el buscador
    const searchInput = document.querySelector('input[type="text"]');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    }
    
    // Configuración de animación para editar examen
    document.querySelectorAll('.btn-editar-repositorio').forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.add('loading');
            setTimeout(() => {
                this.classList.remove('loading');
            }, 2000);
        });
    });
    
    // Cerrar vista previa al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.examen-item') && !e.target.closest('.pdf-preview-container')) {
            document.querySelectorAll('.pdf-preview-container').forEach(container => {
                container.classList.remove('active');
            });
        }
    });
});