document.addEventListener('DOMContentLoaded', () => {
    // Form validation and enhancement for both login and registration
    const authForm = document.querySelector('.auth-form form');
    const inputs = document.querySelectorAll('.auth-form input');
    const submitBtn = document.querySelector('.auth-form .btn');

    // Add floating label effect
    inputs.forEach(input => {
        // Add animation classes when input is focused/filled
        input.addEventListener('focus', () => {
            input.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', () => {
            if (!input.value) {
                input.parentElement.classList.remove('focused');
            }
        });

        // Add visual feedback for validation
        input.addEventListener('input', validateInput);
    });

    function validateInput(e) {
        const input = e.target;
        const value = input.value.trim();
        
        switch(input.getAttribute('type')) {
            case 'email':
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailPattern.test(value)) {
                    showError(input, 'Please enter a valid email address');
                } else {
                    clearError(input);
                }
                break;
                
            case 'password':
                if (value.length < 6) {
                    showError(input, 'Password must be at least 6 characters');
                } else {
                    clearError(input);
                }
                break;
                
            case 'text': // Username
                if (value.length < 3) {
                    showError(input, 'Username must be at least 3 characters');
                } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
                    showError(input, 'Username can only contain letters, numbers and underscore');
                } else {
                    clearError(input);
                }
                break;
        }
        
        updateSubmitButton();
    }

    function showError(input, message) {
        const formGroup = input.parentElement;
        let errorDiv = formGroup.querySelector('.error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            formGroup.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        formGroup.classList.add('has-error');
    }

    function clearError(input) {
        const formGroup = input.parentElement;
        const errorDiv = formGroup.querySelector('.error-message');
        
        if (errorDiv) {
            errorDiv.remove();
        }
        formGroup.classList.remove('has-error');
    }

    function updateSubmitButton() {
        const hasErrors = document.querySelectorAll('.has-error').length > 0;
        const emptyInputs = Array.from(inputs).some(input => !input.value.trim());
        
        submitBtn.disabled = hasErrors || emptyInputs;
        submitBtn.classList.toggle('disabled', hasErrors || emptyInputs);
    }

    // Add loading state during form submission
    if (authForm) {
        authForm.addEventListener('submit', (e) => {
            const submitButton = authForm.querySelector('.btn');
            
            // Prevent double submission
            if (submitButton.classList.contains('loading')) {
                e.preventDefault();
                return;
            }
            
            submitButton.classList.add('loading');
            submitButton.innerHTML = '<span class="spinner"></span> Processing...';
        });
    }

    // Show/hide password functionality
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        const toggleButton = document.createElement('button');
        toggleButton.type = 'button';
        toggleButton.className = 'password-toggle';
        toggleButton.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(toggleButton);
        
        toggleButton.addEventListener('click', () => {
            const type = input.getAttribute('type');
            input.setAttribute('type', type === 'password' ? 'text' : 'password');
            toggleButton.classList.toggle('show');
        });
    });

    // Add subtle animation for form appearance
    const authContainer = document.querySelector('.auth-form');
    if (authContainer) {
        authContainer.style.opacity = '0';
        authContainer.style.transform = 'translateY(20px)';
        
        requestAnimationFrame(() => {
            authContainer.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            authContainer.style.opacity = '1';
            authContainer.style.transform = 'translateY(0)';
        });
    }
});
