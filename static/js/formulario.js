// Variables globales para las firmas
let firmas = {};

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

async function optimizarImagen(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = new Image();
            img.onload = function() {
                const MAX_DIMENSION = 2000;
                const MAX_FILE_SIZE = 0.5 * 1024 * 1024;
                const QUALITY_START = 0.75;
                const QUALITY_MIN = 0.3;
                
                let width = img.width;
                let height = img.height;
                
                if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
                    if (width > height) {
                        width = MAX_DIMENSION;
                        height = Math.round(img.height * (MAX_DIMENSION / img.width));
                    } else {
                        height = MAX_DIMENSION;
                        width = Math.round(img.width * (MAX_DIMENSION / img.height));
                    }
                }
                
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                let quality = QUALITY_START;
                let attempts = 0;
                const maxAttempts = 10;
                
                function tryCompress() {
                    canvas.toBlob(function(compressedBlob) {
                        if (!compressedBlob) {
                            reject(new Error('Error al comprimir imagen'));
                            return;
                        }
                        
                        const size = compressedBlob.size;
                        console.log(`DEBUG: Intento ${attempts + 1} - Tamaño: ${(size / 1024).toFixed(2)} KB, Calidad: ${(quality * 100).toFixed(0)}%`);
                        
                        if (size <= MAX_FILE_SIZE || quality <= QUALITY_MIN || attempts >= maxAttempts) {
                            const optimizedFile = new File([compressedBlob], file.name.replace(/\.[^/.]+$/, '.jpg'), {
                                type: 'image/jpeg',
                                lastModified: Date.now()
                            });
                            
                            const reduction = ((file.size - size) / file.size * 100).toFixed(1);
                            console.log(`DEBUG: Imagen optimizada - Original: ${(file.size / 1024).toFixed(2)} KB, Optimizado: ${(size / 1024).toFixed(2)} KB, Reducción: ${reduction}%`);
                            
                            resolve(optimizedFile);
                        } else {
                            quality -= 0.05;
                            attempts++;
                            tryCompress();
                        }
                    }, 'image/jpeg', quality);
                }
                
                tryCompress();
            };
            img.onerror = function() {
                reject(new Error('Error al cargar imagen'));
            };
            img.src = e.target.result;
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
                if (preview) {
                    const loadingMsg = document.createElement('div');
                    loadingMsg.className = 'alert alert-info';
                    loadingMsg.textContent = 'Optimizando imágenes...';
                    preview.appendChild(loadingMsg);
                }
                
                try {
                    const optimizedFiles = [];
                    
                    for (const file of files) {
                        const isImage = file.type.startsWith('image/') || 
                                       file.name.toLowerCase().endsWith('.heic') ||
                                       file.name.toLowerCase().endsWith('.heif');
                        
                        if (isImage) {
                            try {
                                const optimizedFile = await optimizarImagen(file);
                                optimizedFiles.push(optimizedFile);
                            } catch (error) {
                                console.error('Error optimizando imagen:', error);
                                if (file.name.toLowerCase().endsWith('.heic') || 
                                    file.name.toLowerCase().endsWith('.heif')) {
                                    console.warn('HEIC no soportado directamente, se intentará procesar como imagen');
                                }
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

const formulario = document.getElementById('formularioDiligenciar');
if (formulario) {
    formulario.addEventListener('submit', function(e) {
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

