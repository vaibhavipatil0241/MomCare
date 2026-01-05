/**
 * Unified Authentication module for the Pregnancy & Baby Care application
 */

(function() {
    'use strict';

    class UnifiedAuth {
        constructor() {
            this.isInitialized = false;
            this.currentUser = null;
            this.authCheckInterval = null;
            this.init();
        }

        async init() {
            console.log('🔐 Initializing unified authentication...');
            
            try {
                // Check current authentication status
                await this.checkSession();
                
                // Set up periodic auth checks
                this.startAuthMonitoring();
                
                this.isInitialized = true;
                console.log('✅ Unified auth initialized');
            } catch (error) {
                console.error('Auth initialization failed:', error);
                this.isInitialized = true; // Still mark as initialized to prevent blocking
            }
        }

        // Check if user is authenticated
        isAuthenticated() {
            return this.currentUser !== null;
        }

        // Get current user data
        getCurrentUser() {
            return this.currentUser;
        }

        // Check session with server
        async checkSession() {
            try {
                if (!window.apiClient) {
                    console.warn('API client not available for session check');
                    return false;
                }

                const response = await window.apiClient.checkAuth();
                
                if (response.authenticated && response.user) {
                    this.currentUser = response.user;
                    return true;
                } else {
                    this.currentUser = null;
                    return false;
                }
            } catch (error) {
                console.error('Session check failed:', error);
                this.currentUser = null;
                return false;
            }
        }

        // Login method
        async login(email, password) {
            try {
                if (!window.apiClient) {
                    throw new Error('API client not available');
                }

                const response = await window.apiClient.login(email, password);
                
                if (response.success && response.user) {
                    this.currentUser = response.user;
                    return { success: true, user: response.user };
                } else {
                    return { success: false, error: response.error || 'Login failed' };
                }
            } catch (error) {
                console.error('Login error:', error);
                return { success: false, error: error.message };
            }
        }

        // Logout method
        async logout() {
            try {
                if (window.apiClient) {
                    await window.apiClient.logout();
                }
                
                this.currentUser = null;
                
                // Redirect to home page
                window.location.href = '/';
                
                return true;
            } catch (error) {
                console.error('Logout error:', error);
                return false;
            }
        }

        // Require authentication (redirect if not authenticated)
        requireAuth() {
            if (!this.isAuthenticated()) {
                console.log('Authentication required, redirecting to login...');
                window.location.href = '/auth/login';
                return false;
            }
            return true;
        }

        // Start monitoring authentication status
        startAuthMonitoring() {
            const interval = window.appConfig?.auth?.checkInterval || 5 * 60 * 1000; // 5 minutes
            
            this.authCheckInterval = setInterval(async () => {
                const isAuth = await this.checkSession();
                if (!isAuth && this.currentUser) {
                    console.log('Session expired, logging out...');
                    this.logout();
                }
            }, interval);
        }

        // Stop monitoring authentication status
        stopAuthMonitoring() {
            if (this.authCheckInterval) {
                clearInterval(this.authCheckInterval);
                this.authCheckInterval = null;
            }
        }

        // Update user data
        updateUser(userData) {
            this.currentUser = userData;
        }

        // Check if user has specific role
        hasRole(role) {
            return this.currentUser && this.currentUser.role === role;
        }

        // Check if user is admin
        isAdmin() {
            return this.hasRole('admin');
        }

        // Check if user is doctor
        isDoctor() {
            return this.hasRole('doctor');
        }

        // Get user role
        getUserRole() {
            return this.currentUser ? this.currentUser.role : null;
        }
    }

    // Initialize and expose unified auth
    window.unifiedAuth = new UnifiedAuth();

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ Unified authentication ready');
        });
    } else {
        console.log('✅ Unified authentication ready');
    }

})();
