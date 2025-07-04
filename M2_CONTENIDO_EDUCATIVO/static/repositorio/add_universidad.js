document.addEventListener('DOMContentLoaded', () => {
    // Inicializar select con animación
    $('.select-pais').selectpicker({
        liveSearch: true,
        size: 5,
        style: 'btn-light',
        showSubtext: true,
        noneSelectedText: 'Seleccione un país...'
    }).on('loaded.bs.select', function () {
        $(this).parent().addClass('animated-select');
    });

    const form = document.getElementById('form-universidad');
    const fileInput = document.querySelector('input[type="file"][name="logo"]');
    const previewContainer = document.querySelector('.logo-preview');
    const modalPrevia = document.getElementById('modal-previa');
    const submitBtn = form?.querySelector('button[type="submit"]');
    let originalBtnText = submitBtn?.textContent;
    const isEditMode = form?.dataset.edit === 'true';

    // Hover animado en campos
    const formFields = document.querySelectorAll('.form-field');
    formFields.forEach(field => {
        const input = field.querySelector('input, select, textarea');
        if (input) {
            input.addEventListener('focus', () => {
                field.querySelector('label').style.color = '#3a86ff';
                field.style.transform = 'translateY(-2px)';
            });

            input.addEventListener('blur', () => {
                field.querySelector('label').style.color = '#1a1a2e';
                field.style.transform = 'translateY(0)';
            });
        }
    });

    // Campo de archivo estilizado
    const fileLabel = document.createElement('div');
    fileLabel.className = 'file-label';
    fileLabel.innerHTML = `
        <span class="file-text">Seleccionar archivo</span>
        <span class="icon">📁</span>
    `;

    if (fileInput) {
    // Solo crear el label si no existe ya
    if (!fileInput.nextElementSibling?.classList.contains('file-label')) {
        const fileLabel = document.createElement('div');
        fileLabel.className = 'file-label';
        fileLabel.innerHTML = `
            <span class="file-text">${fileInput.files.length ? fileInput.files[0].name : 'Seleccionar archivo'}</span>
            <span class="icon">📁</span>
        `;
        fileInput.parentNode.insertBefore(fileLabel, fileInput.nextSibling);
        
        // Haz el input transparente pero no lo ocultes completamente
        fileInput.style.opacity = '0';
        fileInput.style.position = 'absolute';
        fileInput.style.width = '100%';
        fileInput.style.height = '100%';
        fileInput.style.left = '0';
        fileInput.style.top = '0';
        fileInput.style.cursor = 'pointer';
    }

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        const fileLabel = fileInput.nextElementSibling;
        const fileName = file?.name || 'Seleccionar archivo';
        
        if (fileLabel && fileLabel.classList.contains('file-label')) {
            fileLabel.querySelector('.file-text').textContent = fileName;

            if (file) {
                const maxSize = 2 * 1024 * 1024;
                if (file.size > maxSize) {
                    fileLabel.style.borderColor = '#ff006e';
                    fileLabel.style.backgroundColor = 'rgba(255, 0, 110, 0.1)';
                    setTimeout(() => {
                        fileLabel.style.borderColor = '#e0e0e0';
                        fileLabel.style.backgroundColor = '#f8f9fa';
                        fileInput.value = '';
                        fileLabel.querySelector('.file-text').textContent = 'Seleccionar archivo';
                    }, 2000);
                    return;
                }

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

                // Confirmación visual
                fileLabel.style.borderColor = '#06d6a0';
                fileLabel.style.backgroundColor = 'rgba(6, 214, 160, 0.1)';
                setTimeout(() => {
                    fileLabel.style.borderColor = '#3a86ff';
                    fileLabel.style.backgroundColor = 'rgba(58, 134, 255, 0.05)';
                }, 1000);
            } else {
                previewContainer.innerHTML = '<p>No hay archivo seleccionado</p>';
            }
        }
    });
}

    // Envío del formulario
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = isEditMode ? 'Actualizando...' : 'Guardando...';
            }

            const formData = new FormData(form);

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
                    if (data.preview) {
                        mostrarPrevisualizacion(data);
                    } else if (data.redirect) {
                        window.location.href = URLS.repositorio;
                    }
                } else {
                    throw new Error(data.errors || 'Error al procesar la solicitud');
                }
            })
            .catch(err => {
                alert('Error: ' + (err.message || 'Error desconocido'));
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

    // Modal acciones
    if (modalPrevia) {
        document.getElementById('btn-editar')?.addEventListener('click', cerrarModalPrevia);
        document.getElementById('btn-guardar')?.addEventListener('click', () => confirmarGuardado(false));
        document.getElementById('btn-agregar-otra')?.addEventListener('click', () => confirmarGuardado(true));

        if (isEditMode) {
            document.getElementById('btn-agregar-otra')?.style.setProperty('display', 'none');
        }
    }

    // Actualización de vista previa rápida
    const camposParaPrevia = ['nombre', 'pais', 'especialidad', 'tipo_solucionario'];
    camposParaPrevia.forEach(campo => {
        const input = document.querySelector(`[name="${campo}"]`);
        if (input) input.addEventListener('change', actualizarPreviaRapida);
    });

    function actualizarPreviaRapida() {
        const nombre = document.querySelector('[name="nombre"]').value;
        const pais = document.querySelector('[name="pais"] option:checked')?.textContent;
        const especialidad = document.querySelector('[name="especialidad"]').value;
        const tipo = document.querySelector('[name="tipo_solucionario"] option:checked')?.textContent;

        if (nombre) document.getElementById('previa-nombre').textContent = nombre;
        if (pais) document.getElementById('previa-pais').textContent = pais;
        if (especialidad) document.getElementById('previa-especialidad').textContent = especialidad;
        if (tipo) document.getElementById('previa-tipo').textContent = tipo;
    }
});

// Funciones globales reutilizadas
function confirmarGuardado(addAnother) {
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
            throw new Error(data.errors || 'Error al guardar');
        }
    })
    .catch(err => {
        console.error('Error completo:', err);
        alert('Error: ' + (err.message || 'Error al procesar la solicitud'));
    })
    .finally(() => {
        buttons.forEach(btn => {
            btn.textContent = btn.dataset.originalText;
            btn.disabled = false;
        });
    });
}

function mostrarPrevisualizacion(data) {
    const modal = document.getElementById('modal-previa');
    if (!modal) return;

    document.getElementById('previa-nombre').textContent = data.nombre;
    document.getElementById('previa-pais').textContent = data.pais;
    document.getElementById('previa-especialidad').textContent = data.especialidad;
    document.getElementById('previa-tipo').textContent = data.tipo_solucionario;

    const logo = document.getElementById('previa-logo');
    if (data.logo_url) {
        logo.src = data.logo_url;
        logo.style.display = 'block';
    } else {
        logo.style.display = 'none';
    }

    if (data.is_edit) {
        const btnAgregarOtra = document.getElementById('btn-agregar-otra');
        if (btnAgregarOtra) btnAgregarOtra.style.display = 'none';
        const btnGuardar = document.getElementById('btn-guardar');
        if (btnGuardar) btnGuardar.textContent = 'Guardar cambios';
    }

    modal.style.display = 'flex';
}

function cerrarModalPrevia() {
    const modal = document.getElementById('modal-previa');
    if (modal) modal.style.display = 'none';
}
