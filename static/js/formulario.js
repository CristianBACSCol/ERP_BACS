// Variables globales para las firmas
// Versión: 2.2 - HEIC se intenta procesar en cliente primero, luego backend
console.log('✅ formulario.js v2.2 cargado - HEIC se procesa en cliente primero, luego backend');
let firmas = {};

// Verificar que heic2any esté disponible
(function() {
    function checkHeic2any() {
        if (typeof heic2any !== 'undefined') {
            console.log('✅ Biblioteca heic2any cargada correctamente');
            window.heic2anyAvailable = true;
            return true;
        } else {
            window.heic2anyAvailable = false;
            return false;
        }
    }
    
    // Verificar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            checkHeic2any();
            setTimeout(checkHeic2any, 500);
            setTimeout(checkHeic2any, 1000);
        });
    } else {
        checkHeic2any();
        setTimeout(checkHeic2any, 500);
        setTimeout(checkHeic2any, 1000);
    }
})();

// Inicializar canvas de firmas
document.addEventListener('DOMContentLoaded', function() {
    inicializarFirmas();
    inicializarPreviewsFotos();
    inicializarSeleccionMultiple();
});

function inicializarFirmas() {
    document.querySelectorAll('.firma-canvas').forEach(canvas => {
        const campoId = canvas.id.split('_')[1];
        const ctx = canvas.getContext('2d');
        
        // Configurar canvas
        ctx.strokeStyle = '#000';
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        
        // Escala entre tamaño visual (CSS) y resolución interna del canvas
        function getScale() {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            return { rect, scaleX, scaleY };
        }
        
        let isDrawing = false;
        
        // Eventos del mouse
        canvas.addEventListener('mousedown', function(e) {
            isDrawing = true;
            const { rect, scaleX, scaleY } = getScale();
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            ctx.beginPath();
            ctx.moveTo(x, y);
        });
        
        canvas.addEventListener('mousemove', function(e) {
            if (!isDrawing) return;
            const { rect, scaleX, scaleY } = getScale();
            const x = (e.clientX - rect.left) * scaleX;
            const y = (e.clientY - rect.top) * scaleY;
            ctx.lineTo(x, y);
            ctx.stroke();
        });
        
        canvas.addEventListener('mouseup', function() {
            isDrawing = false;
        });
        
        // Eventos táctiles para dispositivos móviles
        canvas.addEventListener('touchstart', function(e) {
            e.preventDefault();
            isDrawing = true;
            const { rect, scaleX, scaleY } = getScale();
            const touch = e.touches[0];
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            ctx.beginPath();
            ctx.moveTo(x, y);
        });
        
        canvas.addEventListener('touchmove', function(e) {
            e.preventDefault();
            if (!isDrawing) return;
            const { rect, scaleX, scaleY } = getScale();
            const touch = e.touches[0];
            const x = (touch.clientX - rect.left) * scaleX;
            const y = (touch.clientY - rect.top) * scaleY;
            ctx.lineTo(x, y);
            ctx.stroke();
        });
        
        canvas.addEventListener('touchend', function(e) {
            e.preventDefault();
            isDrawing = false;
        });
        
        firmas[campoId] = ctx;
    });
}

function limpiarFirma(campoId) {
    const canvas = document.getElementById(`canvas_${campoId}`);
    const ctx = firmas[campoId];
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    document.getElementById(`firma_${campoId}`).value = '';
}

function guardarFirma(campoId) {
    const canvas = document.getElementById(`canvas_${campoId}`);
    const firmaInput = document.getElementById(`firma_${campoId}`);
    
    console.log(`DEBUG: Guardando firma para campo ${campoId}`);
    
    const dataURL = canvas.toDataURL('image/png');
    firmaInput.value = dataURL;
    console.log(`DEBUG: Firma guardada exitosamente para campo ${campoId}`);
}

