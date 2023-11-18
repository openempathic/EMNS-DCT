document.getElementById('other').addEventListener('change', function() {
    var otherTextArea = document.getElementById('otherReason');
    if(this.checked) {
        otherTextArea.style.display = 'block';
    } else {
        otherTextArea.style.display = 'none';
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const submitButton = document.getElementById("submitReport");
    const checkboxes = document.querySelectorAll('#reportModal .form-check-input');

    function updateSubmitButtonState() {
        const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
        submitButton.disabled = !isChecked;
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener("change", updateSubmitButtonState);
    });

    updateSubmitButtonState(); // Initial check
});
