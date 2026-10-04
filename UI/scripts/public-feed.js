/** Public, read-only live feed. */
(() => {
    "use strict";

    const API_URL = "/admin/stats";
    const REFRESH_INTERVAL_MS = 15000;
    const EMPTY_STATE = '<p class="empty-state">No encounters yet.</p>';
    const ERROR_STATE = '<p class="empty-state">The live feed is temporarily unavailable.</p>';

    const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }[char]));

    const normalizeNumber = (value) => {
        if (value === null || value === undefined || value === "") {
            return "-";
        }

        const parsed = Number(value);
        return Number.isFinite(parsed) ? String(parsed) : "-";
    };

    const normalizeRows = (rows) => (Array.isArray(rows) ? rows : []);

    function validateStatsPayload(payload) {
        if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
            throw new Error("Stats response was not an object.");
        }

        if (payload.recent !== undefined && !Array.isArray(payload.recent)) {
            throw new Error("Stats response recent field was not an array.");
        }

        return {
            totalEncounters: normalizeNumber(payload.total_encounters),
            uniqueParticipants: normalizeNumber(payload.unique_participants),
            recent: normalizeRows(payload.recent),
        };
    }

    async function requestStats() {
        const response = await fetch(API_URL, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
        });

        if (!response.ok) {
            throw new Error(`Stats request failed with ${response.status}.`);
        }

        const contentType = response.headers.get("content-type") || "";
        if (!contentType.includes("application/json")) {
            throw new Error("Stats response was not JSON.");
        }

        return validateStatsPayload(await response.json());
    }

    function renderFeed(feed, rows) {
        feed.innerHTML = rows.length ? rows.map((row) => `
            <article class="encounter-card">
                ${row.photo_url ? `<img class="encounter-card__photo" src="${escapeHtml(row.photo_url)}" alt="Encounter photo" loading="lazy">` : ""}
                <div>
                    <strong>${escapeHtml(row.submitter_name)} met ${escapeHtml(row.met_name)}</strong>
                    <p>${escapeHtml(row.thought)}</p>
                </div>
            </article>
        `).join("") : EMPTY_STATE;
    }

    function init() {
        const elements = {
            feed: document.getElementById("encounter-feed"),
            total: document.getElementById("stat-total"),
            participants: document.getElementById("stat-participants"),
        };

        if (!elements.feed || !elements.total || !elements.participants) {
            console.warn("Public feed markup is incomplete; live feed was not initialized.");
            return;
        }

        async function load() {
            try {
                const stats = await requestStats();
                elements.total.textContent = stats.totalEncounters;
                elements.participants.textContent = stats.uniqueParticipants;
                renderFeed(elements.feed, stats.recent);
            } catch (error) {
                console.error("Unable to load public live feed.", error);
                elements.total.textContent = "-";
                elements.participants.textContent = "-";
                elements.feed.innerHTML = ERROR_STATE;
            }
        }

        load();
        window.setInterval(load, REFRESH_INTERVAL_MS);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
        init();
    }
})();
