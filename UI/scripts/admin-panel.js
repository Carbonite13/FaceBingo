/* Admin stats poller */
let recentData = [];
let currentRecordId = null;
let submissionsActive = true;
let registrationRequired = true;

function createEncounterCard(row, index) {
    return `
          <div class="encounter-card" style="cursor:pointer;" onclick="openCardModal(${index})">
            ${row.photo_url
            ? `<img class="encounter-card__photo" src="${escHtml(row.photo_url)}" alt="Photo" loading="lazy" />`
            : `<div class="encounter-card__photo"><span class="icon icon--xl">photo_camera</span></div>`
        }
            <div class="encounter-card__body">
              <div class="encounter-card__names">
                <span class="encounter-card__letter">${escHtml(row.letter)}</span>
                ${escHtml(row.submitter_name)}
                <span class="icon icon--sm" style="color:var(--clr-muted)">arrow_forward</span>
                ${escHtml(row.met_name)}
              </div>
              <p class="encounter-card__thought">${escHtml(row.thought)}</p>
              <div class="encounter-card__time">${formatTime(row.created_at)}</div>
            </div>
          </div>
        `;
}

async function loadStats() {
    try {
        const res = await fetch('/admin/stats', {
            headers: { 'Accept': 'application/json' },
            credentials: 'same-origin',
        });
        if (!res.ok) return;
        const data = await res.json();

        recentData = data.recent || [];

        // Update stat cards
        document.getElementById('stat-total').textContent = data.total_encounters ?? '—';
        document.getElementById('stat-participants').textContent = data.unique_participants ?? '—';
        document.getElementById('stat-letter').textContent = data.most_active_letter ?? '—';

        // Render users
        renderUsers(data.users || []);

        // Render encounter feed
        const feed = document.getElementById('encounter-feed');
        if (recentData.length === 0) {
            feed.innerHTML = '<p style="color:var(--clr-muted);font-size:var(--text-sm);">No encounters yet.</p>';
            return;
        }

        feed.innerHTML = recentData.map((row, index) => createEncounterCard(row, index)).join('');
    } catch (e) {
        console.warn('Stats fetch failed', e);
    }
}

function openCardModal(index) {
    const row = recentData[index];
    if (!row) return;
    currentRecordId = row.id;

    const photoContainer = document.getElementById('card-modal-photo-container');
    if (row.photo_url) {
        photoContainer.innerHTML = `<img src="${escHtml(row.photo_url)}" alt="Photo" style="width:100%;height:100%;object-fit:cover;" />`;
    } else {
        photoContainer.innerHTML = `<span class="icon icon--xl" style="color:var(--clr-muted);font-size:3rem;">photo_camera</span>`;
    }

    document.getElementById('card-modal-title').innerHTML = `
            <span class="encounter-card__letter" style="display:inline-flex;align-items:center;justify-content:center;width:1.8rem;height:1.8rem;background:var(--clr-primary);border-radius:var(--radius-sm);font-size:var(--text-sm);font-weight:700;color:var(--clr-text);">${escHtml(row.letter)}</span>
            ${escHtml(row.submitter_name)} <span class="icon icon--sm" style="color:var(--clr-muted)">arrow_forward</span> ${escHtml(row.met_name)}
        `;
    document.getElementById('card-modal-desc').textContent = row.thought || '';
    document.getElementById('card-modal-time').textContent = formatTime(row.created_at);

    document.getElementById('card-modal').classList.add('active');
}

