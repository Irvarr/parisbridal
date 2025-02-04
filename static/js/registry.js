// Social sharing functions
function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
}

function shareOnWhatsApp() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent("Check out my wedding registry!");
    window.open(`https://wa.me/?text=${text}%20${url}`, '_blank');
}

function copyLink() {
    navigator.clipboard.writeText(window.location.href)
        .then(() => {
            alert('Registry link copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy link:', err);
        });
}

// Registry item management
function deleteItem(itemId) {
    if (confirm('Are you sure you want to delete this item?')) {
        fetch(`/registry/item/${itemId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error deleting item');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting item');
        });
    }
}
