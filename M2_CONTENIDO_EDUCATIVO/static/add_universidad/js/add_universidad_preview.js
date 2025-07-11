import { hideModal, showElement, hideElement, showError } from './add_universidad_utils.js';

// Acciones de los botones del modal
export function setupModalActions(modalPrevia, isEditMode) {
    document.getElementById('btn-editar')?.addEventListener('click', cerrarModalPrevia);
    document.getElementById('btn-guardar')?.addEventListener('click', () => confirmarGuardado(false));
    document.getElementById('btn-agregar-otra')?.addEventListener('click', () => confirmarGuardado(true));

    if (isEditMode) {
        hideElement(document.getElementById('btn-agregar-otra'));
    }
}

// Permite que la vista previa se actualice dinámicamente mientras el usuario edita
export function setupPreviewUpdater() {
    ['nombre', 'pais', 'tipo_solucionario'].forEach(campo => {
        const input = document.querySelector(`[name="${campo}"]`);
        if (input) {
            input.addEventListener('change', actualizarPreviaRapida);
        }
    });
}

// Actualiza la previsualización rápida en tiempo real
function actualizarPreviaRapida() {
    const nombre = document.querySelector('[name="nombre"]')?.value || '';
    const tipo = document.querySelector('[name="tipo_solucionario"] option:checked')?.textContent || '';
    const pais = document.querySelector('[name="pais"] option:checked')?.textContent || '';

    document.getElementById('previa-nombre').textContent = nombre;
    document.getElementById('previa-tipo').textContent = tipo;

    // Mostrar país solo si tipo es admisión
    const tipoValor = document.querySelector('[name="tipo_solucionario"]')?.value;
    document.getElementById('previa-pais').textContent = (tipoValor === 'admision') ? pais : '';
}

// Muestra el modal de previsualización con datos reales del servidor
export function mostrarPrevisualizacion(data) {
    const modal = document.getElementById('modal-previa');
    if (!modal) return;

    document.getElementById('previa-nombre').textContent = data.nombre || '';
    document.getElementById('previa-pais').textContent = data.tipo_solucionario === 'admision' ? (data.pais || '') : '';
    document.getElementById('previa-tipo').textContent = data.tipo_solucionario || '';

    const logo = document.getElementById('previa-logo');
    if (logo && data.logo_url) {
        logo.src = data.logo_url;
        showElement(logo);
    } else {
        hideElement(logo);
    }

    if (data.is_edit) {
        hideElement(document.getElementById('btn-agregar-otra'));
        const btnGuardar = document.getElementById('btn-guardar');
        if (btnGuardar) btnGuardar.textContent = 'Guardar cambios';
    }

    const bootstrapModal = bootstrap.Modal.getOrCreateInstance(modal);
    bootstrapModal.hide(); 
    bootstrapModal.show();
}

// Cierra el modal
export function cerrarModalPrevia() {
    const modal = document.getElementById('modal-previa');
    const modalInstance = bootstrap.Modal.getInstance(modal);
    if (modalInstance) modalInstance.hide();
}

// Confirma el guardado real del formulario tras la previsualización
export function confirmarGuardado(addAnother) {
    const form = document.getElementById('form-universidad');
    if (!form) return;

    const buttons = document.querySelectorAll('.modal-footer button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'Procesando...';
    });

    const formData = new FormData(form);
    formData.append('confirm_save', 'true');
    if (addAnother) formData.append('add_another', 'true');

    cerrarModalPrevia();
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(async response => {
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            throw new Error('El servidor devolvió una respuesta no JSON:\n' + text);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            cerrarModalPrevia();
            if (data.redirect) {
                window.location.href = window.APP_CONFIG.URLs.repositorio;
            } else if (data.add_another) {
                window.location.href = window.APP_CONFIG.URLs.add_admision; // o general, según tipo
            }
        } else {
            if (data.errors) {
                const errorMsg = typeof data.errors === 'string'
                    ? data.errors
                    : Object.values(data.errors).flat().join(' ');
                throw new Error(errorMsg);
            }
        }
    })
    .catch(err => {
        console.error('Error completo:', err);
        showError('Error: ' + (err.message || 'Error al procesar la solicitud'));
    })
    .finally(() => {
        buttons.forEach(btn => {
            btn.textContent = btn.dataset.originalText;
            btn.disabled = false;
        });
    });
}
