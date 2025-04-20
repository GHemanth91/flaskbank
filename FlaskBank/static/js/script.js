// FlaskBank JavaScript

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation for transfer, deposit, and withdraw forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (form.querySelector('input[name="amount"]')) {
                const amountInput = form.querySelector('input[name="amount"]');
                const amount = parseFloat(amountInput.value);

                if (isNaN(amount) || amount <= 0) {
                    event.preventDefault();
                    alert('Please enter a valid amount greater than zero.');
                }
            }
        });
    });

    // Confirm password validation for registration form
    const registerForm = document.querySelector('form[action="/register"]');
    if (registerForm) {
        // Toggle admin code field visibility based on user type selection
        const userTypeRadios = document.querySelectorAll('input[name="user_type"]');
        const adminCodeDiv = document.getElementById('admin_code_div');
        const adminCodeInput = document.getElementById('admin_code');

        userTypeRadios.forEach(function(radio) {
            radio.addEventListener('change', function() {
                if (this.value === 'admin') {
                    adminCodeDiv.style.display = 'block';
                    adminCodeInput.setAttribute('required', 'required');
                } else {
                    adminCodeDiv.style.display = 'none';
                    adminCodeInput.removeAttribute('required');
                }
            });
        });

        registerForm.addEventListener('submit', function(event) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;

            if (password !== confirmPassword) {
                event.preventDefault();
                alert('Passwords do not match!');
            }

            // Validate admin code if admin is selected
            const adminRadio = document.getElementById('admin');
            if (adminRadio.checked) {
                const adminCode = adminCodeInput.value;
                if (!adminCode || adminCode.length !== 5 || !/^\d+$/.test(adminCode)) {
                    event.preventDefault();
                    alert('Please enter a valid 5-digit admin verification code.');
                }
            }
        });
    }
});
