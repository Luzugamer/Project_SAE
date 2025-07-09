function irAComunidad(url) {
    window.location.href = url;
}

function confirmarEliminacion(comunidadId, nombreComunidad) {
    if (confirm(`¿Estás seguro de que deseas eliminar la comunidad "${nombreComunidad}"?`)) {
        // Aquí puedes agregar la lógica para eliminar la comunidad
        // Por ejemplo, enviar una petición AJAX o redirigir a una URL de eliminación
        window.location.href = `{% url 'comunidad:eliminar_comunidad' 0 %}`.replace('0', comunidadId);
    }
}

function confirmarEliminacion(comunidadId, nombreComunidad) {
    const modal = document.getElementById('deleteModal');
    const message = document.getElementById('deleteMessage');
    const form = document.getElementById('deleteForm');
    
    message.textContent = `Esta acción eliminará permanentemente la comunidad "${nombreComunidad}" y todos sus mensajes.`;
    form.action = `/comunidad/${comunidadId}/eliminar/`;
    
    modal.style.display = 'flex';
}

function cerrarModalEliminacion() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Cerrar modal al hacer clic fuera
document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) {
        cerrarModalEliminacion();
    }
});

// Animaciones de carga
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.community-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Efecto de hover en las tarjetas
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.community-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
});
