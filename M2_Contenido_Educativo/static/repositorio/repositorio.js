// repositorio.js

document.addEventListener('DOMContentLoaded', function () {
    initializeRepository();
});

function initializeRepository() {
    setupSearch();
    setupUniversityCards();
    addDynamicStyles();
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

    searchInput.addEventListener('focus', function () {
        this.parentElement.classList.add('focused');
    });

    searchInput.addEventListener('blur', function () {
        this.parentElement.classList.remove('focused');
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

function expandCard(tarjeta) {
    const examenesContainer = tarjeta.querySelector('.examenes-container');
    if (!examenesContainer) return;

    tarjeta.classList.add('expanded');
    requestAnimationFrame(() => {
        const scrollHeight = examenesContainer.scrollHeight;
        examenesContainer.style.maxHeight = scrollHeight + 'px';
        examenesContainer.style.overflow = 'visible';
    });
}

function collapseCard(tarjeta) {
    const examenesContainer = tarjeta.querySelector('.examenes-container');
    if (!examenesContainer) return;

    const scrollHeight = examenesContainer.scrollHeight;

    // Establece la altura explícitamente antes de ocultar para que funcione la transición
    examenesContainer.style.maxHeight = scrollHeight + 'px';
    examenesContainer.style.overflow = 'hidden';

    requestAnimationFrame(() => {
        tarjeta.classList.remove('expanded');
        examenesContainer.style.maxHeight = '0px';
    });
}

function mostrarFormulario(universidadId) {
    const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
    if (!tarjeta) return;

    const originalForm = tarjeta.querySelector(`#formulario-examen-${universidadId}`);
    const formElement = originalForm?.querySelector('form');
    const examenesList = tarjeta.querySelector('.examenes-list');

    // Si ya está visible, ocultarlo con animación
    if (originalForm.style.display !== 'none') {
        originalForm.style.opacity = '0';
        setTimeout(() => {
            originalForm.style.display = 'none';
        }, 200);
        return;
    }

    // Reiniciar para modo crear
    formElement.reset();
    formElement.action = `/repositorio/universidad/${universidadId}/add-examen/`;
    formElement.querySelector('input[name="examen_id"]').value = '';
    formElement.querySelector('button[type="submit"]').textContent = 'Subir';

    // Mover el formulario al principio de la lista
    if (examenesList.firstChild) {
        examenesList.insertBefore(originalForm, examenesList.firstChild);
    }

    originalForm.style.display = 'block';
    originalForm.style.opacity = '0';
    setTimeout(() => {
        originalForm.style.opacity = '1';
    }, 50);

    expandCard(tarjeta);

    setTimeout(() => {
        const container = tarjeta.querySelector('.examenes-container');
        if (container && tarjeta.classList.contains('expanded')) {
            container.style.maxHeight = container.scrollHeight + 'px';
        }
    }, 100);
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
        originalForm.style.opacity = '0';
        setTimeout(() => {
            originalForm.style.display = 'none';
            formElement.reset();
            formElement.action = `/repositorio/universidad/${universidadId}/add-examen/`;
            inputHiddenId.value = '';
            formElement.querySelector('button[type="submit"]').textContent = 'Subir';
        }, 200);
        return;
    }

    // Llenar valores
    formElement.action = `/repositorio/examen/${examenId}/editar/`;
    inputHiddenId.value = examenId;
    formElement.querySelector('input[name="nombre"]').value = nombre;
    formElement.querySelector('input[name="fecha"]').value = fecha;
    const inputArchivo = formElement.querySelector('input[name="archivo"]');
    if (inputArchivo) inputArchivo.value = '';

    formElement.querySelector('button[type="submit"]').textContent = 'Actualizar';

    // Insertar el formulario justo después del examen a editar
    const examenItem = tarjeta.querySelector(`.examen-item button[data-examen-id="${examenId}"]`)?.closest('.examen-item');
    if (examenItem && examenItem.nextSibling) {
        examenItem.parentNode.insertBefore(originalForm, examenItem.nextSibling);
    }

    originalForm.style.display = 'block';
    originalForm.style.opacity = '0';

    expandCard(tarjeta);

    setTimeout(() => {
        originalForm.style.opacity = '1';
        const container = tarjeta.querySelector('.examenes-container');
        if (container) {
            container.style.maxHeight = container.scrollHeight + 'px';
        }
    }, 100);
}



function editarExamenDesdeDataset(button) {
    const universidadId = button.dataset.universidadId;
    const examenId = button.dataset.examenId;
    const nombre = button.dataset.nombre;
    const fecha = button.dataset.fecha;

    editarExamen(universidadId, examenId, nombre, fecha);
}

function loadExamenes(universidadId, container) {
    container.dataset.loaded = 'true';
    console.log(`Cargando exámenes para universidad ${universidadId}`);
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.add('show');
    }, 100);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function addDynamicStyles() {
    const additionalStyles = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }
        .notification.show {
            transform: translateX(0);
        }
        .notification-success { background: #4CAF50; }
        .notification-error { background: #f44336; }
        .search-container.focused input {
            box-shadow: 0 8px 25px rgba(126, 212, 173, 0.3);
        }
        .btn-cancel {
            background: #f44336;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        .formulario-examen {
            transition: all 0.3s ease;
        }
        .tarjeta .examenes-container {
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            max-height: 0;
            overflow: hidden;
        }
        .tarjeta.expanded .examenes-container {
            overflow: visible;
        }
    `;

    if (!document.getElementById('repositorio-dynamic-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'repositorio-dynamic-styles';
        styleSheet.textContent = additionalStyles;
        document.head.appendChild(styleSheet);
    }
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
            location.reload(); // o eliminarlo del DOM si no quieres recargar
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
            body: JSON.stringify({}) // Envía un objeto vacío como body
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                showNotification(data.message, 'success');
                // Eliminar la tarjeta del DOM con animación
                const tarjeta = document.querySelector(`.tarjeta[data-universidad-id="${universidadId}"]`);
                tarjeta.style.transition = 'all 0.3s ease';
                tarjeta.style.opacity = '0';
                tarjeta.style.transform = 'translateX(100px)';
                setTimeout(() => tarjeta.remove(), 300);
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
    modal.style.display = 'flex';

    // Eliminar eventos anteriores para evitar múltiples ejecuciones
    btnConfirmar.onclick = () => {
        modal.style.display = 'none';
        callbackConfirmar();
    };

    btnCancelar.onclick = () => {
        modal.style.display = 'none';
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
            modal.style.display = 'flex';
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
    modal.style.display = 'none';
}

function setupFilterOptions() {
    const filtroContenedor = document.querySelector('.filtro-opciones');
    const toggleBtn = document.getElementById('toggle-opciones');
    const filtros = document.getElementById('contenedor-filtros');

    filtroContenedor.style.display = 'block';

    toggleBtn.addEventListener('click', () => {
        filtros.style.display = filtros.style.display === 'none' ? 'flex' : 'none';
    });

    // Extraer valores únicos desde las tarjetas
    const tarjetas = document.querySelectorAll('.tarjeta:not(.tarjeta-agregar)');
    const paises = new Set();
    const especialidades = new Set();
    const tipos = new Set();

    tarjetas.forEach(t => {
        paises.add(t.querySelector('.pais')?.textContent.trim());
        especialidades.add(t.querySelector('.especialidad')?.textContent.trim());
        tipos.add(t.querySelector('.tipo-solucionario')?.textContent.trim());
    });

    fillSelect('filtro-pais', paises);
    fillSelect('filtro-especialidad', especialidades);
    fillSelect('filtro-tipo', tipos);

    document.getElementById('filtro-pais').addEventListener('change', applyCombinedFilters);
    document.getElementById('filtro-especialidad').addEventListener('change', applyCombinedFilters);
    document.getElementById('filtro-tipo').addEventListener('change', applyCombinedFilters);
    document.getElementById('check-pais').addEventListener('change', applyCombinedFilters);
    document.getElementById('check-especialidad').addEventListener('change', applyCombinedFilters);
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
    const checkEspecialidad = document.getElementById('check-especialidad').checked;
    const checkTipo = document.getElementById('check-tipo').checked;

    const valPais = document.getElementById('filtro-pais').value;
    const valEsp = document.getElementById('filtro-especialidad').value;
    const valTipo = document.getElementById('filtro-tipo').value;

    tarjetas.forEach(tarjeta => {
        const nombre = tarjeta.querySelector('h3')?.textContent.toLowerCase() || '';
        const pais = tarjeta.querySelector('.pais')?.textContent.toLowerCase() || '';
        const esp = tarjeta.querySelector('.especialidad')?.textContent.toLowerCase() || '';
        const tipo = tarjeta.querySelector('.tipo-solucionario')?.textContent.toLowerCase() || '';

        const matchTexto = nombre.includes(term) || pais.includes(term) || esp.includes(term) || tipo.includes(term);
        const matchPais = !checkPais || (valPais && pais === valPais.toLowerCase());
        const matchEsp = !checkEspecialidad || (valEsp && esp === valEsp.toLowerCase());
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
            contenedor.classList.toggle('show');   // activa animación contenedor
            boton.classList.toggle('open');        // opcional: animación botón
        });
    }
}



// Cerrar vista previa al hacer clic fuera
document.addEventListener('click', function(e) {
    if (!e.target.closest('.examen-item') && !e.target.closest('.pdf-preview-container')) {
        document.querySelectorAll('.pdf-preview-container').forEach(container => {
            container.classList.remove('active');
        });
    }
});

// Mejorar la animación de los filtros
function setupFiltroAnimado() {
    const boton = document.getElementById('toggle-opciones');
    const contenedor = document.getElementById('contenedor-filtros');

    if (boton && contenedor) {
        boton.addEventListener('click', () => {
            if (contenedor.classList.contains('show')) {
                contenedor.classList.remove('show');
                setTimeout(() => {
                    contenedor.style.display = 'none';
                }, 300);
            } else {
                contenedor.style.display = 'flex';
                setTimeout(() => {
                    contenedor.classList.add('show');
                }, 10);
            }
            boton.classList.toggle('active');
        });
    }
}

function editarExamenDesdeDataset(button) {
    // Agregar clase de animación
    button.classList.add('clicked');
    
    // Eliminar la clase después de la animación
    setTimeout(() => {
        button.classList.remove('clicked');
    }, 300);
    
    // Resto de tu código existente...
    const universidadId = button.dataset.universidadId;
    const examenId = button.dataset.examenId;
    const nombre = button.dataset.nombre;
    const fecha = button.dataset.fecha;
    
    editarExamen(universidadId, examenId, nombre, fecha);
}

document.querySelectorAll('.btn-editar-repositorio').forEach(btn => {
    btn.addEventListener('click', function() {
        this.classList.add('loading');
        // Remover la clase después de 2 segundos (solo para demo)
        setTimeout(() => {
            this.classList.remove('loading');
        }, 2000);
    });
});



window.mostrarFormulario = mostrarFormulario;
window.editarExamen = editarExamen;
window.confirmarEliminarExamen = confirmarEliminarExamen;
window.confirmarEliminarRepositorio = confirmarEliminarRepositorio;
window.abrirModalConFormulario = abrirModalConFormulario;
window.cerrarModalFormulario = cerrarModalFormulario;
window.showNotification = showNotification;