function escHtml(str) {
    return String(str ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

function renderUsers(users) {
    const container = document.getElementById('users-container');
    if (users.length === 0) {
        container.innerHTML = '<div class="empty-state">No users registered yet.</div>';
        return;
    }
    container.innerHTML = users.map(u => {
        const bio = (u.additional_metadata && u.additional_metadata.bio) ? escHtml(u.additional_metadata.bio) : 'No bio';
        return `
          <div class="stat-card fade-up">
            <div style="font-weight: 600; font-size: 1.2rem; color: var(--clr-primary-dk); margin-bottom: var(--sp-1); display: flex; justify-content: space-between; align-items: center;">
              <span>${escHtml(u.name)}</span>
              <button class="btn btn--danger btn--sm" aria-label="Delete User" onclick="deleteUser('${u.id}')" title="Delete User">
                <span class="icon icon--sm">delete</span>
              </button>
            </div>
            <div style="color: var(--clr-text-2); font-size: 0.95rem;">${bio}</div>
            <div style="color: var(--clr-muted); font-size: 0.8rem; margin-top: var(--sp-2);">Registered: ${formatTime(u.created_at)}</div>
          </div>
        `;
    }).join('');
}

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;
    try {
        const res = await fetch(`/admin/users/${id}`, { method: 'DELETE', credentials: 'same-origin' });
        const data = await res.json();
        if (data.success) loadStats();
    } catch (e) {
        console.error('Failed to delete user', e);
    }
}

async function loadStatus() {
    try {
        const res = await fetch('/admin/status', { credentials: 'same-origin' });
        if (res.ok) {
            const data = await res.json();
            submissionsActive = data.active;
            registrationRequired = data.registration_required;
            updateStatusUI();
        }
    } catch (e) { console.error('Failed to load status', e); }
}

async function toggleSubmissions() {
    try {
        const res = await fetch('/admin/status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ active: !submissionsActive })
        });
        if (res.ok) {
            const data = await res.json();
            submissionsActive = data.active;
            updateStatusUI();
        }
    } catch (e) { console.error('Failed to toggle status', e); }
}

async function toggleRegistration() {
    try {
        const res = await fetch('/admin/status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ registration_required: !registrationRequired })
        });
        if (res.ok) {
            const data = await res.json();
            registrationRequired = data.registration_required;
            updateStatusUI();
        }
    } catch (e) { console.error('Failed to toggle registration', e); }
}

function updateStatusUI() {
    const btnStatus = document.getElementById('btn-toggle-status');
    const iconStatus = document.getElementById('icon-status');
    const textStatus = document.getElementById('text-status');

    if (submissionsActive) {
        btnStatus.className = 'btn btn--danger';
        iconStatus.textContent = 'pause_circle';
        textStatus.textContent = 'Pause Submissions';
    } else {
        btnStatus.className = 'btn btn--primary';
        iconStatus.textContent = 'play_circle';
        textStatus.textContent = 'Resume Submissions';
    }

    const btnReg = document.getElementById('btn-toggle-reg');
    const iconReg = document.getElementById('icon-reg');
    const textReg = document.getElementById('text-reg');

    if (registrationRequired) {
        btnReg.className = 'btn btn--secondary';
        iconReg.textContent = 'lock';
        textReg.textContent = 'Registration Required';
    } else {
        btnReg.className = 'btn btn--ghost';
        iconReg.textContent = 'lock_open';
        textReg.textContent = 'Registration Optional';
    }
}

function formatTime(iso) {
    if (!iso) return '';
    try {
        return new Intl.DateTimeFormat(undefined, {
            hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short'
        }).format(new Date(iso));
    } catch { return iso; }
}

async function deleteRecord() {
    if (!currentRecordId) return;
    if (!confirm("Are you sure you want to delete this encounter?")) return;

    try {
        const res = await fetch(`/admin/encounters/${currentRecordId}`, {
            method: 'DELETE',
            credentials: 'same-origin', // sends Basic Auth
        });

        if (res.ok) {
            document.getElementById('card-modal').classList.remove('active');
            loadStats();
        } else {
            alert('Failed to delete record.');
        }
    } catch (e) {
        console.error(e);
        alert('An error occurred while deleting.');
    }
}

// Close modal if clicked outside content
document.getElementById('card-modal').addEventListener('click', function (e) {
    if (e.target === this) {
        this.classList.remove('active');
    }
});

// Initial load + poll every 15 s
loadStats();
loadStatus();
setInterval(loadStats, 15_000);