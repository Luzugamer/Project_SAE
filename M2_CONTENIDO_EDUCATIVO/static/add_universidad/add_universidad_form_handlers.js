import { showError, prepareFormData, validateForm } from './add_universidad_utils.js';
import { mostrarPrevisualizacion } from './add_universidad_preview.js';

export function setupFormSubmission(form, submitBtn, originalBtnText, isEditMode) {
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formDataOriginal = new FormData(form);
        const tipo = formDataOriginal.get('tipo_solucionario');
        const errors = {};

        // Validaciones condicionales
        if (tipo === 'admision') {
            if (!formDataOriginal.get('pais')) {
                errors['pais'] = 'El campo país es obligatorio.';
            }
            if (!formDataOriginal.get('carrera')) {
                errors['carrera'] = 'El campo carrera es obligatorio.';
            }
        } else if (tipo === 'ejercicios') {
            if (!formDataOriginal.get('curso')) {
                errors['curso'] = 'El campo curso es obligatorio.';
            }
            if (!formDataOriginal.get('nivel')) {
                errors['nivel'] = 'El campo nivel es obligatorio.';
            }
        }

        // Mostrar errores si los hay
        if (Object.keys(errors).length > 0) {
            const errorMessages = Object.values(errors).join('\n');
            showError('Por favor corrige los siguientes errores:\n' + errorMessages);
            return;
        }

        const cleanFormData = prepareFormData(form);  // Limpia campos ocultos/vacíos innecesarios

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = isEditMode ? 'Actualizando...' : 'Guardando...';
        }

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.APP_CONFIG.CSRF_TOKEN,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: cleanFormData
        })
        .then(async response => {
            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Error ${response.status}: ${text}`);
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('El servidor devolvió una respuesta no JSON');
            }

            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (data.preview) {
                    mostrarPrevisualizacion(data);
                } else if (data.redirect) {
                    window.location.href = window.APP_CONFIG.URLs.repositorio;
                }
            } else {
                const errorTexto = typeof data.errors === 'string'
                    ? data.errors
                    : JSON.stringify(data.errors, null, 2);
                throw new Error(errorTexto || 'Error al guardar');
            }
        })
        .catch(err => {
            showError('Error: ' + (err.message || 'Error desconocido'));
            console.error('Error:', err);
        })
        .finally(() => {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalBtnText;
            }
        });
    });
}

