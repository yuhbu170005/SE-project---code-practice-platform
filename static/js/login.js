// login.js - Script for login page

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());

            // Convert to JSON for Node backend (Flask version used request.form, but this is cleaner)
            try {
                const res = await fetch("/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });
                const result = await res.json();

                if (result.success) {
                    window.location.href = "/";
                } else {
                    document.getElementById("alert-box").innerHTML = `
                        <div class="alert alert-danger">${result.message}</div>
                    `;
                }
            } catch (err) {
                console.error(err);
            }
        });
    }
});

