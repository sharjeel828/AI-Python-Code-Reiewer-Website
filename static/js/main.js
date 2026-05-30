document.addEventListener('DOMContentLoaded', () => {
    // Tab Switching Logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active class from all
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            // Add active class to clicked
            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');

            // Clear inputs from inactive tab to prevent validation issues or huge payloads
            if (targetId === 'paste-tab') {
                document.getElementById('code_file').value = '';
                document.getElementById('file-name-display').textContent = 'No file selected';
            } else {
                document.getElementById('code_text').value = '';
            }
        });
    });

    // File Drag and Drop Logic
    const dropArea = document.getElementById('file-drop-area');
    const fileInput = document.getElementById('code_file');
    const fileNameDisplay = document.getElementById('file-name-display');

    if (dropArea && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.classList.remove('dragover');
            }, false);
        });

        dropArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;

            if (files.length > 0) {
                fileInput.files = files;
                updateFileName(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                updateFileName(e.target.files[0]);
            }
        });

        function updateFileName(file) {
            const allowedExtensions = ['.py', '.ipynb', '.pyw', '.pyi'];
            const hasValidExtension = allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
            if (hasValidExtension) {
                fileNameDisplay.textContent = file.name;
                fileNameDisplay.style.color = 'var(--success-color)';
            } else {
                fileNameDisplay.textContent = 'Invalid file type. Please select a python file (.py, .ipynb, .pyi, .pyw).';
                fileNameDisplay.style.color = 'var(--danger-color)';
                fileInput.value = ''; // clear
            }
        }
    }

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(() => {
            flashMessages.forEach(msg => {
                msg.style.opacity = '0';
                setTimeout(() => msg.remove(), 300);
            });
        }, 5000);
    }

    // Copy to clipboard functionality
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetSelector = btn.getAttribute('data-clipboard-target');
            const targetEl = document.querySelector(targetSelector);
            if (targetEl) {
                navigator.clipboard.writeText(targetEl.textContent).then(() => {
                    const originalHTML = btn.innerHTML;
                    btn.innerHTML = '<i class="ph ph-check text-success"></i> Copied!';
                    setTimeout(() => {
                        btn.innerHTML = originalHTML;
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    });
});
