/**
 * Global Frontend State & Shared UI Helpers for HaulPool Network
 */
window.HaulPool = {
    user: null,
    
    // Toast notification utility
    showToast: function(message, isError = false) {
        let toast = document.getElementById('authToast') || document.getElementById('globalToast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'globalToast';
            toast.style.cssText = `
                position: fixed;
                bottom: 24px;
                right: 24px;
                background: ${isError ? '#2d1215' : '#141f38'};
                color: ${isError ? '#f87171' : '#fde68a'};
                border: 1px solid ${isError ? '#ef4444' : '#f59e0b'};
                padding: 14px 24px;
                border-radius: 12px;
                font-size: 0.9rem;
                font-weight: 700;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
                z-index: 9999;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(toast);
        }
        
        toast.innerHTML = `<i class="fa-solid ${isError ? 'fa-circle-exclamation' : 'fa-circle-check'}"></i> <span>${message}</span>`;
        toast.style.opacity = '1';
        toast.style.display = 'flex';
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => { toast.style.display = 'none'; }, 300);
        }, 3800);
    },

    // Spinner and button state handler
    setButtonLoading: function(button, isLoading, loadingText = 'Processing...') {
        if (!button) return;
        if (isLoading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.style.opacity = '0.75';
            button.style.cursor = 'not-allowed';
            button.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${loadingText}`;
        } else {
            button.disabled = false;
            button.style.opacity = '1';
            button.style.cursor = 'pointer';
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
            }
        }
    },

    // Fetch current authenticated user profile
    fetchCurrentUser: async function() {
        try {
            const res = await fetch('/api/auth/me');
            if (res.ok) {
                const data = await res.json();
                if (data.authenticated && data.user) {
                    this.user = data.user;
                    this.updateDynamicHeader(data.user);
                }
            }
        } catch (e) {
            console.error('Auth state check failed:', e);
        }
    },

    // Dynamically personalize header & navigation based on user role
    updateDynamicHeader: function(user) {
        if (!user) return;

        const headerActions = document.querySelector('.header-actions');
        const headerNav = document.querySelector('header nav');
        const badge = document.querySelector('.header-badge');

        if (badge) {
            if (user.role === 'OPERATOR') {
                badge.innerHTML = `<i class="fa-solid fa-truck-front" style="color: #f59e0b;"></i> Fleet Portal: <strong>${user.company_name || user.name}</strong>`;
            } else if (user.role === 'CUSTOMER') {
                badge.innerHTML = `<i class="fa-solid fa-user-check" style="color: #10b981;"></i> Welcome, <strong>${user.name}</strong>`;
            }
        }

        if (headerNav) {
            if (user.role === 'OPERATOR') {
                headerNav.innerHTML = `
                    <a href="/operator/dashboard"><i class="fas fa-chart-line"></i> Dashboard</a>
                    <a href="/operator/route-planner"><i class="fas fa-route"></i> Route Planner</a>
                    <a href="/operator/analytics"><i class="fas fa-chart-pie"></i> Fleet Analytics</a>
                `;
            } else if (user.role === 'CUSTOMER') {
                headerNav.innerHTML = `
                    <a href="/customer/dashboard"><i class="fas fa-compass"></i> Find Routes</a>
                    <a href="/customer/shipments"><i class="fas fa-box"></i> My Shipments</a>
                    <a href="/customer/profile"><i class="fas fa-user-gear"></i> Profile</a>
                `;
            }
        }

        if (headerActions) {
            const dashboardUrl = user.role === 'OPERATOR' ? '/operator/dashboard' : '/customer/dashboard';
            headerActions.innerHTML = `
                <a href="${dashboardUrl}" class="btn btn-outline"><i class="fas fa-grip"></i> Dashboard</a>
                <a href="/api/auth/logout" class="btn btn-primary" style="background: rgba(239, 68, 68, 0.2); border: 1px solid rgba(239, 68, 68, 0.4); color: #f87171;"><i class="fas fa-right-from-bracket"></i> Logout</a>
            `;
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    window.HaulPool.fetchCurrentUser();
});