// Función para convertir HEIC a JPEG usando heic2any
async function convertirHEIC(file) {
    return new Promise(async (resolve, reject) => {
        const originalSize = (file.size / 1024 / 1024).toFixed(2);
        console.log(`DEBUG: 🔄 [v2.2] Iniciando conversión HEIC: ${file.name} (${originalSize} MB)`);
        
        // Esperar a que heic2any esté disponible
        let attempts = 0;
        const maxAttempts = 100; // 20 segundos máximo
        
        function waitForLibrary() {
            return new Promise((resolveWait, rejectWait) => {
                function check() {
                    attempts++;
                    // Verificar múltiples formas de acceso a heic2any
                    const heicAvailable = typeof heic2any !== 'undefined' || 
                                         typeof window.heic2any !== 'undefined' ||
                                         (window.heic2anyLoaded === true);
                    
                    if (heicAvailable) {
                        console.log(`DEBUG: [v2.2] ✅ heic2any disponible después de ${attempts} intentos`);
                        resolveWait();
                    } else if (attempts < maxAttempts) {
                        setTimeout(check, 200);
                    } else {
                        rejectWait(new Error('Biblioteca heic2any no disponible después de esperar 20 segundos'));
                    }
                }
                check();
            });
        }
        
        try {
            await waitForLibrary();
            
            // Usar heic2any global o window.heic2any
            const heicConverter = typeof heic2any !== 'undefined' ? heic2any : 
                                 typeof window.heic2any !== 'undefined' ? window.heic2any : null;
            
            if (!heicConverter || typeof heicConverter !== 'function') {
                throw new Error('heic2any no está disponible o no es una función válida');
            }
            
            console.log(`DEBUG: [v2.2] 🔄 Ejecutando conversión con heic2any...`);
            
            // Ejecutar conversión con timeout
            const conversionPromise = heicConverter({
                blob: file,
                toType: 'image/jpeg',
                quality: 0.92
            });
            
            // Agregar timeout de 30 segundos
            const timeoutPromise = new Promise((_, rejectTimeout) => {
                setTimeout(() => rejectTimeout(new Error('Timeout: La conversión HEIC tardó más de 30 segundos')), 30000);
            });
            
            const conversionResult = await Promise.race([conversionPromise, timeoutPromise]);
            
            // heic2any puede devolver un array o un blob directamente
            const blob = Array.isArray(conversionResult) ? conversionResult[0] : conversionResult;
            
            if (!blob || !(blob instanceof Blob)) {
                throw new Error('La conversión HEIC no devolvió un blob válido');
            }
            
            // Verificar que el blob tenga contenido
            if (blob.size === 0) {
                throw new Error('El blob convertido está vacío');
            }
            
            // Crear un nuevo File desde el blob convertido
            const convertedFile = new File([blob], file.name.replace(/\.(heic|heif)$/i, '.jpg'), {
                type: 'image/jpeg',
                lastModified: Date.now()
            });
            
            const convertedSize = (convertedFile.size / 1024 / 1024).toFixed(2);
            console.log(`DEBUG: [v2.2] ✅ HEIC convertido exitosamente - Original: ${originalSize} MB, Convertido: ${convertedSize} MB`);
            
            resolve(convertedFile);
        } catch (error) {
            console.error('❌ [v2.2] Error en convertirHEIC:', error);
            console.error('❌ [v2.2] Stack:', error.stack);
            reject(new Error('Error al convertir HEIC: ' + (error.message || 'Error desconocido')));
        }
    });
}

// Verificar que heic2any esté disponible al cargar el script
(function() {
    function checkHeic2any() {
        if (typeof heic2any !== 'undefined') {
            console.log('✅ Biblioteca heic2any cargada correctamente');
            window.heic2anyAvailable = true;
        } else {
            window.heic2anyAvailable = false;
            console.warn('⚠️ heic2any no disponible aún, se verificará cuando sea necesario');
        }
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkHeic2any);
    } else {
        checkHeic2any();
    }
    
    // Verificar periódicamente
    setTimeout(checkHeic2any, 500);
    setTimeout(checkHeic2any, 1000);
})();

