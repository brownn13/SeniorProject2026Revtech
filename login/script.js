document.getElementById("loginForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorMessage = document.getElementById("errorMessage");

    if (email === "" || password === "") {
        errorMessage.textContent = "Please fill in all fields.";
        return;
    }

    // Example validation (replace with real backend authentication)
    if (email === "user@example.com" && password === "password123") {
        alert("Login successful!");
        window.location.href = "/login/dashboard.html"; // redirect
    } else {
        errorMessage.textContent = "Invalid email or password.";
    }
});
