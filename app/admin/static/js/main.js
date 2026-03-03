document.addEventListener('DOMContentLoaded', function() {
    const modals = document.querySelectorAll('.modal');
    const modalCloses = document.querySelectorAll('.modal-close');
    
    modalCloses.forEach(btn => {
        btn.addEventListener('click', () => {
            modals.forEach(m => m.classList.remove('show'));
        });
    });
    
    modals.forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    window.openModal = function(modalId) {
        document.getElementById(modalId).classList.add('show');
    };
    
    window.closeModal = function(modalId) {
        document.getElementById(modalId).classList.remove('show');
    };
});

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
    }
    return response.json();
}

async function toggleUserStatus(userId, currentStatus) {
    try {
        await apiRequest(`/api/users/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify({ is_active: !currentStatus }),
        });
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function deleteGroup(groupId) {
    if (!confirm('Are you sure you want to delete this group?')) return;
    try {
        await apiRequest(`/api/groups/${groupId}`, { method: 'DELETE' });
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function deleteMenuItem(itemId) {
    if (!confirm('Are you sure you want to delete this menu item?')) return;
    try {
        await apiRequest(`/api/menu/${itemId}`, { method: 'DELETE' });
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function sendMailing(mailingId, groupId = null, allUsers = false) {
    try {
        await apiRequest(`/api/mailings/${mailingId}/send`, {
            method: 'POST',
            body: JSON.stringify({ group_id: groupId, all_users: allUsers }),
        });
        alert('Mailing started!');
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function createGroup() {
    const name = document.getElementById('groupName').value;
    if (!name) return alert('Please enter group name');
    
    try {
        await apiRequest('/api/groups/', {
            method: 'POST',
            body: JSON.stringify({ name }),
        });
        closeModal('groupModal');
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function createMenuItem() {
    const name = document.getElementById('menuName').value;
    const url = document.getElementById('menuUrl').value;
    const position = parseInt(document.getElementById('menuPosition').value) || 0;
    
    if (!name) return alert('Please enter menu item name');
    
    try {
        await apiRequest('/api/menu/', {
            method: 'POST',
            body: JSON.stringify({ name, url: url || null, position }),
        });
        closeModal('menuModal');
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

async function createMailing() {
    const title = document.getElementById('mailingTitle').value;
    const content = document.getElementById('mailingContent').value;
    const mediaPath = document.getElementById('mailingMedia').value;
    const buttonsJson = document.getElementById('mailingButtons').value;
    
    if (!title || !content) return alert('Please fill required fields');
    
    try {
        await apiRequest('/api/mailings/', {
            method: 'POST',
            body: JSON.stringify({
                title,
                content,
                media_path: mediaPath || null,
                buttons_json: buttonsJson || null,
            }),
        });
        closeModal('mailingModal');
        location.reload();
    } catch (e) {
        alert('Error: ' + e.message);
    }
}

function filterUsers() {
    const source = document.getElementById('filterSource').value;
    const status = document.getElementById('filterStatus').value;
    const search = document.getElementById('searchUsers').value;
    
    const params = new URLSearchParams();
    if (source) params.append('source', source);
    if (status) params.append('is_active', status);
    if (search) params.append('search', search);
    
    window.location.href = `/users?${params.toString()}`;
}