async function optimizarImagen(file) {
    return new Promise((resolve, reject) => {
        // IMPORTANTE: No intentar cargar HEIC directamente en Image
        // Si el archivo es HEIC, debe convertirse ANTES de llegar aquí
        if (file.name.toLowerCase().endsWith('.heic') || 
            file.name.toLowerCase().endsWith('.heif') ||
            file.type === 'image/heic' ||
            file.type === 'image/heif') {
            console.error('❌ ERROR CRÍTICO: Se intentó optimizar un HEIC sin convertir primero.');
            reject(new Error('ERROR CRÍTICO: Se intentó optimizar un HEIC sin convertir primero. El archivo debe convertirse a JPEG antes de optimizar.'));
            return;
        }
        
        // Verificar que el tipo MIME sea compatible con Image
        const compatibleTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/bmp'];
        if (file.type && !compatibleTypes.includes(file.type.toLowerCase())) {
            console.warn(`⚠️ ADVERTENCIA: Tipo MIME ${file.type} puede no ser compatible. Se intentará procesar.`);
        }
        
        const reader = new FileReader();
        reader.onload = function(e) {
            // Verificar que el data URL sea válido antes de intentar cargarlo
            const dataUrl = e.target.result;
            if (!dataUrl || !dataUrl.startsWith('data:image/')) {
                reject(new Error('Error: El archivo no es una imagen válida o no se pudo leer correctamente.'));
                return;
            }
            
            const img = new Image();
            
            // Configurar timeout para evitar esperas infinitas
            const timeout = setTimeout(() => {
                reject(new Error('Timeout: La imagen tardó demasiado en cargar. Puede ser un formato no soportado.'));
            }, 10000); // 10 segundos
            
            img.onload = function() {
                clearTimeout(timeout);
                const MAX_FILE_SIZE = 0.5 * 1024 * 1024; // 0.5MB máximo
                const MAX_DIMENSION_INITIAL = 2000;
                const MAX_DIMENSION_AGGRESSIVE = 1200;
                
                let width = img.width;
                let height = img.height;
                const originalSize = file.size;
                
                console.log(`DEBUG: Iniciando optimización - Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB, Dimensiones: ${width}x${height}`);
                
                // Redimensionar primero si es necesario
                if (width > MAX_DIMENSION_INITIAL || height > MAX_DIMENSION_INITIAL) {
                    if (width > height) {
                        width = MAX_DIMENSION_INITIAL;
                        height = Math.round(img.height * (MAX_DIMENSION_INITIAL / img.width));
                    } else {
                        height = MAX_DIMENSION_INITIAL;
                        width = Math.round(img.width * (MAX_DIMENSION_INITIAL / img.height));
                    }
                    console.log(`DEBUG: Redimensionado inicial a ${width}x${height}`);
                }
                
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // Función para intentar comprimir con una calidad específica
                function tryCompressWithQuality(quality, dimension = null) {
                    return new Promise((resolveCompress, rejectCompress) => {
                        // Si se especifica una dimensión, redimensionar primero
                        if (dimension) {
                            let newWidth = width;
                            let newHeight = height;
                            if (width > dimension || height > dimension) {
                                if (width > height) {
                                    newWidth = dimension;
                                    newHeight = Math.round(height * (dimension / width));
                                } else {
                                    newHeight = dimension;
                                    newWidth = Math.round(width * (dimension / height));
                                }
                                canvas.width = newWidth;
                                canvas.height = newHeight;
                                const ctx2 = canvas.getContext('2d');
                                ctx2.drawImage(img, 0, 0, newWidth, newHeight);
                                console.log(`DEBUG: Redimensionado agresivo a ${newWidth}x${newHeight}`);
                            }
                        }
                        
                        canvas.toBlob(function(compressedBlob) {
                            if (!compressedBlob) {
                                rejectCompress(new Error('Error al comprimir imagen'));
                                return;
                            }
                            
                            const size = compressedBlob.size;
                            resolveCompress({ blob: compressedBlob, size: size, quality: quality });
                        }, 'image/jpeg', quality);
                    });
                }
                
                // Intentar diferentes niveles de calidad y dimensiones
                async function optimize() {
                    const qualityLevels = [0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20];
                    
                    // Primera pasada: probar con dimensiones iniciales
                    for (const quality of qualityLevels) {
                        const result = await tryCompressWithQuality(quality);
                        console.log(`DEBUG: Calidad ${(quality * 100).toFixed(0)}% - Tamaño: ${(result.size / 1024).toFixed(2)} KB`);
                        
                        if (result.size <= MAX_FILE_SIZE) {
                            const optimizedFile = new File([result.blob], file.name.replace(/\.[^/.]+$/, '.jpg'), {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            });
                            
                            const reduction = ((originalSize - result.size) / originalSize * 100).toFixed(1);
                            console.log(`DEBUG: ✅ Imagen optimizada - Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB, Optimizado: ${(result.size / 1024).toFixed(2)} KB (${(result.size / 1024 / 1024).toFixed(2)} MB), Reducción: ${reduction}%, Calidad: ${(quality * 100).toFixed(0)}%`);
                            
                            resolve(optimizedFile);
                            return;
                        }
                    }
                    
                    // Segunda pasada: redimensionar más agresivamente y probar de nuevo
                    console.log(`DEBUG: Archivo aún muy grande, redimensionando más agresivamente a ${MAX_DIMENSION_AGGRESSIVE}px...`);
                    for (const quality of [0.50, 0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15]) {
                        const result = await tryCompressWithQuality(quality, MAX_DIMENSION_AGGRESSIVE);
                        console.log(`DEBUG: Calidad ${(quality * 100).toFixed(0)}% (agresivo) - Tamaño: ${(result.size / 1024).toFixed(2)} KB`);
                        
                        if (result.size <= MAX_FILE_SIZE) {
                            const optimizedFile = new File([result.blob], file.name.replace(/\.[^/.]+$/, '.jpg'), {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            });
                            
                            const reduction = ((originalSize - result.size) / originalSize * 100).toFixed(1);
                            console.log(`DEBUG: ✅ Imagen optimizada (agresivo) - Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB, Optimizado: ${(result.size / 1024).toFixed(2)} KB (${(result.size / 1024 / 1024).toFixed(2)} MB), Reducción: ${reduction}%, Calidad: ${(quality * 100).toFixed(0)}%`);
                            
                            resolve(optimizedFile);
                            return;
                        }
                    }
                    
                    // Último recurso: usar la mejor calidad que encontramos (aunque sea > 0.5MB)
                    const lastResult = await tryCompressWithQuality(0.15, MAX_DIMENSION_AGGRESSIVE);
                    const optimizedFile = new File([lastResult.blob], file.name.replace(/\.[^/.]+$/, '.jpg'), {
                        type: 'image/jpeg',
                        lastModified: Date.now()
                    });
                    
                    const reduction = ((originalSize - lastResult.size) / originalSize * 100).toFixed(1);
                    console.log(`DEBUG: ⚠️ Imagen optimizada (último recurso) - Original: ${(originalSize / 1024 / 1024).toFixed(2)} MB, Optimizado: ${(lastResult.size / 1024).toFixed(2)} KB (${(lastResult.size / 1024 / 1024).toFixed(2)} MB), Reducción: ${reduction}%`);
                    
                    resolve(optimizedFile);
                }
                
                optimize().catch(reject);
            };
            img.onerror = function(error) {
                clearTimeout(timeout);
                console.error('❌ Error al cargar imagen en Image object:', error);
                console.error('Tipo de archivo:', file.type);
                console.error('Nombre de archivo:', file.name);
                
                // Si es HEIC, dar mensaje más específico
                if (file.name.toLowerCase().endsWith('.heic') || file.name.toLowerCase().endsWith('.heif')) {
                    reject(new Error('Error: No se puede cargar imagen HEIC directamente. El archivo debe convertirse a JPEG primero. El backend lo procesará automáticamente.'));
                } else {
                    reject(new Error('Error al cargar imagen. El formato puede no ser compatible. El backend lo procesará automáticamente.'));
                }
            };
            
            // Intentar cargar la imagen
            try {
                img.src = dataUrl;
            } catch (error) {
                clearTimeout(timeout);
                console.error('❌ Error al asignar src a Image:', error);
                reject(new Error('Error al procesar imagen: ' + (error.message || 'Error desconocido')));
            }
        };
        reader.onerror = function() {
            reject(new Error('Error al leer archivo'));
        };
        reader.readAsDataURL(file);
    });
}

