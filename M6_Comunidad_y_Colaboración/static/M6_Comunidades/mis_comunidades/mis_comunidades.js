function toggleCommunity(communityId) {
    const content = document.getElementById(`content-${communityId}`);
    const isExpanded = content.classList.contains('expanded');
    
    // Cerrar todas las demás comunidades
    document.querySelectorAll('.community-content').forEach(el => {
        el.classList.remove('expanded');
    });
    
    // Abrir/cerrar la comunidad actual
    if (!isExpanded) {
        content.classList.add('expanded');
        
        // Animación suave de scroll
        setTimeout(() => {
            content.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }, 100);
    }
}

// Animaciones adicionales
document.addEventListener('DOMContentLoaded', function() {
    // Animar las tarjetas al cargar
    const cards = document.querySelectorAll('.community-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 200);
    });
});
