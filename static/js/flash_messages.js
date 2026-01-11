// flash_messages.js - Script for flash messages
// This file will be used to display flash messages from the server
// The actual message data is passed via data attributes or inline script in base.html

function showFlashMessages(messages) {
    if (!messages || messages.length === 0) return;
    
    messages.forEach(function(messageData) {
        const category = messageData.category || 'info';
        const message = messageData.message || '';
        
        const icon = category === 'success' ? 'success' : (category === 'danger' ? 'error' : 'info');
        const title = category === 'success' ? 'Success!' : (category === 'danger' ? 'Error!' : 'Notice');
        
        Swal.fire({
            icon: icon,
            title: title,
            text: message,
            timer: 3000,
            showConfirmButton: false,
            toast: true,
            position: 'top-end'
        });
    });
}