function inicializarPreviewsFotos() {
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', async function(e) {
            const campoId = this.id.split('_')[1];
            const files = Array.from(e.target.files);
            const esDeCamara = this.hasAttribute('capture');
            
            if (files.length > 0) {
                if (!window.fotosPorCampo) {
                    window.fotosPorCampo = {};
                }
                if (!window.fotosPorCampo[campoId]) {
                    window.fotosPorCampo[campoId] = [];
                }
                
                const preview = document.getElementById(`preview_${campoId}`);
                let loadingMsg = null;
                if (preview) {
                    loadingMsg = document.createElement('div');
                    loadingMsg.className = 'alert alert-info';
                    loadingMsg.textContent = 'Procesando imágenes...';
                    preview.appendChild(loadingMsg);
                }
                
                // Función para actualizar el mensaje de carga
                const updateLoadingMsg = (text) => {
                    if (loadingMsg) {
                        loadingMsg.textContent = text;
                    }
                };
                
                try {
                    const optimizedFiles = [];
                    
                    for (const file of files) {
                        // DETECTAR HEIC PRIMERO - enviar directamente al backend
                        const isHeic = file.name.toLowerCase().endsWith('.heic') || 
                                     file.name.toLowerCase().endsWith('.heif') ||
                                     file.type === 'image/heic' ||
                                     file.type === 'image/heif';
                        
                        if (isHeic) {
                            console.log(`DEBUG: 🔍 [v2.2] Archivo HEIC detectado: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`);
                            updateLoadingMsg(`Convirtiendo HEIC a JPEG: ${file.name}...`);
                            
                            // INTENTAR convertir en cliente PRIMERO - SI O SI
                            let conversionSuccess = false;
                            let convertedFile = null;
                            
                            try {
                                // Esperar a que heic2any esté disponible con más tiempo
                                let heicConverter = null;
                                let attempts = 0;
                                const maxAttempts = 100; // 20 segundos
                                
                                console.log('DEBUG: [v2.2] Esperando a que heic2any esté disponible...');
                                while (attempts < maxAttempts && !heicConverter) {
                                    if (typeof heic2any !== 'undefined') {
                                        heicConverter = heic2any;
                                        console.log(`DEBUG: [v2.2] ✅ heic2any disponible después de ${attempts} intentos`);
                                        break;
                                    }
                                    await new Promise(resolve => setTimeout(resolve, 200));
                                    attempts++;
                                }
                                
                                if (heicConverter) {
                                    console.log('DEBUG: [v2.2] 🔄 Iniciando conversión HEIC en cliente...');
                                    convertedFile = await convertirHEIC(file);
                                    
                                    if (convertedFile && convertedFile.type === 'image/jpeg') {
                                        const convertedSize = (convertedFile.size / 1024 / 1024).toFixed(2);
                                        console.log(`DEBUG: [v2.2] ✅ HEIC convertido exitosamente en cliente - ${convertedSize} MB`);
                                        updateLoadingMsg(`Optimizando imagen convertida (${convertedSize} MB)...`);
                                        conversionSuccess = true;
                                        
                                        // Optimizar la imagen convertida
                                        try {
                                            const optimizedFile = await optimizarImagen(convertedFile);
                                            const finalSize = (optimizedFile.size / 1024 / 1024).toFixed(2);
                                            console.log(`DEBUG: [v2.2] ✅ HEIC procesado completamente - Tamaño final: ${finalSize} MB`);
                                            optimizedFiles.push(optimizedFile);
                                            continue; // Archivo procesado exitosamente
                                        } catch (optError) {
                                            console.warn('DEBUG: [v2.2] ⚠️ Error optimizando imagen convertida, usando versión convertida sin optimizar');
                                            optimizedFiles.push(convertedFile);
                                            continue;
                                        }
                                    } else {
                                        console.warn('DEBUG: [v2.2] ⚠️ Conversión no produjo un JPEG válido');
                                    }
                                } else {
                                    console.warn('DEBUG: [v2.2] ⚠️ heic2any no disponible después de 20 segundos');
                                }
                            } catch (conversionError) {
                                console.error('DEBUG: [v2.2] ❌ Error convirtiendo HEIC en cliente:', conversionError);
                                console.error('DEBUG: [v2.2] Stack trace:', conversionError.stack);
                            }
                            
                            // Si la conversión falló, enviar al backend
                            if (!conversionSuccess) {
                                console.log('DEBUG: [v2.2] ⚠️ Conversión en cliente falló, el backend procesará el archivo HEIC');
                                updateLoadingMsg(`El backend procesará el archivo HEIC: ${file.name}...`);
                                optimizedFiles.push(file);
                                continue;
                            }
                        }
                        
                        // Solo procesar imágenes que NO sean HEIC
                        const isImage = file.type.startsWith('image/');
                        
                        if (isImage) {
                            try {
                                // HEIC ya fue manejado arriba - este bloque solo procesa imágenes normales
                                updateLoadingMsg(`Optimizando: ${file.name}...`);
                                
                                // Optimizar la imagen (solo formatos compatibles con navegador)
                                console.log(`DEBUG: 🔄 Optimizando imagen: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB), Tipo: ${file.type}`);
                                const optimizedFile = await optimizarImagen(file);
                                const finalSize = (optimizedFile.size / 1024 / 1024).toFixed(2);
                                console.log(`DEBUG: ✅ Imagen optimizada: ${optimizedFile.name} - Tamaño final: ${finalSize} MB`);
                                
                                // Verificar que el archivo optimizado sea menor a 0.5MB
                                if (optimizedFile.size > 0.5 * 1024 * 1024) {
                                    console.warn(`⚠️ ADVERTENCIA: Archivo optimizado aún es grande: ${finalSize} MB`);
                                }
                                
                                optimizedFiles.push(optimizedFile);
                            } catch (error) {
                                console.error('❌ Error procesando imagen:', error);
                                console.error('Detalles del error:', error.message);
                                
                                // Si falla la optimización en cliente, usar el archivo original y dejar que el backend lo procese
                                console.log('DEBUG: Fallo en optimización cliente, el backend procesará el archivo automáticamente');
                                optimizedFiles.push(file);
                            }
                        } else {
                            optimizedFiles.push(file);
                        }
                    }
                    
                    if (preview) {
                        const loadingMsg = preview.querySelector('.alert-info');
                        if (loadingMsg) loadingMsg.remove();
                    }
                    
                    if (esDeCamara) {
                        const nuevaFoto = optimizedFiles[optimizedFiles.length - 1];
                        window.fotosPorCampo[campoId].push(nuevaFoto);
                    } else {
                        optimizedFiles.forEach(file => {
                            const existe = window.fotosPorCampo[campoId].some(foto => 
                                foto.name === file.name && foto.size === file.size
                            );
                            if (!existe) {
                                window.fotosPorCampo[campoId].push(file);
                            }
                        });
                    }
                    
                    mostrarPreviewsFotos(campoId, window.fotosPorCampo[campoId]);
                    actualizarInputFotos(campoId, window.fotosPorCampo[campoId]);
                    
                    if (esDeCamara) {
                        this.removeAttribute('capture');
                    }
                } catch (error) {
                    console.error('Error procesando imágenes:', error);
                    alert('Error al procesar las imágenes. Por favor, intenta de nuevo.');
                }
            }
        });
    });
}

