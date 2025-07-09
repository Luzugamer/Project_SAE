// Búsqueda rápida
function quickSearch(term) {
    document.getElementById('searchInput').value = term;
    document.getElementById('searchForm').submit();
}

// Limpiar búsqueda
function clearSearch() {
    window.location.href = "{% url 'comunidad:buscar_comunidades' %}";
}

// Animación al unirse a comunidad
function joinCommunity(button, communityName) {
    button.innerHTML = '<span>⏳</span> Uniéndose...';
    button.style.background = 'linear-gradient(135deg, #ED8936, #DD6B20)';
    
    setTimeout(() => {
        button.innerHTML = '<span>✅</span> ¡Te has unido!';
        button.style.background = 'linear-gradient(135deg, #48BB78, #38A169)';
    }, 1000);
}

// Mostrar loading al buscar
document.getElementById('searchForm').addEventListener('submit', function() {
    document.getElementById('loadingState').style.display = 'block';
    document.getElementById('resultsGrid').style.opacity = '0.5';
});

// Animaciones de entrada
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.community-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 100}ms`;
    });

    // Filtros activos
    const filters = document.querySelectorAll('.filter-tag');
    filters.forEach(filter => {
        filter.addEventListener('click', function() {
            filters.forEach(f => f.classList.remove('active'));
            this.classList.add('active');
        });
    });
});

// Búsqueda en tiempo real (opcional)
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value.trim();
    
    if (query.length > 2) {
        searchTimeout = setTimeout(() => {
            // Aquí podrías implementar búsqueda AJAX en tiempo real
            console.log('Búsqueda en tiempo real:', query);
        }, 500);
    }
});

// Efectos de teclado
document.addEventListener('keydown', function(e) {
    if (e.key === '/' && e.target.tagName !== 'INPUT') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
});
