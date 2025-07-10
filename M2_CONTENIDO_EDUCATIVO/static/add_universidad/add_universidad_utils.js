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

    // Siempre necesarios
    const campos_comunes = [
        'csrfmiddlewaretoken', 'tipo_solucionario', 'nombre', 'logo',
        'codigo_modular', 'institucion_educativa',
        'departamento', 'provincia', 'distrito'
    ];

    campos_comunes.forEach(campo => {
        const valor = formData.get(campo);
        if (valor !== null && (typeof valor === 'string' ? valor.trim() !== '' : true)) {
            cleanFormData.append(campo, valor);
        }
    });

    // Obtener el tipo de solucionario actual
    const tipo = formData.get('tipo_solucionario');

    if (tipo === 'admision') {
        const pais = formData.get('pais');
        if (pais && pais.trim() !== '') {
            cleanFormData.append('pais', pais.trim());
        }
        // Asegurar que campos no relacionados no se envíen
    } else if (tipo === 'ejercicios' || tipo === 'otro') {
        const curso = formData.get('curso');
        const carrera = formData.get('carrera');
        const nivel = formData.get('nivel');

        if (curso && curso.trim() !== '') {
            cleanFormData.append('curso', curso.trim());
        }
        if (carrera && carrera.trim() !== '') {
            cleanFormData.append('carrera', carrera.trim());
        }
        if (nivel && nivel.trim() !== '') {
            cleanFormData.append('nivel', nivel.trim());
        }
    }

    return cleanFormData;
}

// Validación básica del formulario
export function validateForm(formData) {
    const errors = {};

    const tipo = formData.get('tipo_solucionario');
    const nombre = formData.get('nombre')?.trim();

    // Validar siempre nombre
    if (!nombre) {
        errors.nombre = 'El nombre es requerido';
    }

    // Validación condicional según tipo
    if (tipo === 'admision') {
        const pais = formData.get('pais')?.trim();
        if (!pais) {
            errors.pais = 'El país es requerido para repositorios de admisión';
        }
    } else if (tipo === 'ejercicios' || tipo === 'otro') {
        const curso = formData.get('curso')?.trim();
        const carrera = formData.get('carrera')?.trim();
        const nivel = formData.get('nivel')?.trim();

        if (!curso) {
            errors.curso = 'El curso es requerido para solucionarios de ejercicios u otros';
        }
        if (!carrera) {
            errors.carrera = 'La materia es requerida';
        }
        if (!nivel) {
            errors.nivel = 'El nivel es requerido';
        }
    }

    return Object.keys(errors).length > 0 ? errors : null;
}

// Inicialización de selectpicker con opciones
export function initializeSelectPicker() {
    // Inicializar todos los selectpickers
    $('.selectpicker').selectpicker({
        noneSelectedText: 'Seleccione una opción',
        noneResultsText: 'No se encontraron resultados',
        countSelectedText: function(numSelected, numTotal) {
            return (numSelected == 1) ? "{0} ítem seleccionado" : "{0} ítems seleccionados";
        }
    });
    
    // Refrescar todos los selectpickers
    $('.selectpicker').selectpicker('refresh');
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