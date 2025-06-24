// REEMPLAZAR todo el contenido de base.js con este código mejorado:
document.addEventListener('DOMContentLoaded', function () {
    const bottomNavbar = document.getElementById('bottomNavbar');
    const navItems = document.querySelectorAll('.nav-item');

    // Función para establecer el item activo basado en la URL actual
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        
        navItems.forEach(item => {
            item.classList.remove('active');
            
            // Verificar si la URL del enlace coincide con la página actual
            const itemHref = item.getAttribute('href');
            if (itemHref && (currentPath === itemHref || currentPath.includes(itemHref))) {
                item.classList.add('active');
            }
            
            // Verificación especial para la página principal
            if (currentPath.includes('/principal/') && item.getAttribute('data-page') === 'principal') {
                item.classList.add('active');
            }
        });
    }

    // Establecer el item activo al cargar la página
    setActiveNavItem();

    // Manejar clicks en nav items
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // NO preventDefault() - permite que los enlaces funcionen normalmente
            
            // Remover clase active de todos los items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Agregar clase active al item clickeado inmediatamente
            this.classList.add('active');
            
            // Forzar el estilo visual inmediatamente
            this.style.background = '#22d3ee';
            this.style.color = '#1e293b';
            this.style.fontWeight = '600';
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 30px rgba(34, 211, 238, 0.4)';
            
            // Guardar el estado en sessionStorage para persistencia
            const page = this.getAttribute('data-page');
            if (page) {
                sessionStorage.setItem('activeNavItem', page);
            }
        });

        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
                this.style.background = '';
                this.style.color = '';
                this.style.fontWeight = '';
                this.style.boxShadow = '';
            }
        });
    });

    // Restaurar estado activo desde sessionStorage
    const savedActiveItem = sessionStorage.getItem('activeNavItem');
    if (savedActiveItem) {
        const targetItem = document.querySelector(`[data-page="${savedActiveItem}"]`);
        if (targetItem) {
            navItems.forEach(nav => nav.classList.remove('active'));
            targetItem.classList.add('active');
        }
    }

    // Funcionalidad de hover para mostrar/ocultar navbar
    if (bottomNavbar) {
        let hoverTimeout;

        // Evento para mostrar navbar al hacer hover
        bottomNavbar.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            this.style.transform = 'translateX(-50%) translateY(0)';
        });

        // Evento para ocultar navbar al quitar el mouse
        bottomNavbar.addEventListener('mouseleave', function() {
            hoverTimeout = setTimeout(() => {
                this.style.transform = 'translateX(-50%) translateY(85%)';
            }, 300); // Pequeño delay para evitar parpadeo
        });

        // Mantener visible si el usuario está interactuando con los elementos
        navItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                clearTimeout(hoverTimeout);
            });
        });
    }

    // Mejorar la experiencia táctil en dispositivos móviles
    if ('ontouchstart' in window) {
        navItems.forEach(item => {
            item.addEventListener('touchstart', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
            });

            item.addEventListener('touchend', function() {
                setTimeout(() => {
                    if (!this.classList.contains('active')) {
                        this.style.transform = '';
                    }
                }, 150);
            });
        });

        // Funcionalidad táctil para dispositivos móviles
        if (bottomNavbar) {
            let touchStartY = 0;
            let isNavbarVisible = false;

            bottomNavbar.addEventListener('touchstart', function(e) {
                touchStartY = e.touches[0].clientY;
            });

            bottomNavbar.addEventListener('touchend', function(e) {
                const touchEndY = e.changedTouches[0].clientY;
                const touchDiff = touchStartY - touchEndY;

                // Si el usuario hace swipe hacia arriba, mostrar navbar
                if (touchDiff > 30 && !isNavbarVisible) {
                    this.style.transform = 'translateX(-50%) translateY(0)';
                    isNavbarVisible = true;
                    
                    // Auto-ocultar después de 3 segundos sin interacción
                    setTimeout(() => {
                        if (isNavbarVisible) {
                            this.style.transform = 'translateX(-50%) translateY(85%)';
                            isNavbarVisible = false;
                        }
                    }, 3000);
                }
                // Si el usuario hace swipe hacia abajo, ocultar navbar
                else if (touchDiff < -30 && isNavbarVisible) {
                    this.style.transform = 'translateX(-50%) translateY(85%)';
                    isNavbarVisible = false;
                }
            });
        }
    }

    // Funcionalidad adicional: mostrar navbar temporalmente cuando se carga la página
    if (bottomNavbar) {
        // Mostrar completamente por 2 segundos al cargar la página
        setTimeout(() => {
            bottomNavbar.style.transform = 'translateX(-50%) translateY(0)';
        }, 500);

        // Luego ocultar automáticamente
        setTimeout(() => {
            bottomNavbar.style.transform = 'translateX(-50%) translateY(85%)';
        }, 2000);
    }
});