function mostrarPreviewsFotos(campoId, files) {
    const preview = document.getElementById(`preview_${campoId}`);
    const grid = document.getElementById(`grid_${campoId}`);
    
    grid.innerHTML = '';
    
    const contador = document.createElement('div');
    contador.className = 'foto-counter';
    contador.style.cssText = `
        grid-column: 1 / -1;
        padding: 10px;
        background: #e9ecef;
        border-radius: 4px;
        text-align: center;
        font-weight: bold;
        color: #495057;
        margin-bottom: 10px;
    `;
    contador.textContent = `${files.length} foto${files.length !== 1 ? 's' : ''} seleccionada${files.length !== 1 ? 's' : ''}`;
    grid.appendChild(contador);
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const fotoItem = document.createElement('div');
            fotoItem.className = 'foto-item';
            fotoItem.innerHTML = `
                <img src="${e.target.result}" alt="Vista previa ${index + 1}">
                <div class="foto-info">
                    <small>${file.name}</small>
                    <small>${(file.size / 1024 / 1024).toFixed(2)} MB</small>
                </div>
                <button type="button" class="foto-remove" onclick="eliminarFoto(${campoId}, ${index})">×</button>
            `;
            grid.appendChild(fotoItem);
        };
        reader.readAsDataURL(file);
    });
    
    preview.style.display = 'block';
}

