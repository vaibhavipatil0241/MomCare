/**
 * API Integration module for the Pregnancy & Baby Care application
 */

(function() {
    'use strict';

    // API Client class
    class ApiClient {
        constructor() {
            this.baseUrl = window.appConfig?.api?.baseUrl || window.location.origin;
            this.endpoints = window.appConfig?.api?.endpoints || {};
            this.isInitialized = false;
            this.init();
        }

        init() {
            console.log('🔌 Initializing API client...');
            this.isInitialized = true;
        }

        // Health check endpoint
        async healthCheck() {
            try {
                const response = await fetch(`${this.baseUrl}/auth/check-auth`, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    return {
                        status: 'healthy',
                        authenticated: data.authenticated || false,
                        timestamp: new Date().toISOString()
                    };
                } else {
                    return {
                        status: 'error',
                        message: `HTTP ${response.status}`,
                        timestamp: new Date().toISOString()
                    };
                }
            } catch (error) {
                console.error('Health check failed:', error);
                return {
                    status: 'error',
                    message: error.message,
                    timestamp: new Date().toISOString()
                };
            }
        }

        // Authentication methods
        async checkAuth() {
            try {
                const response = await fetch(`${this.baseUrl}/auth/check-auth`, {
                    method: 'GET',
                    credentials: 'include'
                });
                
                if (response.ok) {
                    return await response.json();
                }
                return { authenticated: false };
            } catch (error) {
                console.error('Auth check failed:', error);
                return { authenticated: false };
            }
        }

        async login(email, password) {
            try {
                const response = await fetch(`${this.baseUrl}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include',
                    body: JSON.stringify({ email, password })
                });

                return await response.json();
            } catch (error) {
                console.error('Login failed:', error);
                throw error;
            }
        }

        async logout() {
            try {
                const response = await fetch(`${this.baseUrl}/auth/logout`, {
                    method: 'GET',
                    credentials: 'include'
                });
                
                return response.ok;
            } catch (error) {
                console.error('Logout failed:', error);
                return false;
            }
        }

        // Generic API request method
        async request(endpoint, options = {}) {
            const url = endpoint.startsWith('http') ? endpoint : `${this.baseUrl}${endpoint}`;
            
            const defaultOptions = {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            const finalOptions = { ...defaultOptions, ...options };

            try {
                const response = await fetch(url, finalOptions);
                
                if (response.ok) {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        return await response.json();
                    }
                    return await response.text();
                } else {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
            } catch (error) {
                console.error('API request failed:', error);
                throw error;
            }
        }
    }

    // Initialize and expose API client
    window.apiClient = new ApiClient();
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ API integration ready');
        });
    } else {
        console.log('✅ API integration ready');
    }

})();
