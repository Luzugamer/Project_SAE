import { hideModal, showElement, hideElement } from './add_universidad_utils.js';

export function setupModalActions(modalPrevia, isEditMode) {
    document.getElementById('btn-editar')?.addEventListener('click', cerrarModalPrevia);
    document.getElementById('btn-guardar')?.addEventListener('click', () => confirmarGuardado(false));
    document.getElementById('btn-agregar-otra')?.addEventListener('click', () => confirmarGuardado(true));

    if (isEditMode) {
        document.getElementById('btn-agregar-otra')?.style.setProperty('display', 'none');
    }
}

export function setupPreviewUpdater() {
    const camposParaPrevia = ['nombre', 'pais', 'tipo_solucionario'];
    camposParaPrevia.forEach(campo => {
        const input = document.querySelector(`[name="${campo}"]`);
        if (input) input.addEventListener('change', actualizarPreviaRapida);
    });
}

function actualizarPreviaRapida() {
    const nombre = document.querySelector('[name="nombre"]').value;
    const pais = document.querySelector('[name="pais"] option:checked')?.textContent;
    const tipo = document.querySelector('[name="tipo_solucionario"] option:checked')?.textContent;

    if (nombre) document.getElementById('previa-nombre').textContent = nombre;
    if (pais) document.getElementById('previa-pais').textContent = pais;
    if (tipo) document.getElementById('previa-tipo').textContent = tipo;
}

export function mostrarPrevisualizacion(data) {
    const modal = document.getElementById('modal-previa');
    if (!modal) {
        console.warn('No se encontró el modal con ID "modal-previa"');
        return;
    }

    document.getElementById('previa-nombre').textContent = data.nombre || '';
    document.getElementById('previa-pais').textContent = data.pais || '';
    document.getElementById('previa-tipo').textContent = data.tipo_solucionario || '';

    const logo = document.getElementById('previa-logo');
    if (logo && data.logo_url) {
        logo.src = data.logo_url;
        showElement(logo);
    } else {
        hideElement(logo);
    }

    if (data.is_edit) {
        const btnAgregarOtra = document.getElementById('btn-agregar-otra');
        const btnGuardar = document.getElementById('btn-guardar');
        if (btnAgregarOtra) hideElement(btnAgregarOtra);
        if (btnGuardar) btnGuardar.textContent = 'Guardar cambios';
    }

    const bootstrapModal = bootstrap.Modal.getOrCreateInstance(modal);
    bootstrapModal.show();
}

export function cerrarModalPrevia() {
    const modal = document.getElementById('modal-previa');
    if (modal) hideModal(modal);
}

export function confirmarGuardado(addAnother) {
    const form = document.getElementById('form-universidad');
    if (!form) return;

    const buttons = document.querySelectorAll('.modal-actions button');
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.dataset.originalText = btn.textContent;
        btn.textContent = 'Procesando...';
    });

    const formData = new FormData(form);
    formData.append('confirm_save', 'true');
    if (addAnother) formData.append('add_another', 'true');

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
            throw new Error('El servidor devolvió una respuesta no JSON');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            cerrarModalPrevia();
            if (data.redirect) {
                window.location.href = URLS.repositorio;
            } else if (data.add_another) {
                window.location.href = URLS.add_universidad;
            }
        } else {
            throw new Error(typeof data.errors === 'string' ? data.errors : 'Error al guardar. Revisa los campos.');
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