function abrirCamara(campoId) {
    const input = document.getElementById(`campo_${campoId}`);
    input.setAttribute('capture', 'environment');
    input.click();
}

function actualizarInputFotos(campoId, files) {
    const input = document.getElementById(`campo_${campoId}`);
    const dt = new DataTransfer();
    files.forEach(file => dt.items.add(file));
    input.files = dt.files;
    
    console.log(`DEBUG: Input ${campoId} ahora tiene ${input.files.length} archivos`);
    for (let i = 0; i < input.files.length; i++) {
        console.log(`  - Archivo ${i+1}: ${input.files[i].name} (${input.files[i].size} bytes)`);
    }
}

function limpiarFotos(campoId) {
    const input = document.getElementById(`campo_${campoId}`);
    const preview = document.getElementById(`preview_${campoId}`);
    const grid = document.getElementById(`grid_${campoId}`);
    
    if (window.fotosPorCampo && window.fotosPorCampo[campoId]) {
        window.fotosPorCampo[campoId] = [];
    }
    
    input.value = '';
    grid.innerHTML = '';
    preview.style.display = 'none';
}

function eliminarFoto(campoId, index) {
    if (window.fotosPorCampo && window.fotosPorCampo[campoId]) {
        window.fotosPorCampo[campoId].splice(index, 1);
        actualizarInputFotos(campoId, window.fotosPorCampo[campoId]);
        if (window.fotosPorCampo[campoId].length > 0) {
            mostrarPreviewsFotos(campoId, window.fotosPorCampo[campoId]);
        } else {
            limpiarFotos(campoId);
        }
    }
}

function inicializarSeleccionMultiple() {
    document.querySelectorAll('.menu-select').forEach(select => {
        select.addEventListener('change', function() {
            const menuIndex = this.dataset.menu;
            const submenuContainer = document.querySelector(`.submenu-campos[data-menu="${menuIndex}"]`);
            const selectedOption = this.options[this.selectedIndex];
            
            submenuContainer.innerHTML = '';
            
            if (selectedOption.value) {
                const tipoCampo = selectedOption.dataset.tipo;
                const titulo = selectedOption.value;
                let campoHTML = '';
                const campoId = `submenu_${menuIndex}_${Date.now()}`;
                
                if (tipoCampo === 'texto') {
                    campoHTML = `
                        <div class="form-group">
                            <label for="${campoId}" class="form-label">${titulo}</label>
                            <input type="text" id="${campoId}" name="submenu_${menuIndex}_${titulo}" class="form-control">
                        </div>
                    `;
                } else if (tipoCampo === 'fecha') {
                    campoHTML = `
                        <div class="form-group">
                            <label for="${campoId}" class="form-label">${titulo}</label>
                            <input type="date" id="${campoId}" name="submenu_${menuIndex}_${titulo}" class="form-control">
                        </div>
                    `;
                } else {
                    campoHTML = `
                        <div class="form-group">
                            <label for="${campoId}" class="form-label">${titulo}</label>
                            <input type="text" id="${campoId}" name="submenu_${menuIndex}_${titulo}" class="form-control">
                        </div>
                    `;
                }
                
                submenuContainer.innerHTML = campoHTML;
            }
        });
    });
}

