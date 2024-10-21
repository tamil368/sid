document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("signup-form");
    
    form.addEventListener("submit", function (event) {
        const name = document.getElementById("name").value.trim();
        const email = document.getElementById("email").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const password = document.getElementById("password").value.trim();
        const confirmPassword = document.getElementById("confirm_password").value.trim();

        // Regular expression for email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phoneRegex = /^\d{10}$/; // Assuming a 10-digit phone number

        if (!name) {
            alert("Please enter your name.");
            event.preventDefault();
            return false;
        }

        if (!email || !emailRegex.test(email)) {
            alert("Please enter a valid email address.");
            event.preventDefault();
            return false;
        }

        if (!phone || !phoneRegex.test(phone)) {
            alert("Please enter a valid 10-digit phone number.");
            event.preventDefault();
            return false;
        }

        if (password.length < 6) {
            alert("Password must be at least 6 characters.");
            event.preventDefault();
            return false;
        }

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            event.preventDefault();
            return false;
        }

        return true;
    });
});
