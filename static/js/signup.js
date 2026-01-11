// signup.js - Script for signup page

document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());

            try {
                const res = await fetch("/api/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data),
                });
                const result = await res.json();

                if (result.success) {
                    Swal.fire({
                        icon: "success",
                        title: "Success",
                        text: "Account created successfully!",
                        showConfirmButton: false,
                        timer: 1500,
                    }).then(() => (window.location.href = "/login"));
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