// Funciones de validación de formato
function validarFormato(valor, tipoValidacion) {
    if (!valor || !tipoValidacion) return { valido: true };
    
    valor = valor.trim();
    
    switch(tipoValidacion) {
        case 'cedula':
            // Cédula: solo números, 7-11 dígitos
            const regexCedula = /^\d{7,11}$/;
            return {
                valido: regexCedula.test(valor),
                mensaje: 'La cédula debe contener solo números (7-11 dígitos)'
            };
        
        case 'telefono':
            // Teléfono: números, espacios, +, -, paréntesis (7-15 dígitos numéricos)
            const telefonoLimpio = valor.replace(/[\s\+\-\(\)]/g, '');
            const regexTelefono = /^[\d\s\+\-\(\)]+$/;
            const tieneDigitos = /^\d{7,15}$/.test(telefonoLimpio);
            return {
                valido: regexTelefono.test(valor) && tieneDigitos,
                mensaje: 'El teléfono debe contener solo números, espacios, +, - y paréntesis (7-15 dígitos)'
            };
        
        case 'solo_numeros':
            // Solo números (sin espacios ni otros caracteres)
            const regexSoloNumeros = /^\d+$/;
            return {
                valido: regexSoloNumeros.test(valor),
                mensaje: 'Este campo solo acepta números'
            };
        
        case 'email':
            // Email: formato estándar
            const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return {
                valido: regexEmail.test(valor),
                mensaje: 'Por favor ingresa un correo electrónico válido'
            };
        
        case 'numero':
            // Solo números
            const regexNumero = /^\d+$/;
            return {
                valido: regexNumero.test(valor),
                mensaje: 'Este campo solo acepta números'
            };
        
        case 'alfanumerico':
            // Alfanumérico: letras, números y espacios
            const regexAlfanumerico = /^[a-zA-Z0-9\s]+$/;
            return {
                valido: regexAlfanumerico.test(valor),
                mensaje: 'Este campo solo acepta letras, números y espacios'
            };
        
        default:
            return { valido: true };
    }
}

// Agregar validación en tiempo real a los campos
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.campo-validado').forEach(campo => {
        const tipoValidacion = campo.dataset.tipoValidacion;
        if (tipoValidacion) {
            const mensajeElement = document.getElementById(`mensaje_validacion_${campo.id.replace('campo_', '')}`);
            
            campo.addEventListener('blur', function() {
                const valor = this.value.trim();
                if (valor) {
                    const resultado = validarFormato(valor, tipoValidacion);
                    if (!resultado.valido) {
                        this.classList.add('is-invalid');
                        if (mensajeElement) {
                            mensajeElement.textContent = resultado.mensaje;
                            mensajeElement.style.display = 'block';
                        }
                    } else {
                        this.classList.remove('is-invalid');
                        this.classList.add('is-valid');
                        if (mensajeElement) {
                            mensajeElement.style.display = 'none';
                        }
                    }
                } else {
                    this.classList.remove('is-invalid', 'is-valid');
                    if (mensajeElement) {
                        mensajeElement.style.display = 'none';
                    }
                }
            });
            
            campo.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    const valor = this.value.trim();
                    if (valor) {
                        const resultado = validarFormato(valor, tipoValidacion);
                        if (resultado.valido) {
                            this.classList.remove('is-invalid');
                            this.classList.add('is-valid');
                            if (mensajeElement) {
                                mensajeElement.style.display = 'none';
                            }
                        }
                    }
                }
            });
        }
    });
});

