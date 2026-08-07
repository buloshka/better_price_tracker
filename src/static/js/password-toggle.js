document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('password-toggle');
    const passwordInput = document.getElementById('password');
    const eyeIcon = document.getElementById('eye-icon');
    const eyeSlashIcon = document.getElementById('eye-slash-icon');

    if (!toggleBtn || !passwordInput || !eyeIcon || !eyeSlashIcon) return;

    toggleBtn.addEventListener('click', () => {
        const start = passwordInput.selectionStart;
        const end = passwordInput.selectionEnd;

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            eyeIcon.style.display = 'none';
            eyeSlashIcon.style.display = 'block';
        } else {
            passwordInput.type = 'password';
            eyeIcon.style.display = 'block';
            eyeSlashIcon.style.display = 'none';
        }

        passwordInput.focus();
        try {
            passwordInput.setSelectionRange(start, end);
        } catch (e) {}
    });
});
