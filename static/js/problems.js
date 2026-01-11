// problems.js - Script for problems list page

function navigateTo(url) {
    window.location.href = url;
}

function confirmDelete(problemId) {
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch("/problems/delete/" + problemId, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    Swal.fire('Deleted!', data.message, 'success').then(() => {
                        window.location.reload();
                    });
                } else {
                    Swal.fire('Error!', data.message, 'error');
                }
            })
            .catch(err => {
                Swal.fire('Error!', 'Failed to delete problem.', 'error');
            });
        }
    })
}

// Logic Dropdown
function toggleTagDropdown() {
    document.getElementById("tagDropdownContent").classList.toggle("show");
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Đóng dropdown khi click ra ngoài
    window.addEventListener('click', function(e) {
        const dropdown = document.getElementById('tagDropdown');
        const content = document.getElementById('tagDropdownContent');
        
        if (!dropdown.contains(e.target)) {
            if (content.classList.contains('show')) {
                content.classList.remove('show');
            }
        }
    });
});

