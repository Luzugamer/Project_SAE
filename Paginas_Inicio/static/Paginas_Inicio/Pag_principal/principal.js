document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cardsContainer');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const originalCards = Array.from(document.querySelectorAll('.card'));
    
    let currentIndex = 0;
    const totalOriginalCards = originalCards.length;
    const radius = 400;
    let isAnimating = false;
    let cards = [];
    
    // Duración de la transición en milisegundos
    const TRANSITION_DURATION = 1000;
    
    // Número de clones a cada lado para el efecto infinito
    const CLONES_COUNT = 2;

    const angleStep = 360 / totalOriginalCards; // Basado en cartas originales
    
    // Crear clones para el efecto infinito
    function createInfiniteCarousel() {
        // Crear clones al final (primeras cartas)
        for (let i = 0; i < CLONES_COUNT; i++) {
            const clone = originalCards[i].cloneNode(true);
            clone.classList.add('clone', 'clone-end');
            clone.setAttribute('data-original-index', i);
            cardsContainer.appendChild(clone);
        }
        
        // Crear clones al principio (últimas cartas) - insertarlos al inicio
        for (let i = totalOriginalCards - CLONES_COUNT; i < totalOriginalCards; i++) {
            const clone = originalCards[i].cloneNode(true);
            clone.classList.add('clone', 'clone-start');
            clone.setAttribute('data-original-index', i);
            cardsContainer.insertBefore(clone, cardsContainer.firstChild);
        }
        
        // Actualizar el array de cartas
        cards = Array.from(cardsContainer.querySelectorAll('.card'));
        
        // Ajustar el índice inicial para empezar en la primera carta original
        currentIndex = CLONES_COUNT;
        
        console.log('Infinite carousel created:', {
            originalCards: totalOriginalCards,
            totalCards: cards.length,
            startIndex: currentIndex
        });
    }
    
    function updateCarousel(skipTransition = false) {
        if (isAnimating && !skipTransition) {
            console.log('Animation already in progress, blocking update');
            return;
        }
        
        if (!skipTransition) {
            isAnimating = true;
            prevBtn.classList.add('disabled');
            nextBtn.classList.add('disabled');
        }
        
        const rotation = -currentIndex * angleStep;
        
        if (skipTransition) {
            cardsContainer.style.transition = 'none';
        } else {
            cardsContainer.style.transition = 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)';
        }
        
        cardsContainer.style.transform = `rotateY(${rotation}deg)`;

        cards.forEach((card) => {
            card.classList.remove('active', 'side', 'back');

            let originalIndex = card.classList.contains('clone')
                ? parseInt(card.getAttribute('data-original-index'))
                : cards.indexOf(card) - CLONES_COUNT;

            const cardAngle = (originalIndex * angleStep) - (currentIndex * angleStep);
            const normalizedAngle = ((cardAngle % 360) + 360) % 360;

            const relativeAngle = normalizedAngle > 180 ? normalizedAngle - 360 : normalizedAngle;

            if (Math.abs(relativeAngle) < angleStep / 2) {
                card.classList.add('active');
            } else if (Math.abs(relativeAngle) < angleStep * 1.5) {
                card.classList.add('side');
            } else {
                card.classList.add('back');
            }
        });


        if (!skipTransition) {
            setTimeout(() => {
                checkAndResetPosition();
                isAnimating = false;
                prevBtn.classList.remove('disabled');
                nextBtn.classList.remove('disabled');
                updateActiveCardAnimation();
            }, TRANSITION_DURATION);
        } else {
            setTimeout(() => {
                cardsContainer.style.transition = 'transform 1s cubic-bezier(0.4, 0, 0.2, 1)';
            }, 50);
        }
    }
    
    function checkAndResetPosition() {
        const totalCards = cards.length;
        
        // Si estamos en un clon del final, saltar al inicio real
        if (currentIndex >= totalCards - CLONES_COUNT) {
            const newIndex = currentIndex - totalOriginalCards;
            console.log('Reset from end clone:', currentIndex, '→', newIndex);
            currentIndex = newIndex;
            updateCarousel(true); // Sin transición
        }
        // Si estamos en un clon del inicio, saltar al final real
        else if (currentIndex < CLONES_COUNT) {
            const newIndex = currentIndex + totalOriginalCards;
            console.log('Reset from start clone:', currentIndex, '→', newIndex);
            currentIndex = newIndex;
            updateCarousel(true); // Sin transición
        }
    }

    function nextCard() {
        if (isAnimating) {
            console.log('Animation in progress, ignoring nextCard click');
            return false;
        }
        
        console.log('nextCard called - currentIndex before:', currentIndex);
        currentIndex++;
        console.log('nextCard called - currentIndex after:', currentIndex);
        
        updateCarousel();
        return true;
    }
    
    function prevCard() {
        if (isAnimating) {
            console.log('Animation in progress, ignoring prevCard click');
            return false;
        }
        
        console.log('prevCard called - currentIndex before:', currentIndex);
        currentIndex--;
        console.log('prevCard called - currentIndex after:', currentIndex);
        
        updateCarousel();
        return true;
    }
    
    // Posicionar las cartas en círculo
    function positionCards() {
        cards.forEach((card, index) => {
            // Calcular el ángulo basándose en la posición original
            let originalIndex;
            if (card.classList.contains('clone')) {
                originalIndex = parseInt(card.getAttribute('data-original-index'));
            } else {
                originalIndex = index - CLONES_COUNT;
            }
            
            const angle = originalIndex * angleStep;
            card.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;
        });
    }
    
    // Función para animar el hover de los iconos
    function animateIconHover(icon, scale = 1.1) {
        if (icon) {
            icon.style.transform = `scale(${scale})`;
        }
    }
    
    // Función para la animación flotante
    function startFloatingAnimation(element) {
        if (element) {
            element.style.animation = 'float 3s ease-in-out infinite';
        }
    }
    
    function stopFloatingAnimation(element) {
        if (element) {
            element.style.animation = 'none';
        }
    }
    
    // Event listeners para navegación
    nextBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Right button clicked!');
        
        if (isAnimating) {
            showAnimationFeedback(this);
            return;
        }
        
        nextCard();
    });
    
    prevBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Left button clicked!');
        
        if (isAnimating) {
            showAnimationFeedback(this);
            return;
        }
        
        prevCard();
    });
    
    // Click en las cartas para navegar
    function setupCardClickListeners() {
        cards.forEach((card, index) => {
            // Remover listeners anteriores
            card.replaceWith(card.cloneNode(true));
        });
        
        // Obtener las cartas actualizadas y agregar listeners
        cards = Array.from(cardsContainer.querySelectorAll('.card'));
        
        cards.forEach((card, index) => {
            card.addEventListener('click', function(e) {
                if (isAnimating) {
                    console.log('Animation in progress, ignoring card click');
                    return;
                }
                
                if (index !== currentIndex) {
                    currentIndex = index;
                    updateCarousel();
                }
            });
            
            // Animaciones de hover para cada carta
            card.addEventListener('mouseenter', function() {
                if (isAnimating) return;
                
                const icon = card.querySelector('.icon');
                if (card.classList.contains('active')) {
                    animateIconHover(icon, 1.2);
                    startFloatingAnimation(icon);
                } else {
                    animateIconHover(icon, 1.05);
                }
            });
            
            card.addEventListener('mouseleave', function() {
                const icon = card.querySelector('.icon');
                animateIconHover(icon, 1);
                if (!card.classList.contains('active')) {
                    stopFloatingAnimation(icon);
                }
            });
        });
    }
    
    // Animación especial para la carta activa
    function updateActiveCardAnimation() {
        cards.forEach(card => {
            const icon = card.querySelector('.icon');
            if (card.classList.contains('active')) {
                startFloatingAnimation(icon);
            } else {
                stopFloatingAnimation(icon);
            }
        });
    }
    
    // Navegación con teclado con debounce
    let keyboardTimeout;
    document.addEventListener('keydown', function(e) {
        if (keyboardTimeout) return;
        
        let actionTaken = false;
        
        if (e.key === 'ArrowLeft') {
            actionTaken = prevCard();
        } else if (e.key === 'ArrowRight') {
            actionTaken = nextCard();
        }
        
        if (actionTaken) {
            keyboardTimeout = setTimeout(() => {
                keyboardTimeout = null;
            }, TRANSITION_DURATION);
        }
    });
    
    // Soporte para touch/swipe en dispositivos móviles
    let startX = 0;
    let startY = 0;
    let distX = 0;
    let distY = 0;
    let isSwipping = false;
    
    cardsContainer.addEventListener('touchstart', function(e) {
        if (isAnimating) return;
        
        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
        isSwipping = true;
    }, { passive: true });
    
    cardsContainer.addEventListener('touchmove', function(e) {
        if (isSwipping && !isAnimating) {
            e.preventDefault();
        }
    });
    
    cardsContainer.addEventListener('touchend', function(e) {
        if (!isSwipping || isAnimating) {
            isSwipping = false;
            return;
        }
        
        const touch = e.changedTouches[0];
        distX = touch.clientX - startX;
        distY = touch.clientY - startY;
        
        if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > 50) {
            if (distX > 0) {
                prevCard();
            } else {
                nextCard();
            }
        }
        
        isSwipping = false;
    });
    
    // Animaciones para los botones de navegación
    function animateButton(button, scale = 1.15) {
        if (!button.classList.contains('disabled')) {
            button.style.transform = `scale(${scale}) translateY(-50%)`;
        }
    }
    
    // Event listeners para animaciones de botones
    [prevBtn, nextBtn].forEach(button => {
        button.addEventListener('mouseenter', function() {
            if (!isAnimating && !this.classList.contains('disabled')) {
                animateButton(this, 1.15);
            }
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.classList.contains('disabled')) {
                animateButton(this, 1);
            }
        });
        
        button.addEventListener('mousedown', function() {
            if (!isAnimating && !this.classList.contains('disabled')) {
                animateButton(this, 1.05);
            }
        });
        
        button.addEventListener('mouseup', function() {
            if (!isAnimating && !this.classList.contains('disabled')) {
                animateButton(this, 1.15);
            }
        });
    });
    
    // Feedback visual para cuando se intenta navegar durante animación
    function showAnimationFeedback(button) {
        button.style.opacity = '0.5';
        setTimeout(() => {
            button.style.opacity = '1';
        }, 150);
    }
    
    // Inicializar el carrusel infinito
    createInfiniteCarousel();
    positionCards();
    setupCardClickListeners();
    updateCarousel(true); // Inicializar sin transición
    
    // Inicializar animación activa
    setTimeout(() => {
        updateActiveCardAnimation();
    }, 100);
});