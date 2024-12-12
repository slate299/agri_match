document.addEventListener('DOMContentLoaded', function () {
    // Target the form by ID
    const form = document.getElementById('myForm');

    // Add a submit event listener to the form
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Prevent default form submission

        const formData = new FormData(form); // Collect form data

        fetch(form.action, { // Use the form's action URL
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // CSRF token
            },
            body: formData
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            console.log('Success:', data);
            alert('Form submitted successfully!'); // Feedback to the user
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});