const formulario = document.getElementById('formularioDiligenciar');
if (formulario) {
    formulario.addEventListener('submit', function(e) {
        // Validar formato de campos con validación
        let erroresValidacion = [];
        document.querySelectorAll('.campo-validado').forEach(campo => {
            const tipoValidacion = campo.dataset.tipoValidacion;
            if (tipoValidacion) {
                const valor = campo.value.trim();
                if (valor || campo.hasAttribute('required')) {
                    const resultado = validarFormato(valor, tipoValidacion);
                    if (!resultado.valido) {
                        erroresValidacion.push({
                            campo: campo.previousElementSibling?.textContent.replace(' *', '') || 'Campo',
                            mensaje: resultado.mensaje
                        });
                        campo.classList.add('is-invalid');
                        const campoId = campo.id.replace('campo_', '');
                        const mensajeElement = document.getElementById(`mensaje_validacion_${campoId}`);
                        if (mensajeElement) {
                            mensajeElement.textContent = resultado.mensaje;
                            mensajeElement.style.display = 'block';
                        }
                    }
                }
            }
        });
        
        if (erroresValidacion.length > 0) {
            e.preventDefault();
            const mensaje = 'Por favor corrige los siguientes errores de formato:\n\n' +
                          erroresValidacion.map(e => `- ${e.campo}: ${e.mensaje}`).join('\n');
            alert(mensaje);
            // Scroll al primer error
            const primerError = document.querySelector('.is-invalid');
            if (primerError) {
                primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                primerError.focus();
            }
            return false;
        }
        
        // Validar campos obligatorios
        const camposObligatorios = document.querySelectorAll('[required]');
        let camposFaltantes = [];
        
        camposObligatorios.forEach(campo => {
            if (!campo.value.trim()) {
                camposFaltantes.push(campo.previousElementSibling.textContent.replace(' *', ''));
            }
        });
        
        if (camposFaltantes.length > 0) {
            e.preventDefault();
            alert('Por favor completa los siguientes campos obligatorios:\n' + camposFaltantes.join('\n'));
            return false;
        }
        
        // Validar que todos los archivos de imagen estén optimizados y sean menores a 0.5MB
        // NOTA: Los archivos HEIC se permiten porque el backend los procesará automáticamente
        const MAX_FILE_SIZE = 0.5 * 1024 * 1024; // 0.5MB
        let archivosGrandes = [];
        let archivosHEIC = [];
        
        document.querySelectorAll('input[type="file"]').forEach(input => {
            if (input.files && input.files.length > 0) {
                for (let i = 0; i < input.files.length; i++) {
                    const file = input.files[i];
                    
                    // Detectar HEIC (se permiten porque el backend los procesará)
                    const isHeic = file.name.toLowerCase().endsWith('.heic') || 
                                  file.name.toLowerCase().endsWith('.heif') ||
                                  file.type === 'image/heic' ||
                                  file.type === 'image/heif';
                    
                    if (isHeic) {
                        archivosHEIC.push(file.name);
                        console.log(`DEBUG: [v2.1] Archivo HEIC permitido para envío: ${file.name} - El backend lo procesará`);
                        // NO bloquear HEIC - el backend los procesará
                        continue;
                    }
                    
                    // Verificar tamaño solo para archivos NO-HEIC
                    if (file.size > MAX_FILE_SIZE) {
                        archivosGrandes.push({
                            nombre: file.name,
                            tamaño: (file.size / 1024 / 1024).toFixed(2) + ' MB'
                        });
                    }
                }
            }
        });
        
        // NO bloquear HEIC - el backend los procesará automáticamente
        if (archivosHEIC.length > 0) {
            console.log(`DEBUG: [v2.1] Se enviarán ${archivosHEIC.length} archivo(s) HEIC al backend para procesamiento automático`);
        }
        
        if (archivosGrandes.length > 0) {
            e.preventDefault();
            const mensaje = '❌ ERROR: Los siguientes archivos son demasiado grandes (máximo 0.5MB):\n' + 
                          archivosGrandes.map(a => `- ${a.nombre}: ${a.tamaño}`).join('\n') +
                          '\n\nPor favor, espera a que se completen la optimización antes de enviar.';
            alert(mensaje);
            console.error('Archivos grandes detectados:', archivosGrandes);
            return false;
        }
        
        console.log('✅ Validación de archivos completada - Archivos HEIC serán procesados por el backend');
        
        const firmasObligatorias = document.querySelectorAll('.firma-canvas');
        for (let canvas of firmasObligatorias) {
            const campoId = canvas.id.split('_')[1];
            const campoElement = document.querySelector(`[data-campo-id="${campoId}"]`);
            const esObligatorio = campoElement.querySelector('.form-label').textContent.includes('*');
            
            if (esObligatorio) {
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const pixels = imageData.data;
                
                let tieneContenido = false;
                for (let i = 0; i < pixels.length; i += 4) {
                    const r = pixels[i];
                    const g = pixels[i + 1];
                    const b = pixels[i + 2];
                    if (r !== 255 || g !== 255 || b !== 255) {
                        tieneContenido = true;
                        break;
                    }
                }
                
                if (!tieneContenido) {
                    e.preventDefault();
                    alert('Por favor completa todas las firmas obligatorias');
                    return false;
                }
            }
        }
        
        console.log('DEBUG: Procesando todas las firmas antes del envío...');
        
        document.querySelectorAll('canvas[id^="canvas_"]').forEach(function(canvas) {
            const campoId = canvas.id.replace('canvas_', '');
            const firmaInput = document.getElementById(`firma_${campoId}`);
            
            if (firmaInput) {
                console.log(`DEBUG: Procesando firma automática para campo ${campoId}`);
                try {
                    const dataURL = canvas.toDataURL('image/png');
                    firmaInput.value = dataURL;
                    console.log(`DEBUG: Firma automática guardada para campo ${campoId} - Tamaño: ${dataURL.length} caracteres`);
                } catch (error) {
                    console.error(`ERROR procesando firma para campo ${campoId}:`, error);
                }
            } else {
                console.warn(`WARNING: No se encontró input hidden para firma del campo ${campoId}`);
            }
        });
        
        console.log('DEBUG: Todas las firmas procesadas, enviando formulario...');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.firma-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const campoId = this.getAttribute('data-campo');
            
            if (action === 'limpiar') {
                limpiarFirma(campoId);
            }
        });
    });
    
    document.querySelectorAll('.foto-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const campoId = this.getAttribute('data-campo');
            
            if (action === 'abrir-camara') {
                abrirCamara(campoId);
            } else if (action === 'limpiar-fotos') {
                limpiarFotos(campoId);
            }
        });
    });
});

