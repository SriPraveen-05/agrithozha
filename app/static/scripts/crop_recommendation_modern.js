// Modern Crop Recommendation JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('cropForm');
    const resetBtn = document.getElementById('resetForm');
    // IMPORTANT: scope inputs to this form only
    const inputs = form ? form.querySelectorAll('.form-input') : [];
    
    // Form validation and enhancement
    function initializeForm() {
        // Add real-time validation
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                validateInput(this);
                updateFormState();
            });
            
            input.addEventListener('blur', function() {
                validateInput(this);
            });
            
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });
        });
        
        // Form submission via fetch with timeout + redirect handling
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return;
            }
            e.preventDefault();
            setLoadingState(true);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 20000); // 20s timeout

            fetch(form.action, {
                method: form.method || 'POST',
                body: new FormData(form),
                signal: controller.signal,
                headers: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                },
                redirect: 'follow'
            }).then(async (resp) => {
                clearTimeout(timeoutId);
                if (resp.redirected) {
                    window.location.href = resp.url;
                    return;
                }
                const text = await resp.text();
                if (resp.ok) {
                    // Replace current page with server-rendered HTML
                    document.open();
                    document.write(text);
                    document.close();
                } else {
                    showGlobalError('Server returned an error. Please try again.');
                    setLoadingState(false);
                }
            }).catch((err) => {
                const reason = err?.name === 'AbortError' ? 'Request timed out. ' : '';
                showGlobalError(reason + 'Please check your connection and try again.');
                setLoadingState(false);
            });
        });
        
        // Reset form
        resetBtn.addEventListener('click', function() {
            resetForm();
        });
    }
    
    // Validate individual input
    function validateInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);
        const formGroup = input.parentElement;
        
        // Remove existing validation classes
        formGroup.classList.remove('valid', 'invalid');
        
        if (input.value === '') {
            formGroup.classList.add('invalid');
            showInputError(input, 'This field is required');
            return false;
        }
        
        if (isNaN(value)) {
            formGroup.classList.add('invalid');
            showInputError(input, 'Please enter a valid number');
            return false;
        }
        
        if (value < min || value > max) {
            formGroup.classList.add('invalid');
            showInputError(input, `Value must be between ${min} and ${max}`);
            return false;
        }
        
        formGroup.classList.add('valid');
        hideInputError(input);
        return true;
    }
    
    // Show input error
    function showInputError(input, message) {
        hideInputError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'input-error';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            color: var(--error);
            font-size: var(--font-size-xs);
            margin-top: var(--space-1);
            display: flex;
            align-items: center;
            gap: var(--space-1);
        `;
        
        input.parentElement.appendChild(errorDiv);
    }
    
    // Hide input error
    function hideInputError(input) {
        const existingError = input.parentElement.querySelector('.input-error');
        if (existingError) {
            existingError.remove();
        }
    }

    function showGlobalError(message) {
        // Simple top-of-form error banner
        let banner = document.getElementById('crop-form-error');
        if (!banner) {
            banner = document.createElement('div');
            banner.id = 'crop-form-error';
            banner.style.cssText = `
                margin-bottom: var(--space-4);
                padding: var(--space-3) var(--space-4);
                border: 1px solid var(--error);
                background: #FEF2F2;
                color: var(--error);
                border-radius: var(--radius-md);
            `;
            form.parentElement.insertBefore(banner, form);
        }
        banner.textContent = message;
    }
    
    // Validate entire form
    function validateForm() {
        let isValid = true;
        
        inputs.forEach(input => {
            if (!validateInput(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Update form state
    function updateFormState() {
        const allValid = Array.from(inputs).every(input => {
            const value = parseFloat(input.value);
            const min = parseFloat(input.min);
            const max = parseFloat(input.max);
            return input.value !== '' && !isNaN(value) && value >= min && value <= max;
        });
        
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = !allValid;
            submitBtn.style.opacity = allValid ? '1' : '0.6';
        }
    }
    
    function setLoadingState(loading) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (!submitBtn) return;
        if (loading) {
            // Add loading animation style once
            if (!document.getElementById('crop-loading-style')) {
                const loadingStyle = document.createElement('style');
                loadingStyle.id = 'crop-loading-style';
                loadingStyle.textContent = `
                    .loading {
                        display: inline-block;
                        width: 20px;
                        height: 20px;
                        border: 3px solid rgba(255, 255, 255, 0.3);
                        border-radius: 50%;
                        border-top-color: #fff;
                        animation: spin 1s ease-in-out infinite;
                    }
                `;
                document.head.appendChild(loadingStyle);
            }
            submitBtn.dataset.original = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="loading"></span> Processing...';
            submitBtn.disabled = true;
            form.classList.add('form-loading');
        } else {
            submitBtn.innerHTML = submitBtn.dataset.original || 'Submit';
            submitBtn.disabled = false;
            form.classList.remove('form-loading');
        }
    }
    
    // Reset form
    function resetForm() {
        form.reset();
        inputs.forEach(input => {
            const formGroup = input.parentElement;
            formGroup.classList.remove('valid', 'invalid', 'focused');
            hideInputError(input);
        });
        updateFormState();
        
        // Add reset animation
        form.style.transform = 'scale(0.98)';
        setTimeout(() => {
            form.style.transform = 'scale(1)';
        }, 150);
    }
    
    // Add input animations
    function addInputAnimations() {
        inputs.forEach((input, index) => {
            input.style.opacity = '0';
            input.style.transform = 'translateY(20px)';
            input.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                input.style.opacity = '1';
                input.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    // Add number input enhancements
    function enhanceNumberInputs() {
        inputs.forEach(input => {
            if (input.type === 'number') {
                // Add increment/decrement buttons
                const wrapper = document.createElement('div');
                wrapper.className = 'number-input-wrapper';
                wrapper.style.cssText = `
                    position: relative;
                    display: flex;
                    align-items: center;
                `;
                
                input.parentNode.insertBefore(wrapper, input);
                wrapper.appendChild(input);
                
                // Add step buttons
                const stepUp = document.createElement('button');
                stepUp.type = 'button';
                stepUp.innerHTML = '<i class="fas fa-plus"></i>';
                stepUp.className = 'step-btn step-up';
                stepUp.style.cssText = `
                    position: absolute;
                    right: 8px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: none;
                    border: none;
                    color: var(--gray-500);
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                `;
                
                const stepDown = document.createElement('button');
                stepDown.type = 'button';
                stepDown.innerHTML = '<i class="fas fa-minus"></i>';
                stepDown.className = 'step-btn step-down';
                stepDown.style.cssText = `
                    position: absolute;
                    right: 32px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: none;
                    border: none;
                    color: var(--gray-500);
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                `;
                
                wrapper.appendChild(stepUp);
                wrapper.appendChild(stepDown);
                
                // Add step functionality
                stepUp.addEventListener('click', () => {
                    const step = parseFloat(input.step) || 1;
                    const newValue = parseFloat(input.value) + step;
                    const max = parseFloat(input.max);
                    if (newValue <= max) {
                        input.value = newValue;
                        validateInput(input);
                        updateFormState();
                    }
                });
                
                stepDown.addEventListener('click', () => {
                    const step = parseFloat(input.step) || 1;
                    const newValue = parseFloat(input.value) - step;
                    const min = parseFloat(input.min);
                    if (newValue >= min) {
                        input.value = newValue;
                        validateInput(input);
                        updateFormState();
                    }
                });
                
                // Add hover effects
                [stepUp, stepDown].forEach(btn => {
                    btn.addEventListener('mouseenter', () => {
                        btn.style.color = 'var(--primary-color)';
                        btn.style.backgroundColor = 'var(--gray-100)';
                    });
                    
                    btn.addEventListener('mouseleave', () => {
                        btn.style.color = 'var(--gray-500)';
                        btn.style.backgroundColor = 'transparent';
                    });
                });
            }
        });
    }
    
    // Add form progress indicator
    function addProgressIndicator() {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'form-progress';
        progressContainer.style.cssText = `
            margin-bottom: var(--space-6);
            padding: var(--space-4);
            background: var(--gray-50);
            border-radius: var(--radius-lg);
            border: 1px solid var(--gray-200);
        `;
        
        const progressBar = document.createElement('div');
        progressBar.className = 'progress-bar';
        progressBar.style.cssText = `
            width: 0%;
            height: 8px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            border-radius: var(--radius-full);
            transition: width 0.3s ease;
        `;
        
        const progressText = document.createElement('div');
        progressText.className = 'progress-text';
        progressText.style.cssText = `
            margin-top: var(--space-2);
            font-size: var(--font-size-sm);
            color: var(--gray-600);
            text-align: center;
        `;
        
        progressContainer.appendChild(progressBar);
        progressContainer.appendChild(progressText);
        
        form.insertBefore(progressContainer, form.firstElementChild);
        
        // Update progress
        function updateProgress() {
            const filledInputs = Array.from(inputs).filter(input => input.value !== '').length;
            const progress = (filledInputs / inputs.length) * 100;
            
            progressBar.style.width = progress + '%';
            progressText.textContent = `${Math.round(progress)}% Complete`;
            
            if (progress === 100) {
                progressText.textContent = 'Ready to analyze!';
                progressText.style.color = 'var(--success)';
            }
        }
        
        inputs.forEach(input => {
            input.addEventListener('input', updateProgress);
        });
        
        updateProgress();
    }
    
    // Add tooltips for better UX
    function addTooltips() {
        const tooltipData = {
            nitrogen: 'Nitrogen is essential for leaf growth and overall plant health. Higher levels promote vigorous growth.',
            phosphorus: 'Phosphorus is crucial for root development, flowering, and fruit production.',
            potassium: 'Potassium helps with disease resistance, water regulation, and overall plant strength.',
            temperature: 'Temperature affects plant growth rates, flowering, and fruit development.',
            humidity: 'Humidity levels impact water uptake and disease susceptibility in plants.',
            ph: 'pH affects nutrient availability. Most crops prefer slightly acidic to neutral soil (6.0-7.0).',
            rainfall: 'Rainfall patterns determine water availability and influence crop selection.'
        };
        
        inputs.forEach(input => {
            const tooltip = document.createElement('div');
            tooltip.className = 'input-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                top: -40px;
                left: 50%;
                transform: translateX(-50%);
                background: var(--gray-800);
                color: white;
                padding: var(--space-2) var(--space-3);
                border-radius: var(--radius-md);
                font-size: var(--font-size-xs);
                white-space: nowrap;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
                z-index: 1000;
                pointer-events: none;
            `;
            
            const tooltipText = tooltipData[input.name];
            if (tooltipText) {
                tooltip.textContent = tooltipText;
                input.parentElement.style.position = 'relative';
                input.parentElement.appendChild(tooltip);
                
                input.addEventListener('mouseenter', () => {
                    tooltip.style.opacity = '1';
                    tooltip.style.visibility = 'visible';
                });
                
                input.addEventListener('mouseleave', () => {
                    tooltip.style.opacity = '0';
                    tooltip.style.visibility = 'hidden';
                });
            }
        });
    }
    
    // Initialize everything
    function init() {
        initializeForm();
        addInputAnimations();
        enhanceNumberInputs();
        addProgressIndicator();
        addTooltips();
        
        // Add form validation styles
        const validationStyles = document.createElement('style');
        validationStyles.textContent = `
            .form-group.valid .form-input {
                border-color: var(--success);
                box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
            }
            
            .form-group.invalid .form-input {
                border-color: var(--error);
                box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
            }
            
            .form-group.focused .form-label {
                color: var(--primary-color);
            }
            
            .number-input-wrapper {
                position: relative;
            }
            
            .number-input-wrapper .form-input {
                padding-right: 60px;
            }
        `;
        document.head.appendChild(validationStyles);
        
        console.log('🌱 Modern Crop Recommendation form initialized!');
    }
    
    // Start the application
    init();
});

