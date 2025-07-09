let currentCommunityId = null;

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('active');
}

function mostrarModal(nombreComunidad, comunidadId) {
    document.getElementById('modalCommunityName').textContent = nombreComunidad;
    currentCommunityId = comunidadId;
    document.getElementById('joinModal').style.display = 'block';
}

function cerrarModal() {
    document.getElementById('joinModal').style.display = 'none';
    currentCommunityId = null;
}

function confirmarUnion() {
    if (currentCommunityId) {
        // Crear formulario para enviar POST request
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/comunidad/${currentCommunityId}/unirse/`;

        // Agregar token CSRF
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'csrfmiddlewaretoken';
            input.value = csrfToken.value;
            form.appendChild(input);
        }

        document.body.appendChild(form);
        form.submit();
    }
    cerrarModal();
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('joinModal');
    if (event.target === modal) {
        cerrarModal();
    }
}

// Cerrar sidebar al hacer clic fuera
document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    
    if (!sidebar.contains(event.target) && !toggle.contains(event.target)) {
        sidebar.classList.remove('active');
    }
});

// Animaciones al cargar
window.addEventListener('load', function() {
    const cards = document.querySelectorAll('.comunidad-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.style.animation = 'fadeInUp 0.6s ease forwards';
        }, index * 100);
    });
});
