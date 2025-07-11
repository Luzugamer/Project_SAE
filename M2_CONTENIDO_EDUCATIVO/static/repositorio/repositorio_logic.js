document.addEventListener('DOMContentLoaded', function () {
    initializeRepository();
});

function initializeRepository() {
    setupSearch();
    setupUniversityCards();
    setupFilterOptions();
    setupFiltroToggle();
    setupFiltroAnimado();
    setupFormHandlers();
}

function setupSearch() {
    const searchInput = document.querySelector('input[type="text"]');
    if (!searchInput) return;

    let searchTimeout;

    searchInput.addEventListener('input', function (e) {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            applyCombinedFilters(e.target.value);
        }, 300);
    });
}

function setupUniversityCards() {
    const tarjetas = document.querySelectorAll('.tarjeta:not(.tarjeta-agregar)');

    tarjetas.forEach(tarjeta => {
        if (!tarjeta.dataset.universidadId) return;

        const header = tarjeta.querySelector('.tarjeta-header');
        if (header) {
            header.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleUniversityCard(tarjeta);
            });
        }
    });
}

function toggleUniversityCard(tarjeta) {
    const universidadId = tarjeta.dataset.universidadId;
    const examenesContainer = tarjeta.querySelector('.examenes-container');

    if (!universidadId || !examenesContainer) return;

    const isExpanded = tarjeta.classList.contains('expanded');

    document.querySelectorAll('.tarjeta.expanded').forEach(otherCard => {
        if (otherCard !== tarjeta) {
            collapseCard(otherCard);
        }
    });

    if (isExpanded) {
        collapseCard(tarjeta);
    } else {
        expandCard(tarjeta);
        if (!examenesContainer.dataset.loaded) {
            loadExamenes(universidadId, examenesContainer);
        }
    }
}

