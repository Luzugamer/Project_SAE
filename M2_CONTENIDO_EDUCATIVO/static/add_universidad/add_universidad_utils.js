// Función para mostrar errores
export function showError(message) {
    // Primero intenta mostrar el error en un contenedor bonito
    const formContainer = document.querySelector('.form-container');
    if (formContainer) {
        // Eliminar errores previos
        const existingError = formContainer.querySelector('.form-error-box');
        if (existingError) existingError.remove();

        // Crear nuevo elemento de error
        const errorBox = document.createElement('div');
        errorBox.className = 'form-error-box alert alert-danger mt-3';
        errorBox.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-exclamation-circle me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Insertar después del título o al inicio del formulario
        const formTitle = formContainer.querySelector('h1');
        if (formTitle) {
            formTitle.insertAdjacentElement('afterend', errorBox);
        } else {
            formContainer.prepend(errorBox);
        }

        // Hacer scroll al error
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Auto-eliminarse después de 5 segundos
        setTimeout(() => {
            errorBox.classList.add('fade-out');
            setTimeout(() => errorBox.remove(), 300);
        }, 5000);
        
        return;
    }
    
    // Fallback a alert si no se encuentra el contenedor
    alert(message);
}

// Función básica para preparar datos del formulario
export function prepareFormData(form) {
    const formData = new FormData(form);
    const cleanFormData = new FormData();
    
    // Campos básicos del formulario
    const campos = [
        'csrfmiddlewaretoken', 'tipo_solucionario', 'nombre', 'logo',
        'codigo_modular', 'institucion_educativa', 'departamento', 
        'provincia', 'distrito', 'pais', 'curso'
    ];
    
    campos.forEach(campo => {
        const valor = formData.get(campo);
        if (valor !== null && (typeof valor === 'string' ? valor.trim() !== '' : true)) {
            cleanFormData.append(campo, valor);
        }
    });
    
    return cleanFormData;
}

// Validación básica del formulario
export function validateForm(formData) {
    const errors = {};
    const nombre = formData.get('nombre')?.trim();
    
    // Validación de nombre
    if (!nombre) {
        errors.nombre = 'El nombre es requerido';
    }
    
    return Object.keys(errors).length > 0 ? errors : null;
}

// Inicialización de selectpicker con opciones
export function initializeSelectPicker() {
    $('.select-pais').selectpicker({
        liveSearch: true,
        size: 5,
        style: 'btn-light',
        showSubtext: true,
        noneSelectedText: 'Seleccione un país...',
        dropupAuto: false
    });
}

// Manejo de modales
export function showModal(modal) {
    $(modal).modal('show');
}

export function hideModal(modal) {
    $(modal).modal('hide');
}

// Utilidades para mostrar/ocultar elementos
export function showElement(element) {
    if (element) {
        element.style.display = 'block';
        element.removeAttribute('aria-hidden');
    }
}

export function hideElement(element) {
    if (element) {
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
    }
}

// Función adicional útil para toggles
export function toggleElement(element, show) {
    if (show) {
        showElement(element);
    } else {
        hideElement(element);
    }
}