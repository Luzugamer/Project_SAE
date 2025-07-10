// repositorio_logic.js

document.addEventListener('DOMContentLoaded', function () {
    initializeRepository();
});

function initializeRepository() {
    setupSearch();
    setupUniversityCards();
    setupFilterOptions();
    setupFiltroToggle();
    setupFiltroAnimado();
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
    console.log(`Cargando exámenes para universidad ${universidadId}`);
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
                'Content-Type': 'application/json'
            }
        })
        .then(res => {
            if (!res.ok) throw new Error('Error al eliminar');
            return res.json();
        })
        .then(() => {
            showNotification('Examen eliminado');
            location.reload();
        })
        .catch(err => {
            console.error(err);
            showNotification('Error al eliminar', 'error');
        });
    });
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
    fetch(url)
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

        const matchTexto = nombre.includes(term) || pais.includes(term) || esp.includes(term) || tipo.includes(term);
        const matchPais = !checkPais || (valPais && pais === valPais.toLowerCase());
        const matchTipo = !checkTipo || (valTipo && tipo === valTipo.toLowerCase());

        if (matchTexto && matchPais && matchEsp && matchTipo) {
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

window.mostrarFormulario = mostrarFormulario;
window.editarExamen = editarExamen;
window.confirmarEliminarExamen = confirmarEliminarExamen;
window.confirmarEliminarRepositorio = confirmarEliminarRepositorio;
window.abrirModalConFormulario = abrirModalConFormulario;
window.cerrarModalFormulario = cerrarModalFormulario;
window.showNotification = showNotification;
window.editarExamenDesdeDataset = editarExamenDesdeDataset;