function loadExamenes(universidadId, container) {
    container.dataset.loaded = 'true';
    
    fetch(`/repositorio/universidad/${universidadId}/examenes/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': window.csrfToken
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error al cargar exámenes');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            renderExamenes(container, data.examenes, universidadId);
        } else {
            throw new Error(data.error || 'Error al cargar exámenes');
        }
    })
    .catch(error => {
        console.error('Error cargando exámenes:', error);
        container.innerHTML = '<p class="error">Error al cargar los exámenes</p>';
    });
}

function renderExamenes(container, examenes, universidadId) {
    const examenesList = container.querySelector('.examenes-list');
    if (!examenesList) return;

    examenesList.innerHTML = '';

    examenes.forEach(examen => {
        const examenElement = createExamenElement(examen, universidadId);
        examenesList.appendChild(examenElement);
    });
}

function createExamenElement(examen, universidadId) {
    const div = document.createElement('div');
    div.className = 'examen-item';
    div.innerHTML = `
        <div class="examen-info">
            <h4>${examen.nombre}</h4>
            <p class="fecha">${examen.fecha}</p>
            ${examen.miniatura_url ? `<img src="${examen.miniatura_url}" alt="Miniatura" class="miniatura">` : ''}
        </div>
        <div class="examen-actions">
            <button class="btn-editar" 
                    data-universidad-id="${universidadId}" 
                    data-examen-id="${examen.id}" 
                    data-nombre="${examen.nombre}" 
                    data-fecha="${examen.fecha}"
                    onclick="editarExamenDesdeDataset(this)">
                Editar
            </button>
            <button class="btn-eliminar" onclick="confirmarEliminarExamen(${examen.id})">
                Eliminar
            </button>
            ${examen.archivo_url ? `<a href="${examen.archivo_url}" target="_blank" class="btn-ver">Ver</a>` : ''}
        </div>
    `;
    return div;
}

function setupFormHandlers() {
    // Interceptar envío de formularios de examen
    document.addEventListener('submit', function(e) {
        if (e.target.matches('form[action*="add-examen"], form[action*="editar"]')) {
            e.preventDefault();
            handleExamenFormSubmit(e.target);
        }
    });
}

function handleExamenFormSubmit(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Procesando...';

    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': window.csrfToken
        },
        body: formData
    })
    .then(response => {
        if (!response.ok) throw new Error('Error en la respuesta');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            handleExamenSuccess(data, form);
        } else {
            handleExamenError(data, form);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al procesar el formulario', 'error');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    });
}

function handleExamenSuccess(data, form) {
    showNotification(data.message, 'success');
    
    // Actualizar la UI con los datos del examen
    if (data.examen_data) {
        updateExamenInUI(data.examen_data, form);
    }
    
    // Limpiar y ocultar formulario
    form.reset();
    const formContainer = form.closest('.formulario-container');
    if (formContainer) {
        hideForm(formContainer);
    }
}

function handleExamenError(data, form) {
    if (data.errors) {
        displayFormErrors(form, data.errors);
    } else {
        showNotification(data.error || 'Error al procesar', 'error');
    }
}

function updateExamenInUI(examenData, form) {
    const isEditing = form.action.includes('editar');
    const universidadId = extractUniversidadIdFromForm(form);
    
    if (isEditing) {
        updateExistingExamen(examenData);
    } else {
        addNewExamenToUI(examenData, universidadId);
    }
}

function updateExistingExamen(examenData) {
    const examenItem = document.querySelector(`[data-examen-id="${examenData.id}"]`)?.closest('.examen-item');
    if (examenItem) {
        const newElement = createExamenElement(examenData, extractUniversidadIdFromExamen(examenItem));
        examenItem.replaceWith(newElement);
    }
}

function addNewExamenToUI(examenData, universidadId) {
    const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
    if (tarjeta) {
        const examenesList = tarjeta.querySelector('.examenes-list');
        if (examenesList) {
            const newElement = createExamenElement(examenData, universidadId);
            examenesList.insertBefore(newElement, examenesList.firstChild);
        }
    }
}

function extractUniversidadIdFromForm(form) {
    const match = form.action.match(/universidad\/(\d+)/);
    return match ? match[1] : null;
}

function extractUniversidadIdFromExamen(examenElement) {
    const btn = examenElement.querySelector('[data-universidad-id]');
    return btn ? btn.dataset.universidadId : null;
}

function displayFormErrors(form, errors) {
    // Limpiar errores anteriores
    form.querySelectorAll('.error-message').forEach(el => el.remove());
    
    // Mostrar nuevos errores
    Object.keys(errors).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = errors[fieldName][0];
            field.parentNode.insertBefore(errorDiv, field.nextSibling);
        }
    });
}

function mostrarFormulario(universidadId) {
    const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
    if (!tarjeta) return;

    const originalForm = tarjeta.querySelector(`#formulario-examen-${universidadId}`);
    const formElement = originalForm?.querySelector('form');
    const examenesList = tarjeta.querySelector('.examenes-list');

    if (originalForm.style.display !== 'none') {
        hideForm(originalForm);
        return;
    }

    formElement.reset();
    formElement.action = `/repositorio/universidad/${universidadId}/add-examen/`;
    formElement.querySelector('input[name="examen_id"]').value = '';
    formElement.querySelector('button[type="submit"]').textContent = 'Subir';

    if (examenesList.firstChild) {
        examenesList.insertBefore(originalForm, examenesList.firstChild);
    }

    showForm(originalForm);
    expandCard(tarjeta);
}

function editarExamen(universidadId, examenId, nombre, fecha) {
    const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
    if (!tarjeta) return;

    const originalForm = tarjeta.querySelector(`#formulario-examen-${universidadId}`);
    if (!originalForm) return;

    const formElement = originalForm.querySelector('form');
    const inputHiddenId = formElement.querySelector('input[name="examen_id"]');
    const isEditingSame = inputHiddenId?.value === examenId;

    if (originalForm.style.display !== 'none' && isEditingSame) {
        hideForm(originalForm);
        return;
    }

    formElement.action = `/repositorio/examen/${examenId}/editar/`;
    inputHiddenId.value = examenId;
    formElement.querySelector('input[name="nombre"]').value = nombre;
    formElement.querySelector('input[name="fecha"]').value = fecha;
    const inputArchivo = formElement.querySelector('input[name="archivo"]');
    if (inputArchivo) inputArchivo.value = '';

    formElement.querySelector('button[type="submit"]').textContent = 'Actualizar';

    const examenItem = tarjeta.querySelector(`.examen-item button[data-examen-id="${examenId}"]`)?.closest('.examen-item');
    if (examenItem && examenItem.nextSibling) {
        examenItem.parentNode.insertBefore(originalForm, examenItem.nextSibling);
    }

    showForm(originalForm);
    expandCard(tarjeta);
}

function editarExamenDesdeDataset(button) {
    const universidadId = button.dataset.universidadId;
    const examenId = button.dataset.examenId;
    const nombre = button.dataset.nombre;
    const fecha = button.dataset.fecha;

    editarExamen(universidadId, examenId, nombre, fecha);
}

function confirmarEliminarExamen(examenId) {
    mostrarModal("¿Seguro que quiere eliminar este examen?", () => {
        fetch(`/repositorio/examen/${examenId}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al eliminar');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                removeExamenFromUI(examenId);
            } else {
                throw new Error(data.error || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error al eliminar', 'error');
        });
    });
}

function removeExamenFromUI(examenId) {
    const examenItem = document.querySelector(`[data-examen-id="${examenId}"]`)?.closest('.examen-item');
    if (examenItem) {
        examenItem.remove();
    }
}

function confirmarEliminarRepositorio(universidadId) {
    mostrarModal("¿Seguro que quiere eliminar este repositorio? Esta acción no se puede deshacer.", () => {
        const btn = document.querySelector(`.btn-eliminar-repositorio[onclick*="${universidadId}"]`);
        if (btn) btn.classList.add('loading');

        fetch(`/repositorio/universidad/${universidadId}/eliminar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': window.csrfToken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                removeUniversityCard(universidadId);
            } else {
                throw new Error(data.message || 'Error al eliminar');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification(error.message || 'Error al eliminar el repositorio', 'error');
        })
        .finally(() => {
            if (btn) btn.classList.remove('loading');
        });
    });
}

