$(document).ready(function () {
    // Custom method to check if passwords match
    $.validator.addMethod("passwordMatch", function (value, element) {
        return $('#password').val() === $('#confirm_password').val();
    }, "Passwords do not match.");

    // Form validation
    $("#signup-form").validate({
        rules: {
            name: {
                required: true,
                minlength: 3
            },
            email: {
                required: true,
                email: true
            },
            phone: {
                required: true,
                digits: true,
                minlength: 10,
                maxlength: 10
            },
            password: {
                required: true,
                minlength: 6
            },
            confirm_password: {
                required: true,
                passwordMatch: true
            }
        },
        messages: {
            name: {
                required: "Please enter your name",
                minlength: "Name must be at least 3 characters long"
            },
            email: {
                required: "Please enter your email",
                email: "Please enter a valid email address"
            },
            phone: {
                required: "Please enter your phone number",
                digits: "Please enter only digits",
                minlength: "Phone number must be exactly 10 digits",
                maxlength: "Phone number must be exactly 10 digits"
            },
            password: {
                required: "Please provide a password",
                minlength: "Password must be at least 6 characters long"
            },
            confirm_password: {
                required: "Please confirm your password",
                passwordMatch: "Passwords do not match"
            }
        },
        submitHandler: function (form) {
            // Collect form data to display in the alert box
            var name = $('#name').val();
            var email = $('#email').val();
            var phone = $('#phone').val();
            var password = $('#password').val();

            // Create the alert box with the form data
            alert("Form is valid!\n\n" +
                  "Name: " + name + "\n" +
                  "Email: " + email + "\n" +
                  "Phone: " + phone + "\n" +
                  "Password: " + password + "\n");

            // After the alert box, you can submit the form
            form.submit();
        }
    });
});
