import { initializeSelectPicker } from './add_universidad_utils.js';
import { setupFormSubmission } from './add_universidad_form_handlers.js';
import { setupModalActions, setupPreviewUpdater } from './add_universidad_preview.js';
import { setupUI } from './add_universidad_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-universidad');
    const isEditMode = form?.dataset.edit === 'true';
    const submitBtn = form?.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn?.textContent;
    const modalPrevia = document.getElementById('modal-previa');

    // Inicialización del selectpicker
    initializeSelectPicker();

    // Configuración del formulario
    if (form) {
        setupFormSubmission(form, submitBtn, originalBtnText, isEditMode);
    }

    // Configuración del modal
    if (modalPrevia) {
        setupModalActions(modalPrevia, isEditMode);
    }

    // Configuración de actualización de vista previa
    setupPreviewUpdater();

    setupUI();
});