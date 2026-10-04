/**
 * Self-contained admin dashboard controller. It uses no implicit DOM globals
 * and all dynamically rendered actions use delegated event handlers.
 */
(() => {
    "use strict";

    const API = { stats: "/admin/stats", status: "/admin/status", encounters: "/admin/encounters/", users: "/admin/users/" };
    const POLL_INTERVAL_MS = 15_000;
    const escapeHtml = (value) => String(value ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    const formatTime = (value) => {
        const date = new Date(value);
        return !value || Number.isNaN(date.getTime()) ? "" : new Intl.DateTimeFormat(undefined, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" }).format(date);
    };
    async function request(url, options = {}) {
        const response = await fetch(url, { credentials: "same-origin", headers: { Accept: "application/json", ...options.headers }, ...options });
        if (!response.ok) throw new Error(`${options.method || "GET"} ${url} failed (${response.status})`);
        return response.status === 204 ? null : response.json();
    }
    function init() {
        const el = {
            total: document.getElementById("stat-total"), participants: document.getElementById("stat-participants"), letter: document.getElementById("stat-letter"),
            users: document.getElementById("users-container"), feed: document.getElementById("encounter-feed"), modal: document.getElementById("card-modal"),
            photo: document.getElementById("card-modal-photo-container"), title: document.getElementById("card-modal-title"), description: document.getElementById("card-modal-desc"), time: document.getElementById("card-modal-time"),
            statusButton: document.getElementById("btn-toggle-status"), statusIcon: document.getElementById("icon-status"), statusText: document.getElementById("text-status"),
            registrationButton: document.getElementById("btn-toggle-reg"), registrationIcon: document.getElementById("icon-reg"), registrationText: document.getElementById("text-reg"),
            close: document.getElementById("btn-close-modal"), deleteEncounter: document.getElementById("btn-delete-record"),
        };
        if (["total", "participants", "letter", "users", "feed", "modal", "statusButton", "registrationButton"].some((key) => !el[key])) {
            console.warn("FaceBingo admin panel was not initialized: required markup is missing.");
            return;
        }
        const state = { recent: [], selectedEncounterId: null, submissionsActive: true, registrationRequired: true };
        const renderStatus = () => {
            el.statusButton.className = state.submissionsActive ? "btn btn--danger" : "btn btn--primary";
            el.statusIcon.textContent = state.submissionsActive ? "pause_circle" : "play_circle";
            el.statusText.textContent = state.submissionsActive ? "Pause Submissions" : "Resume Submissions";
            el.registrationButton.className = state.registrationRequired ? "btn btn--secondary" : "btn btn--ghost";
            el.registrationIcon.textContent = state.registrationRequired ? "lock" : "lock_open";
            el.registrationText.textContent = state.registrationRequired ? "Registration Required" : "Registration Optional";
        };
        const renderUsers = (users) => {
            el.users.innerHTML = users.length ? users.map((user) => {
                const bio = user.additional_metadata?.bio || "No bio";
                return `<article class="stat-card"><div class="admin-card-heading"><strong>${escapeHtml(user.name)}</strong><button class="btn btn--danger btn--sm" type="button" data-delete-user="${escapeHtml(user.id)}">Delete</button></div><p>${escapeHtml(bio)}</p><small>Registered: ${escapeHtml(formatTime(user.created_at))}</small></article>`;
            }).join("") : '<p class="empty-state">No users registered yet.</p>';
        };
        const renderFeed = (rows) => {
            el.feed.innerHTML = rows.length ? rows.map((row, index) => `<button class="encounter-card admin-encounter-card" type="button" data-encounter-index="${index}">${row.photo_url ? `<img class="encounter-card__photo" src="${escapeHtml(row.photo_url)}" alt="Encounter photo" loading="lazy">` : ""}<span class="encounter-card__body"><strong>${escapeHtml(row.submitter_name)} → ${escapeHtml(row.met_name)}</strong><span>${escapeHtml(row.thought)}</span><small>${escapeHtml(formatTime(row.created_at))}</small></span></button>`).join("") : '<p class="empty-state">No encounters yet.</p>';
        };
        const openEncounter = (row) => {
            if (!row) return;
            state.selectedEncounterId = row.id || null;
            el.photo.innerHTML = row.photo_url ? `<img src="${escapeHtml(row.photo_url)}" alt="Encounter photo">` : '<span class="icon icon--xl">photo_camera</span>';
            el.title.textContent = `${row.submitter_name || "Unknown"} → ${row.met_name || "Unknown"}`;
            el.description.textContent = row.thought || "";
            el.time.textContent = formatTime(row.created_at);
            el.modal.classList.add("active");
        };
        const loadStats = async () => {
            try {
                const data = await request(API.stats);
                state.recent = Array.isArray(data.recent) ? data.recent : [];
                el.total.textContent = data.total_encounters ?? "—"; el.participants.textContent = data.unique_participants ?? "—"; el.letter.textContent = data.most_active_letter ?? "—";
                renderUsers(Array.isArray(data.users) ? data.users : []); renderFeed(state.recent);
            } catch (error) { console.error("Unable to load admin statistics.", error); el.feed.innerHTML = '<p class="empty-state">Unable to load the dashboard.</p>'; }
        };
        const loadStatus = async () => {
            try { const data = await request(API.status); state.submissionsActive = Boolean(data.active); state.registrationRequired = Boolean(data.registration_required); renderStatus(); }
            catch (error) { console.error("Unable to load event status.", error); }
        };
        const updateStatus = async (payload) => {
            try { const data = await request(API.status, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); state.submissionsActive = Boolean(data.active); state.registrationRequired = Boolean(data.registration_required); renderStatus(); }
            catch (error) { console.error("Unable to update event status.", error); window.alert("The event status could not be updated."); }
        };
        el.statusButton.addEventListener("click", () => updateStatus({ active: !state.submissionsActive }));
        el.registrationButton.addEventListener("click", () => updateStatus({ registration_required: !state.registrationRequired }));
        el.close?.addEventListener("click", () => el.modal.classList.remove("active"));
        el.modal.addEventListener("click", (event) => { if (event.target === el.modal) el.modal.classList.remove("active"); });
        el.feed.addEventListener("click", (event) => { const card = event.target.closest("[data-encounter-index]"); if (card) openEncounter(state.recent[Number(card.dataset.encounterIndex)]); });
        el.users.addEventListener("click", async (event) => {
            const button = event.target.closest("[data-delete-user]");
            if (!button || !window.confirm("Delete this registered user?")) return;
            try { await request(`${API.users}${encodeURIComponent(button.dataset.deleteUser)}`, { method: "DELETE" }); await loadStats(); }
            catch (error) { console.error("Unable to delete user.", error); window.alert("The user could not be deleted."); }
        });
        el.deleteEncounter?.addEventListener("click", async () => {
            if (!state.selectedEncounterId || !window.confirm("Delete this encounter?")) return;
            try { await request(`${API.encounters}${encodeURIComponent(state.selectedEncounterId)}`, { method: "DELETE" }); el.modal.classList.remove("active"); await loadStats(); }
            catch (error) { console.error("Unable to delete encounter.", error); window.alert("The encounter could not be deleted."); }
        });
        loadStats(); loadStatus(); window.setInterval(loadStats, POLL_INTERVAL_MS);
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true }); else init();
})();
