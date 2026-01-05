/**
 * Common Header module for the Pregnancy & Baby Care application
 */

(function() {
    'use strict';

    class CommonHeader {
        constructor() {
            this.isInitialized = false;
            this.headerElement = null;
            this.init();
        }

        init() {
            console.log('🎯 Initializing common header...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    this.setupHeader();
                });
            } else {
                this.setupHeader();
            }
        }

        setupHeader() {
            // Find the common header container
            this.headerElement = document.getElementById('common-header');
            
            if (!this.headerElement) {
                console.log('No common header container found');
                return;
            }

            // Check if we should show a common header
            // For now, we'll keep it minimal since each page has its own header
            this.renderMinimalHeader();
            
            this.isInitialized = true;
            console.log('✅ Common header initialized');
        }

        renderMinimalHeader() {
            // For now, just add a minimal status indicator
            // This could be expanded to show notifications, user status, etc.
            
            const statusHtml = `
                <div id="app-status" style="display: none; position: fixed; top: 10px; right: 10px; z-index: 9999;">
                    <div style="background: #4caf50; color: white; padding: 8px 12px; border-radius: 4px; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                        <i class="fas fa-check-circle"></i> Connected
                    </div>
                </div>
            `;
            
            this.headerElement.innerHTML = statusHtml;
        }

        // Show connection status
        showConnectionStatus(isConnected = true) {
            const statusElement = document.getElementById('app-status');
            if (statusElement) {
                const statusDiv = statusElement.querySelector('div');
                if (isConnected) {
                    statusDiv.style.background = '#4caf50';
                    statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Connected';
                } else {
                    statusDiv.style.background = '#f44336';
                    statusDiv.innerHTML = '<i class="fas fa-exclamation-circle"></i> Disconnected';
                }
                statusElement.style.display = 'block';
                
                // Auto-hide after 3 seconds if connected
                if (isConnected) {
                    setTimeout(() => {
                        statusElement.style.display = 'none';
                    }, 3000);
                }
            }
        }

        // Show notification in header area
        showNotification(message, type = 'info', duration = 5000) {
            const notificationHtml = `
                <div id="header-notification" style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999; max-width: 400px;">
                    <div style="background: ${this.getNotificationColor(type)}; color: white; padding: 12px 16px; border-radius: 8px; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); display: flex; align-items: center; gap: 8px;">
                        <i class="fas ${this.getNotificationIcon(type)}"></i>
                        <span>${message}</span>
                        <button onclick="this.parentElement.parentElement.remove()" style="background: none; border: none; color: white; font-size: 16px; cursor: pointer; margin-left: auto;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            `;
            
            // Remove existing notification
            const existing = document.getElementById('header-notification');
            if (existing) {
                existing.remove();
            }
            
            // Add new notification
            document.body.insertAdjacentHTML('afterbegin', notificationHtml);
            
            // Auto-remove after duration
            if (duration > 0) {
                setTimeout(() => {
                    const notification = document.getElementById('header-notification');
                    if (notification) {
                        notification.remove();
                    }
                }, duration);
            }
        }

        getNotificationColor(type) {
            switch (type) {
                case 'success': return '#4caf50';
                case 'error': return '#f44336';
                case 'warning': return '#ff9800';
                case 'info':
                default: return '#2196f3';
            }
        }

        getNotificationIcon(type) {
            switch (type) {
                case 'success': return 'fa-check-circle';
                case 'error': return 'fa-exclamation-circle';
                case 'warning': return 'fa-exclamation-triangle';
                case 'info':
                default: return 'fa-info-circle';
            }
        }

        // Update user info in header (if applicable)
        updateUserInfo(user) {
            // This could be used to show user info in a common header
            console.log('User info updated in header:', user);
        }

        // Show loading state
        showLoading(message = 'Loading...') {
            this.showNotification(message, 'info', 0);
        }

        // Hide loading state
        hideLoading() {
            const notification = document.getElementById('header-notification');
            if (notification) {
                notification.remove();
            }
        }

        // Get header status
        getStatus() {
            return {
                isInitialized: this.isInitialized,
                hasHeaderElement: !!this.headerElement
            };
        }
    }

    // Initialize and expose common header
    window.commonHeader = new CommonHeader();

    // Expose utility functions globally
    window.showNotification = function(message, type, duration) {
        if (window.commonHeader) {
            window.commonHeader.showNotification(message, type, duration);
        }
    };

    window.showConnectionStatus = function(isConnected) {
        if (window.commonHeader) {
            window.commonHeader.showConnectionStatus(isConnected);
        }
    };

    console.log('✅ Common header module ready');

})();