function mostrarModal(mensaje, callbackConfirmar) {
    const modal = document.getElementById('modal-confirmacion');
    const mensajeElem = document.getElementById('modal-mensaje');
    const btnConfirmar = document.getElementById('btn-confirmar');
    const btnCancelar = document.getElementById('btn-cancelar');

    if (!modal || !mensajeElem || !btnConfirmar || !btnCancelar) {
        console.error("Elementos del modal no encontrados");
        return;
    }

    mensajeElem.textContent = mensaje;
    showModal(modal);

    btnConfirmar.onclick = () => {
        hideModal(modal);
        callbackConfirmar();
    };

    btnCancelar.onclick = () => {
        hideModal(modal);
    };
}

function abrirModalConFormulario(url) {
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => {
            if (!response.ok) throw new Error('No se pudo cargar el formulario');
            return response.text();
        })
        .then(html => {
            const modal = document.getElementById('modal-formulario');
            const contenido = document.getElementById('modal-formulario-body');
            contenido.innerHTML = html;
            showModal(modal);
        })
        .catch(error => {
            alert('Error al cargar el formulario');
            console.error(error);
        });
}

function cerrarModalFormulario() {
    const modal = document.getElementById('modal-formulario');
    const contenido = document.getElementById('modal-formulario-body');
    contenido.innerHTML = '';
    hideModal(modal);
}

function setupFilterOptions() {
    const filtroContenedor = document.querySelector('.filtro-opciones');
    const toggleBtn = document.getElementById('toggle-opciones');
    const filtros = document.getElementById('contenedor-filtros');

    if (!filtroContenedor || !toggleBtn || !filtros) return;

    filtroContenedor.style.display = 'block';

    toggleBtn.addEventListener('click', () => {
        filtros.style.display = filtros.style.display === 'none' ? 'flex' : 'none';
    });

    const tarjetas = document.querySelectorAll('.tarjeta:not(.tarjeta-agregar)');
    const paises = new Set();
    const tipos = new Set();

    tarjetas.forEach(t => {
        paises.add(t.querySelector('.pais')?.textContent.trim());
        tipos.add(t.querySelector('.tipo-solucionario')?.textContent.trim());
    });

    fillSelect('filtro-pais', paises);
    fillSelect('filtro-tipo', tipos);

    document.getElementById('filtro-pais').addEventListener('change', applyCombinedFilters);
    document.getElementById('filtro-tipo').addEventListener('change', applyCombinedFilters);
    document.getElementById('check-pais').addEventListener('change', applyCombinedFilters);
    document.getElementById('check-tipo').addEventListener('change', applyCombinedFilters);
}

function fillSelect(id, values) {
    const select = document.getElementById(id);
    values.forEach(value => {
        if (value && !select.querySelector(`option[value="${value}"]`)) {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            select.appendChild(option);
        }
    });
}

function applyCombinedFilters() {
    const term = document.querySelector('input[type="text"]').value.toLowerCase().trim();
    const tarjetas = document.querySelectorAll('.tarjeta:not(.tarjeta-agregar)');

    const checkPais = document.getElementById('check-pais').checked;
    const checkTipo = document.getElementById('check-tipo').checked;

    const valPais = document.getElementById('filtro-pais').value;
    const valTipo = document.getElementById('filtro-tipo').value;

    tarjetas.forEach(tarjeta => {
        const nombre = tarjeta.querySelector('h3')?.textContent.toLowerCase() || '';
        const pais = tarjeta.querySelector('.pais')?.textContent.toLowerCase() || '';
        const tipo = tarjeta.querySelector('.tipo-solucionario')?.textContent.toLowerCase() || '';

        const matchTexto = nombre.includes(term) || pais.includes(term) || tipo.includes(term);
        const matchPais = !checkPais || (valPais && pais === valPais.toLowerCase());
        const matchTipo = !checkTipo || (valTipo && tipo === valTipo.toLowerCase());

        if (matchTexto && matchPais && matchTipo) {
            tarjeta.style.display = 'block';
        } else {
            tarjeta.style.display = 'none';
        }
    });
}

function setupFiltroToggle() {
    const btnToggle = document.getElementById('toggle-filtros');
    const contenedor = document.getElementById('contenedor-filtros');

    if (!btnToggle || !contenedor) return;

    btnToggle.addEventListener('click', () => {
        contenedor.classList.toggle('oculto');
        document.body.classList.toggle('filtros-activos');
    });
}

function setupFiltroAnimado() {
    const boton = document.getElementById('toggle-opciones');
    const contenedor = document.getElementById('contenedor-filtros');

    if (boton && contenedor) {
        boton.addEventListener('click', () => {
            contenedor.classList.toggle('show');
            boton.classList.toggle('open');
        });
    }
}

// Exportar funciones al scope global
window.mostrarFormulario = mostrarFormulario;
window.editarExamen = editarExamen;
window.confirmarEliminarExamen = confirmarEliminarExamen;
window.confirmarEliminarRepositorio = confirmarEliminarRepositorio;
window.abrirModalConFormulario = abrirModalConFormulario;
window.cerrarModalFormulario = cerrarModalFormulario;
window.showNotification = showNotification;
window.editarExamenDesdeDataset = editarExamenDesdeDataset;