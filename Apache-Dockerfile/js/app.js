const form = document.querySelector(".contact-form");

if (form) {
    form.addEventListener("submit", function (event) {
        event.preventDefault();

        alert("Contact form submitted! We can connect this to a backend next.");
        form.reset();
    });
}
