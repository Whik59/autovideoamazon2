// Comprehensive Fingerprint Injection Script
// This script overrides browser APIs to inject custom fingerprint data

(function() {
    'use strict';
    
    // Fingerprint data will be injected here by Python
    const FINGERPRINT_DATA = {fingerprint_data};
    
    console.log('Fingerprint injection starting with data:', FINGERPRINT_DATA);
    
    // Override Navigator properties
    if (FINGERPRINT_DATA.platform) {
        Object.defineProperty(navigator, 'platform', {
            get: () => FINGERPRINT_DATA.platform,
            configurable: false,
            enumerable: true
        });
    }
    
    if (FINGERPRINT_DATA.hardware_concurrency) {
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => FINGERPRINT_DATA.hardware_concurrency,
            configurable: false,
            enumerable: true
        });
    }
    
    if (FINGERPRINT_DATA.device_memory) {
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => FINGERPRINT_DATA.device_memory,
            configurable: false,
            enumerable: true
        });
    }
    
    if (FINGERPRINT_DATA.max_touch_points !== undefined) {
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => FINGERPRINT_DATA.max_touch_points,
            configurable: false,
            enumerable: true
        });
    }
    
    if (FINGERPRINT_DATA.language) {
        Object.defineProperty(navigator, 'language', {
            get: () => FINGERPRINT_DATA.language.split(',')[0],
            configurable: false,
            enumerable: true
        });
        
        Object.defineProperty(navigator, 'languages', {
            get: () => FINGERPRINT_DATA.language.split(',').map(l => l.split(';')[0].trim()),
            configurable: false,
            enumerable: true
        });
    }
    
    // Override Screen properties
    if (FINGERPRINT_DATA.screen_width && FINGERPRINT_DATA.screen_height) {
        Object.defineProperty(screen, 'width', {
            get: () => FINGERPRINT_DATA.screen_width,
            configurable: false,
            enumerable: true
        });
        
        Object.defineProperty(screen, 'height', {
            get: () => FINGERPRINT_DATA.screen_height,
            configurable: false,
            enumerable: true
        });
        
        Object.defineProperty(screen, 'availWidth', {
            get: () => FINGERPRINT_DATA.viewport_width || FINGERPRINT_DATA.screen_width,
            configurable: false,
            enumerable: true
        });
        
        Object.defineProperty(screen, 'availHeight', {
            get: () => FINGERPRINT_DATA.viewport_height || (FINGERPRINT_DATA.screen_height - 40),
            configurable: false,
            enumerable: true
        });
    }
    
    if (FINGERPRINT_DATA.color_depth) {
        Object.defineProperty(screen, 'colorDepth', {
            get: () => FINGERPRINT_DATA.color_depth,
            configurable: false,
            enumerable: true
        });
        
        Object.defineProperty(screen, 'pixelDepth', {
            get: () => FINGERPRINT_DATA.color_depth,
            configurable: false,
            enumerable: true
        });
    }
    
    // Override Timezone
    if (FINGERPRINT_DATA.timezone) {
        const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
        const originalToLocaleString = Date.prototype.toLocaleString;
        const originalToLocaleDateString = Date.prototype.toLocaleDateString;
        const originalToLocaleTimeString = Date.prototype.toLocaleTimeString;
        
        // Calculate timezone offset for the fake timezone
        const fakeTimezone = FINGERPRINT_DATA.timezone;
        const timezoneOffsets = {
            'Europe/London': 0, 'Europe/Paris': -60, 'Europe/Berlin': -60,
            'America/New_York': 300, 'America/Chicago': 360, 'America/Los_Angeles': 480,
            'Asia/Tokyo': -540, 'Asia/Shanghai': -480, 'Australia/Sydney': -660
        };
        const fakeOffset = timezoneOffsets[fakeTimezone] || 0;
        
        Date.prototype.getTimezoneOffset = function() {
            return fakeOffset;
        };
        
        // Override Intl.DateTimeFormat
        const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {
            const options = originalResolvedOptions.call(this);
            options.timeZone = fakeTimezone;
            return options;
        };
    }
    
    // Override WebGL fingerprinting
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(contextType, contextAttributes) {
        const context = originalGetContext.call(this, contextType, contextAttributes);
        
        if (contextType === 'webgl' || contextType === 'experimental-webgl' || contextType === 'webgl2') {
            if (FINGERPRINT_DATA.webgl_vendor) {
                const originalGetParameter = context.getParameter;
                context.getParameter = function(parameter) {
                    if (parameter === context.VENDOR) {
                        return FINGERPRINT_DATA.webgl_vendor;
                    }
                    if (parameter === context.RENDERER) {
                        return FINGERPRINT_DATA.webgl_renderer;
                    }
                    return originalGetParameter.call(this, parameter);
                };
            }
            
            // Add WebGL noise
            if (FINGERPRINT_DATA.webgl_noise) {
                const originalReadPixels = context.readPixels;
                context.readPixels = function(x, y, width, height, format, type, pixels) {
                    originalReadPixels.call(this, x, y, width, height, format, type, pixels);
                    if (pixels && pixels.length) {
                        for (let i = 0; i < pixels.length; i++) {
                            pixels[i] += Math.floor(FINGERPRINT_DATA.webgl_noise * 255) * (Math.random() - 0.5);
                        }
                    }
                    return pixels;
                };
            }
        }
        
        return context;
    };
    
    // Override Canvas fingerprinting
    if (FINGERPRINT_DATA.canvas_noise) {
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        
        HTMLCanvasElement.prototype.toDataURL = function() {
            const context = this.getContext('2d');
            if (context) {
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
                    imageData.data[i + 1] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
                    imageData.data[i + 2] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
                }
                context.putImageData(imageData, 0, 0);
            }
            return originalToDataURL.apply(this, arguments);
        };
        
        CanvasRenderingContext2D.prototype.getImageData = function() {
            const imageData = originalGetImageData.apply(this, arguments);
            for (let i = 0; i < imageData.data.length; i += 4) {
                imageData.data[i] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
                imageData.data[i + 1] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
                imageData.data[i + 2] += Math.floor(FINGERPRINT_DATA.canvas_noise * 255) * (Math.random() - 0.5);
            }
            return imageData;
        };
    }
    
    // Override AudioContext fingerprinting
    if (FINGERPRINT_DATA.audio_noise) {
        const AudioContexts = [window.AudioContext, window.webkitAudioContext].filter(Boolean);
        AudioContexts.forEach(AudioContext => {
            const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
            AudioContext.prototype.createAnalyser = function() {
                const analyser = originalCreateAnalyser.call(this);
                const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                analyser.getFloatFrequencyData = function(array) {
                    originalGetFloatFrequencyData.call(this, array);
                    for (let i = 0; i < array.length; i++) {
                        array[i] += FINGERPRINT_DATA.audio_noise * (Math.random() - 0.5);
                    }
                    return array;
                };
                return analyser;
            };
        });
    }
    
    // Override Battery API
    if (FINGERPRINT_DATA.battery_level !== undefined) {
        if (navigator.getBattery) {
            const originalGetBattery = navigator.getBattery;
            navigator.getBattery = function() {
                return originalGetBattery.call(this).then(battery => {
                    Object.defineProperty(battery, 'level', {
                        get: () => FINGERPRINT_DATA.battery_level,
                        configurable: false,
                        enumerable: true
                    });
                    Object.defineProperty(battery, 'charging', {
                        get: () => FINGERPRINT_DATA.battery_charging,
                        configurable: false,
                        enumerable: true
                    });
                    return battery;
                });
            };
        }
    }
    
    // Override Connection API
    if (FINGERPRINT_DATA.connection_type) {
        if (navigator.connection) {
            Object.defineProperty(navigator.connection, 'effectiveType', {
                get: () => FINGERPRINT_DATA.connection_type,
                configurable: false,
                enumerable: true
            });
            
            if (FINGERPRINT_DATA.connection_downlink) {
                Object.defineProperty(navigator.connection, 'downlink', {
                    get: () => FINGERPRINT_DATA.connection_downlink,
                    configurable: false,
                    enumerable: true
                });
            }
            
            if (FINGERPRINT_DATA.connection_rtt) {
                Object.defineProperty(navigator.connection, 'rtt', {
                    get: () => FINGERPRINT_DATA.connection_rtt,
                    configurable: false,
                    enumerable: true
                });
            }
        }
    }
    
    // Override Do Not Track
    if (FINGERPRINT_DATA.do_not_track) {
        Object.defineProperty(navigator, 'doNotTrack', {
            get: () => FINGERPRINT_DATA.do_not_track,
            configurable: false,
            enumerable: true
        });
    }
    
    // Override devicePixelRatio
    if (FINGERPRINT_DATA.pixel_ratio) {
        Object.defineProperty(window, 'devicePixelRatio', {
            get: () => FINGERPRINT_DATA.pixel_ratio,
            configurable: false,
            enumerable: true
        });
    }
    
    // Override Permission API
    if (FINGERPRINT_DATA.permissions && navigator.permissions) {
        const originalQuery = navigator.permissions.query;
        navigator.permissions.query = function(permissionDesc) {
            const permissionName = permissionDesc.name;
            if (FINGERPRINT_DATA.permissions[permissionName]) {
                return Promise.resolve({
                    state: FINGERPRINT_DATA.permissions[permissionName],
                    onchange: null
                });
            }
            return originalQuery.call(this, permissionDesc);
        };
    }
    
    console.log('Fingerprint injection completed successfully');
    
})(); 