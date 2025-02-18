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
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to all delete buttons
    document.querySelectorAll('.delete-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            if (confirm('Are you sure you want to delete this item?')) {
                deleteItem(itemId);
            }
        });
    });
});

function deleteItem(itemId) {
    fetch(`/registry/item/${itemId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            // Remove the table row
            const row = document.querySelector(`[data-item-id="${itemId}"]`).closest('tr');
            row.remove();

            // If no items left, show the "no items" message
            const tbody = document.querySelector('tbody');
            if (!tbody.children.length) {
                const registryItems = document.querySelector('.registry-items');
                registryItems.innerHTML = `
                    <div class="alert alert-info">
                        No items in your registry yet. Add your first item using the form.
                    </div>`;
            }
        } else {
            throw new Error('Failed to delete item');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting item. Please try again.');
    });
}