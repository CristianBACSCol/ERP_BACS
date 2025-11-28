// Cargar heic2any de forma síncrona para asegurar que esté disponible
(function() {
    function loadHeic2any() {
        // Verificar si ya está cargado
        if (typeof heic2any !== 'undefined') {
            console.log('✅ heic2any ya está disponible');
            window.heic2any = heic2any;
            return;
        }
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/heic2any@0.0.4/dist/heic2any.min.js';
        script.async = false; // Cargar de forma síncrona
        script.onload = function() {
            console.log('✅ heic2any cargado desde CDN jsdelivr');
            if (typeof heic2any !== 'undefined') {
                window.heic2any = heic2any;
                window.heic2anyLoaded = true;
            }
        };
        script.onerror = function() {
            console.warn('⚠️ Error cargando heic2any desde jsdelivr, intentando fallback...');
            // Intentar cargar desde otro CDN como fallback
            const fallbackScript = document.createElement('script');
            fallbackScript.src = 'https://unpkg.com/heic2any@0.0.4/dist/heic2any.min.js';
            fallbackScript.async = false;
            fallbackScript.onload = function() {
                console.log('✅ heic2any cargado desde fallback CDN (unpkg)');
                if (typeof heic2any !== 'undefined') {
                    window.heic2any = heic2any;
                    window.heic2anyLoaded = true;
                }
            };
            fallbackScript.onerror = function() {
                console.error('❌ Error cargando heic2any desde todos los CDN');
                window.heic2anyLoaded = false;
            };
            document.head.appendChild(fallbackScript);
        };
        document.head.appendChild(script);
    }
    
    // Cargar inmediatamente
    loadHeic2any();
    
    // También verificar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadHeic2any);
    }
})();

