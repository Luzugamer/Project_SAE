export function mostrarCamposCondicionales(valorTipo) {
    const campoPais = document.getElementById('campo-pais');
    const campoCarrera = document.getElementById('campo-carrera');
    const campoCurso = document.getElementById('campo-curso');
    const campoNivel = document.getElementById('campo-nivel');
    const campoNombre = document.getElementById('campo-nombre');
    const inputPais = document.querySelector('[name="pais"]');
    const inputCarrera = document.querySelector('[name="carrera"]');
    const inputCurso = document.querySelector('[name="curso"]');
    const inputNivel = document.querySelector('[name="nivel"]');
    
    // Ocultamos todo primero
    if (campoPais) campoPais.style.display = 'none';
    if (campoCarrera) campoCarrera.style.display = 'none';
    if (campoCurso) campoCurso.style.display = 'none';
    if (campoNivel) campoNivel.style.display = 'none';
    if (campoNombre) campoNombre.style.display = 'block'; // Siempre visible
    
    // Limpiamos valores para evitar conflictos en validación
    if (inputPais) inputPais.removeAttribute('required');
    if (inputCarrera) inputCarrera.removeAttribute('required');
    if (inputCurso) inputCurso.removeAttribute('required');
    if (inputNivel) inputNivel.removeAttribute('required');
    
    if (valorTipo === 'admision') {
        if (campoPais) campoPais.style.display = 'block';
        if (campoCarrera) campoCarrera.style.display = 'block';
        if (inputPais) inputPais.setAttribute('required', 'required');
        if (inputCarrera) inputCarrera.setAttribute('required', 'required');
        if (inputCurso) inputCurso.value = '';
        if (inputNivel) inputNivel.value = '';
        
        // Manejo mejorado del Bootstrap Select para el campo país
        if (inputPais && $(inputPais).hasClass('selectpicker')) {
            // Primero mostramos el campo, luego refrescamos
            setTimeout(() => {
                $(inputPais).selectpicker('val', ''); // Limpia la selección
                $(inputPais).selectpicker('refresh'); // Refresca el componente
                $(inputPais).selectpicker('render'); // Re-renderiza
                
                // Aseguramos que el dropdown esté correctamente inicializado
                if ($(inputPais).data('selectpicker')) {
                    $(inputPais).selectpicker('toggle');
                    $(inputPais).selectpicker('toggle'); // Doble toggle para forzar renderizado
                }
            }, 150); // Aumentamos el tiempo para asegurar que el DOM esté listo
        }
        
    } else if (valorTipo === 'ejercicios') {
        if (campoCurso) campoCurso.style.display = 'block';
        if (campoNivel) campoNivel.style.display = 'block';
        if (inputCurso) inputCurso.setAttribute('required', 'required');
        if (inputNivel) inputNivel.setAttribute('required', 'required');
        
        // Limpiamos campos no utilizados
        if (inputPais) inputPais.value = '';
        if (inputCarrera) inputCarrera.value = '';
        
        // Limpiamos y ocultamos correctamente el selectpicker del país
        if (inputPais && $(inputPais).hasClass('selectpicker')) {
            $(inputPais).selectpicker('val', '');
            $(inputPais).selectpicker('refresh');
            $(inputPais).selectpicker('render');
        }
        
    } else if (valorTipo === 'otro') {
        // Limpiamos todos los campos
        if (inputPais) inputPais.value = '';
        if (inputCarrera) inputCarrera.value = '';
        if (inputCurso) inputCurso.value = '';
        if (inputNivel) inputNivel.value = '';
        
        // Limpiamos el selectpicker del país
        if (inputPais && $(inputPais).hasClass('selectpicker')) {
            $(inputPais).selectpicker('val', '');
            $(inputPais).selectpicker('refresh');
            $(inputPais).selectpicker('render');
        }
    }
    
    actualizarLabelYPlaceholder(valorTipo);
}

export function actualizarLabelYPlaceholder(valorTipo) {
    const labelNombre = document.getElementById('label-nombre');
    const inputNombre = document.querySelector('[name="nombre"]');
    
    if (!labelNombre || !inputNombre) return;
    
    if (valorTipo === 'admision') {
        labelNombre.textContent = 'Nombre de universidad:';
        inputNombre.placeholder = 'Ej: Universidad Nacional de Ingeniería';
    } else {
        labelNombre.textContent = 'Nombre del repositorio:';
        inputNombre.placeholder = 'Ej: Estadística Descriptiva';
    }
}

// Función auxiliar para inicializar selectpickers cuando sea necesario
export function inicializarSelectpickers() {
    // Inicializa todos los selectpickers en la página
    $('.selectpicker').selectpicker('refresh');
}

// Función para manejar específicamente el campo país
export function manejarCampoPais(mostrar = true) {
    const inputPais = document.querySelector('[name="pais"]');
    
    if (!inputPais || !$(inputPais).hasClass('selectpicker')) return;
    
    if (mostrar) {
        // Aseguramos que el selectpicker esté correctamente configurado
        setTimeout(() => {
            if (!inputPais.value || inputPais.value === '') {
                $(inputPais).selectpicker('val', 'PE'); 
            }
            $(inputPais).selectpicker('refresh');
            $(inputPais).selectpicker('render');
            
            const opciones = $(inputPais).find('option');
            if (opciones.length > 1) { 
                $(inputPais).selectpicker('refresh');
            }
        }, 200);
    } else {
        $(inputPais).selectpicker('val', 'PE');
        $(inputPais).selectpicker('refresh');
    }
}