document.getElementById('icono').addEventListener('change', function(e) {
    const file = e.target.files[0];
    const label = document.querySelector('.file-input-label');
    
    if (file) {
        // Actualizar texto del botón
        label.innerHTML = `<span class="file-icon">✅</span>${file.name}`;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            // Remover vista previa anterior si existe
            const existingPreview = document.querySelector('.image-preview');
            if (existingPreview) {
                existingPreview.remove();
            }
            
            // Crear nueva vista previa
            const preview = document.createElement('div');
            preview.className = 'image-preview';
            preview.innerHTML = `
                <p>Vista previa del nuevo icono:</p>
                <div class="preview-container">
                    <img src="${e.target.result}" alt="Vista previa">
                </div>
            `;
            
            // Insertar después del wrapper del input
            document.querySelector('.file-input-wrapper').parentNode.appendChild(preview);
        };
        reader.readAsDataURL(file);
    } else {
        label.innerHTML = '<span class="file-icon">📁</span>Seleccionar archivo';
    }
});

// Validación básica del formulario
document.querySelector('form').addEventListener('submit', function(e) {
    const nombre = document.getElementById('nombre').value.trim();
    const descripcion = document.getElementById('descripcion').value.trim();
    
    if (!nombre) {
        showAlert('El nombre de la comunidad es obligatorio.', 'error');
        e.preventDefault();
        return;
    }
    
    if (!descripcion) {
        showAlert('La descripción de la comunidad es obligatoria.', 'error');
        e.preventDefault();
        return;
    }
    
    if (nombre.length > 100) {
        showAlert('El nombre no puede exceder los 100 caracteres.', 'error');
        e.preventDefault();
        return;
    }
    
    if (descripcion.length > 5000) {
        showAlert('La descripción es demasiado larga.', 'error');
        e.preventDefault();
        return;
    }
    
    // Mostrar feedback de envío
    const submitBtn = document.querySelector('.btn-primary');
    submitBtn.innerHTML = '<span class="btn-icon loading">⏳</span>Guardando...';
    submitBtn.disabled = true;
});

function showAlert(message, type) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} temp-alert`;
    alert.innerHTML = `
        <span class="alert-icon">${type === 'error' ? '⚠️' : '✅'}</span>
        ${message}
    `;
    
    document.querySelector('.container').insertBefore(alert, document.querySelector('.modern-form'));
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Efectos de animación para inputs
document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentNode.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentNode.classList.remove('focused');
    });
});
