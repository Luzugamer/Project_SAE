let archivoSeleccionado = null;

function actualizarVistaPrevia() {
    const nombre = document.getElementById('nombre').value || 'Nombre de la Comunidad';
    const descripcion = document.getElementById('descripcion').value || 'La descripción de tu comunidad aparecerá aquí...';
    const institucion = document.getElementById('institucion_afiliada').value || 'Sin institución especificada';

    document.getElementById('preview-nombre').textContent = nombre;
    document.getElementById('preview-descripcion').textContent = descripcion;
    document.getElementById('preview-institucion').textContent = institucion;
}

function manejarArchivo(input) {
    const file = input.files[0];
    const fileText = document.getElementById('file-text');
    const previewIcon = document.getElementById('preview-icon');

    if (file) {
        // Validar tipo de archivo
        const tiposPermitidos = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
        if (!tiposPermitidos.includes(file.type)) {
            alert('Por favor selecciona un archivo de imagen válido (JPG, PNG, GIF)');
            input.value = '';
            return;
        }

        // Validar tamaño (5MB máximo)
        if (file.size > 5 * 1024 * 1024) {
            alert('El archivo es demasiado grande. El tamaño máximo es 5MB.');
            input.value = '';
            return;
        }

        fileText.innerHTML = `✅ ${file.name}`;
        archivoSeleccionado = file;

        // Mostrar vista previa de la imagen
        const reader = new FileReader();
        reader.onload = function(e) {
            previewIcon.innerHTML = `<img src="${e.target.result}" alt="Vista previa">`;
        };
        reader.readAsDataURL(file);
    } else {
        fileText.innerHTML = '📸 Haz clic para seleccionar una imagen';
        previewIcon.innerHTML = '🏫';
        archivoSeleccionado = null;
    }
}

// Validación del formulario antes del envío
document.getElementById('comunidadForm').addEventListener('submit', function(e) {
    const nombre = document.getElementById('nombre').value.trim();
    const descripcion = document.getElementById('descripcion').value.trim();

    if (!nombre || !descripcion) {
        e.preventDefault();
        alert('Por favor completa todos los campos requeridos (marcados con *).');
        return;
    }

    if (nombre.length < 3) {
        e.preventDefault();
        alert('El nombre de la comunidad debe tener al menos 3 caracteres.');
        return;
    }

    if (descripcion.length < 10) {
        e.preventDefault();
        alert('La descripción debe tener al menos 10 caracteres.');
        return;
    }
});

// Inicializar vista previa
document.addEventListener('DOMContentLoaded', function() {
    actualizarVistaPrevia();
});

// Prevenir pérdida de datos
let formModificado = false;
const form = document.getElementById('comunidadForm');
form.addEventListener('input', function() {
    formModificado = true;
});
form.addEventListener('submit', function() {
    formModificado = false;
});
windows.addEventListener('beforeunload', function(e) {
    if (formModificado) {
        e.preventDefault();
        e.returnValue = '';
    }
});
