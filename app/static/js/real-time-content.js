/**
 * Real-time Content Management module for the Pregnancy & Baby Care application
 */

(function() {
    'use strict';

    class ContentManager {
        constructor() {
            this.isActive = false;
            this.subscribers = new Map();
            this.updateQueue = [];
            this.lastUpdate = null;
            this.init();
        }

        init() {
            console.log('📡 Initializing real-time content manager...');
            
            // Listen for storage events (for cross-tab communication)
            window.addEventListener('storage', (e) => {
                this.handleStorageEvent(e);
            });

            // Listen for visibility changes
            document.addEventListener('visibilitychange', () => {
                this.handleVisibilityChange();
            });

            console.log('✅ Real-time content manager initialized');
        }

        // Start content monitoring
        start() {
            if (this.isActive) {
                console.log('Content monitoring already active');
                return;
            }

            this.isActive = true;
            console.log('📡 Started real-time content monitoring');

            // Simulate periodic content checks (in a real app, this might be WebSocket or polling)
            this.startContentPolling();
        }

        // Stop content monitoring
        stop() {
            this.isActive = false;
            console.log('📡 Stopped real-time content monitoring');
        }

        // Subscribe to content updates
        subscribe(contentType, callback) {
            if (!this.subscribers.has(contentType)) {
                this.subscribers.set(contentType, []);
            }
            
            this.subscribers.get(contentType).push(callback);
            console.log(`📡 Subscribed to ${contentType} content updates`);
        }

        // Unsubscribe from content updates
        unsubscribe(contentType, callback) {
            if (this.subscribers.has(contentType)) {
                const callbacks = this.subscribers.get(contentType);
                const index = callbacks.indexOf(callback);
                if (index > -1) {
                    callbacks.splice(index, 1);
                    console.log(`📡 Unsubscribed from ${contentType} content updates`);
                }
            }
        }

        // Notify subscribers of content updates
        notifySubscribers(contentType, content) {
            const allSubscribers = this.subscribers.get('all') || [];
            const typeSubscribers = this.subscribers.get(contentType) || [];
            
            [...allSubscribers, ...typeSubscribers].forEach(callback => {
                try {
                    callback(content, contentType);
                } catch (error) {
                    console.error('Error in content update callback:', error);
                }
            });
        }

        // Handle storage events (cross-tab communication)
        handleStorageEvent(event) {
            if (event.key === 'contentUpdate') {
                try {
                    const updateData = JSON.parse(event.newValue);
                    console.log('📡 Received content update from storage:', updateData);
                    
                    this.notifySubscribers(updateData.type, updateData.content);
                } catch (error) {
                    console.error('Error parsing content update:', error);
                }
            }
        }

        // Handle visibility changes
        handleVisibilityChange() {
            if (document.hidden) {
                console.log('📡 Page hidden, reducing content monitoring');
            } else {
                console.log('📡 Page visible, resuming full content monitoring');
                // Trigger a content refresh when page becomes visible
                this.checkForUpdates();
            }
        }

        // Start content polling (simulated real-time updates)
        startContentPolling() {
            // In a real application, this would be replaced with WebSocket connections
            // or Server-Sent Events for true real-time updates
            
            setInterval(() => {
                if (this.isActive && !document.hidden) {
                    this.checkForUpdates();
                }
            }, 30000); // Check every 30 seconds
        }

        // Check for content updates
        async checkForUpdates() {
            try {
                // Check for real content updates from the server
                const response = await fetch('/api/content-updates');
                if (response.ok) {
                    const data = await response.json();

                    if (data.success && data.updates && data.updates.length > 0) {
                        console.log(`📡 Found ${data.updates.length} content updates`);

                        // Process each update
                        for (const update of data.updates) {
                            const contentType = update.content_type;
                            const action = update.action;

                            // Fetch fresh content for the updated type
                            await this.fetchAndNotifyContent(contentType, action);
                        }
                    }
                }
            } catch (error) {
                console.error('Error checking for content updates:', error);
            }
        }

        // Fetch fresh content and notify subscribers
        async fetchAndNotifyContent(contentType, action) {
            try {
                let apiEndpoint = '';
                switch (contentType) {
                    case 'nutrition':
                        apiEndpoint = '/api/nutrition-data';
                        break;
                    case 'faq':
                        apiEndpoint = '/api/faq-data';
                        break;
                    case 'vaccination':
                        apiEndpoint = '/api/vaccination-data';
                        break;
                    case 'schemes':
                        apiEndpoint = '/api/schemes-data';
                        break;
                    default:
                        return;
                }

                const response = await fetch(apiEndpoint);
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        console.log(`📡 Broadcasting ${contentType} update (${action}):`, data.data);

                        // Notify subscribers with fresh content
                        this.notifySubscribers(contentType, {
                            action: action,
                            data: data.data,
                            count: data.count,
                            timestamp: new Date().toISOString()
                        });
                    }
                }
            } catch (error) {
                console.error(`Error fetching ${contentType} content:`, error);
            }
        }

        // Trigger manual content update
        triggerUpdate(contentType, content) {
            console.log(`📡 Triggering manual content update: ${contentType}`);
            
            // Store in localStorage for cross-tab communication
            const updateData = {
                type: contentType,
                content: content,
                timestamp: new Date().toISOString()
            };
            
            try {
                localStorage.setItem('contentUpdate', JSON.stringify(updateData));
                // Remove after a short delay to trigger storage event
                setTimeout(() => {
                    localStorage.removeItem('contentUpdate');
                }, 100);
            } catch (error) {
                console.error('Error storing content update:', error);
            }
            
            // Notify local subscribers
            this.notifySubscribers(contentType, content);
        }

        // Get current status
        getStatus() {
            return {
                isActive: this.isActive,
                subscriberCount: this.subscribers.size,
                lastUpdate: this.lastUpdate
            };
        }
    }

    // Initialize and expose content manager
    window.contentManager = new ContentManager();

    // Auto-start if not in admin mode
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            console.log('✅ Real-time content management ready');
        });
    } else {
        console.log('✅ Real-time content management ready');
    }

})();
