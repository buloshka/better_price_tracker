const inputs = document.querySelectorAll('.code-input');

inputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        const value = e.target.value;

        if (!/^[0-9]$/.test(value)) {
            e.target.value = '';
            return;
        }

        if (value && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace') {
            if (!e.target.value && index > 0) {
                inputs[index - 1].value = '';
                inputs[index - 1].focus();
            } else {
                e.target.value = '';
            }
            e.preventDefault();
        }

        if (e.key === 'ArrowLeft' && index > 0) {
            inputs[index - 1].focus();
        }
        if (e.key === 'ArrowRight' && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasteData = e.clipboardData.getData('text').trim();

        if (/^\d+$/.test(pasteData)) {
            const characters = pasteData.split('');

            inputs.forEach((inputField, i) => {
                if (i >= index && characters[i - index]) {
                    inputField.value = characters[i - index];
                    if (i < inputs.length - 1) {
                        inputs[i + 1].focus();
                    }
                }
            });
        }
    });
});
