import { initializeSelectPicker } from './add_universidad_utils.js';
import { setupFormSubmission } from './add_universidad_form_handlers.js';
import { setupModalActions, setupPreviewUpdater } from './add_universidad_preview.js';
import { setupUI } from './add_universidad_ui.js';
import { mostrarCamposCondicionales } from './add_universidad_conditional.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-universidad');
    const isEditMode = form?.dataset.edit === 'true';
    const submitBtn = form?.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn?.textContent;
    const modalPrevia = document.getElementById('modal-previa');
    const tipoSelect = document.querySelector('#id_tipo_solucionario');
    
    // PRIMER PASO: Inicializar todos los selectpickers ANTES de manipular campos
    initializeSelectPicker();
    
    // SEGUNDO PASO: Configurar la UI básica
    setupUI();
    
    // TERCER PASO: Configurar los campos condicionales después de que todo esté inicializado
    if (tipoSelect) {
        // Esperamos un momento para que los selectpickers estén completamente inicializados
        setTimeout(() => {
            // Configuración inicial basada en el valor actual
            mostrarCamposCondicionales(tipoSelect.value);
            
            // Configurar el listener para cambios futuros
            tipoSelect.addEventListener('change', (e) => {
                mostrarCamposCondicionales(e.target.value);
            });
        }, 200); // Tiempo suficiente para que Bootstrap Select se inicialice
    }
    
    // CUARTO PASO: Configuración del formulario
    if (form) {
        setupFormSubmission(form, submitBtn, originalBtnText, isEditMode);
    }
    
    // QUINTO PASO: Configuración del modal
    if (modalPrevia) {
        setupModalActions(modalPrevia, isEditMode);
    }
    
    // SEXTO PASO: Configuración de actualización de vista previa
    setupPreviewUpdater();
    
    // VERIFICACIÓN ADICIONAL: Asegurarnos de que los selectpickers estén funcionando
    setTimeout(() => {
        verificarSelectpickers();
    }, 500);
});

// Función auxiliar para verificar que los selectpickers estén funcionando correctamente
function verificarSelectpickers() {
    const selectpickers = document.querySelectorAll('.selectpicker');
    
    selectpickers.forEach(select => {
        const $select = $(select);
        
        // Verificar si el selectpicker está inicializado
        if (!$select.data('selectpicker')) {
            console.warn('Selectpicker no inicializado:', select.name || select.id);
            // Intentar inicializarlo
            $select.selectpicker();
        }
        
        // Verificar si tiene opciones
        const opciones = $select.find('option');
        if (opciones.length <= 1) {
            console.warn('Selectpicker sin opciones:', select.name || select.id);
        }
        
        // Refrescar para asegurar que esté actualizado
        $select.selectpicker('refresh');
    });
}

// Función para reinicializar selectpickers si es necesario
window.reinicializarSelectpickers = function() {
    $('.selectpicker').selectpicker('destroy').selectpicker();
    verificarSelectpickers();
};