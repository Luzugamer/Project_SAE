export function setupUI() {
    const fileInput = document.querySelector('input[type="file"][name="logo"]');
    const previewContainer = document.querySelector('.logo-preview');
    const formFields = document.querySelectorAll('.form-field');

    // Configuración de estilos para campos de formulario
    setupFormFields(formFields);

    // Configuración del input de archivo
    if (fileInput) {
        setupFileInput(fileInput, previewContainer);
    }

    // Configuración de eventos para el selectpicker
    $('.select-pais').on('loaded.bs.select', function () {
        $(this).parent().addClass('animated-select');
    });

    console.log("Interfaz inicializada correctamente (setupUI)");
}

function setupFormFields(formFields) {
    formFields.forEach(field => {
        const input = field.querySelector('input, select, textarea');
        if (input) {
            input.addEventListener('focus', () => {
                animateFieldFocus(field);
            });

            input.addEventListener('blur', () => {
                animateFieldBlur(field);
            });
        }
    });
}

function animateFieldFocus(field) {
    const label = field.querySelector('label');
    if (label) {
        label.style.color = '#3a86ff';
    }
    field.style.transform = 'translateY(-2px)';
}

function animateFieldBlur(field) {
    const label = field.querySelector('label');
    if (label) {
        label.style.color = '#1a1a2e';
    }
    field.style.transform = 'translateY(0)';
}

function setupFileInput(fileInput, previewContainer) {
    // Solo crear el label si no existe ya
    if (!fileInput.nextElementSibling?.classList.contains('file-label')) {
        const fileLabel = document.createElement('div');
        fileLabel.className = 'file-label';
        fileLabel.innerHTML = `
            <span class="file-text">${fileInput.files.length ? fileInput.files[0].name : 'Seleccionar archivo'}</span>
            <span class="icon">📁</span>
        `;
        fileInput.parentNode.insertBefore(fileLabel, fileInput.nextSibling);
        
        // Estilos para el input de archivo
        fileInput.style.opacity = '0';
        fileInput.style.position = 'absolute';
        fileInput.style.width = '100%';
        fileInput.style.height = '100%';
        fileInput.style.left = '0';
        fileInput.style.top = '0';
        fileInput.style.cursor = 'pointer';
    }

    fileInput.addEventListener('change', () => {
        handleFileChange(fileInput, previewContainer);
    });
}

function handleFileChange(fileInput, previewContainer) {
    const file = fileInput.files[0];
    const fileLabel = fileInput.nextElementSibling;
    const fileName = file?.name || 'Seleccionar archivo';
    
    if (fileLabel && fileLabel.classList.contains('file-label')) {
        fileLabel.querySelector('.file-text').textContent = fileName;

        if (file) {
            const maxSize = 2 * 1024 * 1024;
            if (file.size > maxSize) {
                showFileError(fileInput, fileLabel);
                return;
            }

            previewFile(file, previewContainer);
            showFileSuccess(fileLabel);
        } else {
            previewContainer.innerHTML = '<p>No hay archivo seleccionado</p>';
        }
    }
}

function showFileError(fileInput, fileLabel) {
    fileLabel.style.borderColor = '#ff006e';
    fileLabel.style.backgroundColor = 'rgba(255, 0, 110, 0.1)';
    setTimeout(() => {
        fileLabel.style.borderColor = '#e0e0e0';
        fileLabel.style.backgroundColor = '#f8f9fa';
        fileInput.value = '';
        fileLabel.querySelector('.file-text').textContent = 'Seleccionar archivo';
    }, 2000);
}

function showFileSuccess(fileLabel) {
    fileLabel.style.borderColor = '#06d6a0';
    fileLabel.style.backgroundColor = 'rgba(6, 214, 160, 0.1)';
    setTimeout(() => {
        fileLabel.style.borderColor = '#3a86ff';
        fileLabel.style.backgroundColor = 'rgba(58, 134, 255, 0.05)';
    }, 1000);
}

function previewFile(file, previewContainer) {
    const reader = new FileReader();
    reader.onload = e => {
        previewContainer.innerHTML = `
            <div class="fade-in-image">
                <img src="${e.target.result}" alt="Logo Preview" />
                <div class="mini-thumb">Miniatura seleccionada</div>
            </div>
        `;
    };
    reader.readAsDataURL(file);
}