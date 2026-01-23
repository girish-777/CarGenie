/**
 * Simple notification system
 */

// Simple notification function
function showNotification(message, type = 'success') {
    // Remove any existing notifications
    const old = document.querySelector('.notification-popup');
    if (old) old.remove();
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification-popup';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#2563eb'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        font-weight: 500;
        min-width: 250px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
    
    console.log('[Notifications] Notification shown:', message);
}

// Simple confirm dialog
function showConfirm(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 10001;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        const dialog = document.createElement('div');
        dialog.style.cssText = `
            background: white;
            padding: 2rem;
            border-radius: 0.5rem;
            max-width: 400px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        `;
        
        dialog.innerHTML = `
            <div style="margin-bottom: 1.5rem; color: #1f2937; font-size: 1.1rem;">${message}</div>
            <div style="display: flex; gap: 1rem; justify-content: flex-end;">
                <button class="btn-cancel" style="padding: 0.5rem 1.5rem; border: none; border-radius: 0.25rem; background: #e5e7eb; color: #374151; cursor: pointer;">Cancel</button>
                <button class="btn-ok" style="padding: 0.5rem 1.5rem; border: none; border-radius: 0.25rem; background: #2563eb; color: white; cursor: pointer;">OK</button>
            </div>
        `;
        
        overlay.appendChild(dialog);
        document.body.appendChild(overlay);
        
        dialog.querySelector('.btn-ok').onclick = () => {
            overlay.remove();
            resolve(true);
        };
        
        dialog.querySelector('.btn-cancel').onclick = () => {
            overlay.remove();
            resolve(false);
        };
        
        overlay.onclick = (e) => {
            if (e.target === overlay) {
                overlay.remove();
                resolve(false);
            }
        };
    });
}

// Add CSS animation
if (!document.getElementById('notification-styles')) {
    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Make globally available
window.showNotification = showNotification;
window.showConfirm = showConfirm;

console.log('[Notifications] System loaded and ready');
