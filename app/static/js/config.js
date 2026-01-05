/**
 * Configuration file for the Pregnancy & Baby Care application
 */

// Application configuration
window.appConfig = {
    // API endpoints
    api: {
        baseUrl: window.location.origin,
        endpoints: {
            auth: '/auth',
            checkAuth: '/auth/check-auth',
            login: '/auth/login',
            logout: '/auth/logout',
            register: '/auth/register',
            userData: '/auth/api/user-data',
            pregnancy: '/pregnancy',
            babycare: '/babycare',
            admin: '/admin'
        }
    },
    
    // Application settings
    app: {
        name: 'Maternal and Child Health Monitoring',
        version: '1.0.0',
        debug: false
    },
    
    // UI settings
    ui: {
        theme: 'default',
        animations: true,
        notifications: true
    },
    
    // Authentication settings
    auth: {
        sessionTimeout: 30 * 60 * 1000, // 30 minutes
        checkInterval: 5 * 60 * 1000,   // 5 minutes
        maxRetries: 3
    }
};

// Environment detection
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.appConfig.app.debug = true;
}

// Export for other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.appConfig;
}

console.log('✅ Config loaded:', window.appConfig.app.name, 'v' + window.appConfig.app.version);
