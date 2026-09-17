/**
 * SkyCast User Authentication Module
 */
import { loginUser, registerUser, fetchCurrentUser } from '../api.js';

let currentUser = null;
let isRegisterMode = false;
let onAuthSuccessCallback = null;

export function initAuth(onSuccess) {
    onAuthSuccessCallback = onSuccess;

    const modal = document.getElementById('auth-modal');
    const modalBtn = document.getElementById('auth-modal-btn');
    const closeBtn = document.getElementById('auth-modal-close');
    const form = document.getElementById('auth-form');
    const switchLink = document.getElementById('auth-switch-link');

    // Check if user is already logged in via stored JWT token
    checkExistingSession();

    if (modalBtn && modal) {
        modalBtn.addEventListener('click', () => {
            if (currentUser) {
                // Logout user on click if logged in
                if (confirm(`Logged in as ${currentUser.username}. Do you want to sign out?`)) {
                    localStorage.removeItem('skycast_jwt_token');
                    currentUser = null;
                    updateAuthUI();
                }
            } else {
                modal.classList.add('active');
            }
        });
    }

    if (closeBtn && modal) {
        closeBtn.addEventListener('click', () => modal.classList.remove('active'));
    }

    modal?.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('active');
    });

    if (switchLink) {
        switchLink.addEventListener('click', (e) => {
            e.preventDefault();
            isRegisterMode = !isRegisterMode;
            updateAuthModalState();
        });
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const usernameInput = document.getElementById('auth-username-input')?.value.trim();
            const emailInput = document.getElementById('auth-email-input')?.value.trim();
            const passwordInput = document.getElementById('auth-password-input')?.value;

            try {
                let res;
                if (isRegisterMode) {
                    res = await registerUser(usernameInput, emailInput, passwordInput, 'London');
                } else {
                    res = await loginUser(emailInput, passwordInput);
                }

                if (res.success && res.token) {
                    localStorage.setItem('skycast_jwt_token', res.token);
                    currentUser = res.user;
                    modal.classList.remove('active');
                    updateAuthUI();
                    if (onAuthSuccessCallback) onAuthSuccessCallback(currentUser);
                } else {
                    alert(res.error || 'Authentication failed');
                }
            } catch (err) {
                console.error(err);
                alert('An error occurred during authentication');
            }
        });
    }
}

async function checkExistingSession() {
    const token = localStorage.getItem('skycast_jwt_token');
    if (!token) return;

    try {
        const res = await fetchCurrentUser();
        if (res.success && res.user) {
            currentUser = res.user;
            updateAuthUI();
        } else {
            localStorage.removeItem('skycast_jwt_token');
        }
    } catch (e) {
        localStorage.removeItem('skycast_jwt_token');
    }
}

function updateAuthModalState() {
    const title = document.getElementById('auth-modal-title');
    const usernameGroup = document.getElementById('username-group');
    const submitBtn = document.getElementById('auth-submit-btn');
    const switchText = document.getElementById('auth-switch-text');
    const switchLink = document.getElementById('auth-switch-link');

    if (isRegisterMode) {
        if (title) title.textContent = 'Create a SkyCast Account';
        if (usernameGroup) usernameGroup.style.display = 'flex';
        if (submitBtn) submitBtn.textContent = 'Register Account';
        if (switchText) switchText.textContent = 'Already have an account?';
        if (switchLink) switchLink.textContent = 'Sign In';
    } else {
        if (title) title.textContent = 'Sign In to SkyCast';
        if (usernameGroup) usernameGroup.style.display = 'none';
        if (submitBtn) submitBtn.textContent = 'Sign In';
        if (switchText) switchText.textContent = "Don't have an account?";
        if (switchLink) switchLink.textContent = 'Register Now';
    }
}

function updateAuthUI() {
    const label = document.getElementById('auth-btn-label');
    if (label) {
        label.textContent = currentUser ? currentUser.username : 'Sign In';
    }
}

export function getCurrentUser() {
    return currentUser;
}
