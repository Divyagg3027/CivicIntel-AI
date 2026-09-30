/**
 * CivicIntel AI - Main Dashboard Controller
 * Synchronizes real-time metrics, dynamic filtering, charts, maps, and hotspot intelligence modals.
 */

let allHotspotsData = [];

document.addEventListener("DOMContentLoaded", async () => {
    initDashboard();
});

async function initDashboard() {
    // 1. Initialize Map
    CivicMap.init("map");

    // 2. Setup Filter Event Listeners
    setupFilters();

    // 3. Setup Modal Close Handlers
    setupModals();

    // 4. Fetch and Render Live Data
    await refreshDashboard();
}

async function refreshDashboard() {
    try {
        setLoadingState(true);

        // Parallel data loading
        const [summary, categories, languages, locations, hotspots, comparison] = await Promise.all([
            CivicIntelAPI.getSummary().catch(e => null),
            CivicIntelAPI.getCategories().catch(e => []),
            CivicIntelAPI.getLanguages().catch(e => []),
            CivicIntelAPI.getLocations().catch(e => []),
            CivicIntelAPI.getHotspots().catch(e => []),
            CivicIntelAPI.getInfrastructureComparison().catch(e => null)
        ]);

        // 1. Render Summary KPIs
        if (summary) {
            document.getElementById("kpiTotalRequests").textContent = summary.total_requests.toLocaleString();
            document.getElementById("kpiHighSeverity").textContent = summary.high_severity.toLocaleString();
            document.getElementById("kpiAffectedPeople").textContent = summary.total_affected_people.toLocaleString();
            document.getElementById("kpiHotspots").textContent = hotspots ? hotspots.length : 0;
        }

        // 2. Render Charts
        if (categories && categories.length > 0) {
            CivicCharts.renderCategories(categories);
        }

        if (summary) {
            CivicCharts.renderSeverities(summary);
        }

        if (languages && languages.length > 0) {
            CivicCharts.renderLanguages(languages);
        }

        if (locations && locations.length > 0) {
            CivicCharts.renderLocations(locations);
        }

        if (comparison && comparison.comparison) {
            CivicCharts.renderComparison(comparison.comparison);
        }

        // 3. Render Hotspots Table & Map
        if (hotspots && hotspots.length > 0) {
            allHotspotsData = hotspots;
            renderHotspotsTable(hotspots);
            CivicMap.renderHotspots(hotspots, (hotspot) => {
                showHotspotModal(hotspot);
            });
            populateLocationFilter(hotspots);
        }

        // 4. Render Requests Table with active filters
        await applyFiltersAndLoadRequests();

    } catch (err) {
        console.error("Dashboard initial load failed:", err);
        showBannerError(`Failed to connect to CivicIntel AI backend (${err.message}). Verify backend server is running.`);
    } finally {
        setLoadingState(false);
    }
}

function renderHotspotsTable(hotspots) {
    const tbody = document.getElementById("hotspotsTableBody");
    if (!tbody) return;

    tbody.innerHTML = "";

    hotspots.forEach((h, idx) => {
        let badgeClass = "badge-cni-tier3";
        let tierLabel = "Monitoring";

        if (h.civic_need_index >= 70) {
            badgeClass = "badge-cni-tier1";
            tierLabel = "Tier 1 Priority";
        } else if (h.civic_need_index >= 40) {
            badgeClass = "badge-cni-tier2";
            tierLabel = "Tier 2 Need";
        }

        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>#${idx + 1}</strong></td>
            <td><strong>${h.location}</strong></td>
            <td><span class="badge ${badgeClass}">${h.civic_need_index.toFixed(1)} / 100</span></td>
            <td>${h.request_count}</td>
            <td>${h.affected_people.toLocaleString()}</td>
            <td><span class="badge badge-neutral">${h.dominant_category}</span></td>
            <td>${h.infrastructure_gap ? h.infrastructure_gap.toFixed(1) : 0.0} / 100</td>
            <td>
                <button class="btn-secondary" style="padding: 4px 10px; font-size: 0.8rem;" onclick="inspectHotspot('${h.location}')">
                    Inspect Intelligence
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function populateLocationFilter(hotspots) {
    const locFilter = document.getElementById("locationFilter");
    if (!locFilter) return;

    const currentVal = locFilter.value;
    locFilter.innerHTML = '<option value="all">All Locations</option>';

    const locations = Array.from(new Set(hotspots.map(h => h.location))).sort();
    locations.forEach(loc => {
        const opt = document.createElement("option");
        opt.value = loc;
        opt.textContent = loc;
        if (loc === currentVal) opt.selected = true;
        locFilter.appendChild(opt);
    });
}

async function applyFiltersAndLoadRequests() {
    const searchVal = document.getElementById("searchInput")?.value.trim() || "";
    const categoryVal = document.getElementById("categoryFilter")?.value || "all";
    const severityVal = document.getElementById("severityFilter")?.value || "all";
    const languageVal = document.getElementById("languageFilter")?.value || "all";
    const locationVal = document.getElementById("locationFilter")?.value || "all";

    const tbody = document.getElementById("requestsTableBody");
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 20px;">Loading matching requests...</td></tr>';

    try {
        const requests = await CivicIntelAPI.getRequests({
            search: searchVal,
            category: categoryVal,
            severity: severityVal,
            language: languageVal,
            location: locationVal,
            limit: 100
        });

        tbody.innerHTML = "";

        if (requests.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center; padding: 25px; color: var(--text-muted);">No citizen requests matching the selected filters.</td></tr>';
            return;
        }

        requests.forEach(req => {
            const tr = document.createElement("tr");
            tr.style.cursor = "pointer";

            const dateStr = req.created_at ? new Date(req.created_at).toLocaleDateString() : "Recent";
            const sevBadge = `badge badge-${(req.severity || 'low').toLowerCase()}`;

            tr.innerHTML = `
                <td>#${req.id}</td>
                <td>${dateStr}</td>
                <td><strong>${req.location}</strong></td>
                <td style="max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${req.request_text}</td>
                <td><span class="badge badge-neutral">${req.category || 'Other'}</span></td>
                <td><span class="${sevBadge}">${req.severity || 'Low'}</span></td>
                <td>${req.affected_people ? req.affected_people.toLocaleString() : 0}</td>
                <td><span class="badge badge-neutral">${req.language || 'English'}</span></td>
            `;

            tr.addEventListener("click", () => {
                showRequestModal(req);
            });

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Filter request loading failed:", err);
        tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--danger); padding: 20px;">Error loading requests: ${err.message}</td></tr>`;
    }
}

function setupFilters() {
    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const severityFilter = document.getElementById("severityFilter");
    const languageFilter = document.getElementById("languageFilter");
    const locationFilter = document.getElementById("locationFilter");
    const resetBtn = document.getElementById("resetFiltersBtn");
    const refreshBtn = document.getElementById("refreshBtn");

    let debounceTimer;
    searchInput?.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            applyFiltersAndLoadRequests();
        }, 300);
    });

    [categoryFilter, severityFilter, languageFilter, locationFilter].forEach(el => {
        el?.addEventListener("change", () => {
            applyFiltersAndLoadRequests();
        });
    });

    resetBtn?.addEventListener("click", () => {
        if (searchInput) searchInput.value = "";
        if (categoryFilter) categoryFilter.value = "all";
        if (severityFilter) severityFilter.value = "all";
        if (languageFilter) languageFilter.value = "all";
        if (locationFilter) locationFilter.value = "all";
        applyFiltersAndLoadRequests();
    });

    refreshBtn?.addEventListener("click", async () => {
        await refreshDashboard();
    });
}

function setupModals() {
    const hotspotModal = document.getElementById("hotspotModal");
    const requestModal = document.getElementById("requestModal");

    document.querySelectorAll(".modal-close").forEach(btn => {
        btn.addEventListener("click", () => {
            if (hotspotModal) hotspotModal.style.display = "none";
            if (requestModal) requestModal.style.display = "none";
        });
    });

    window.addEventListener("click", (e) => {
        if (e.target === hotspotModal) hotspotModal.style.display = "none";
        if (e.target === requestModal) requestModal.style.display = "none";
    });
}

// Global inspectHotspot function accessible from inline onclicks
window.inspectHotspot = function(locationName) {
    const found = allHotspotsData.find(h => h.location.toLowerCase() === locationName.toLowerCase());
    if (found) {
        showHotspotModal(found);
    }
};

function showHotspotModal(h) {
    const modal = document.getElementById("hotspotModal");
    if (!modal) return;

    document.getElementById("modalHotspotLocation").textContent = h.location;
    document.getElementById("modalHotspotCNI").textContent = `${h.civic_need_index.toFixed(1)} / 100`;
    document.getElementById("modalHotspotRequests").textContent = h.request_count;
    document.getElementById("modalHotspotPopulation").textContent = h.affected_people.toLocaleString();
    document.getElementById("modalHotspotCategory").textContent = h.dominant_category;
    document.getElementById("modalHotspotSeverity").textContent = `${h.severity_score.toFixed(1)} / 20`;
    document.getElementById("modalHotspotInfraGap").textContent = `${h.infrastructure_gap.toFixed(1)} / 100`;
    
    const invCr = (h.investment_amount || h.investment_context || 0) / 10000000.0;
    document.getElementById("modalHotspotInvestment").textContent = `₹${invCr.toFixed(1)} Cr`;

    document.getElementById("modalHotspotExplanation").textContent = h.explanation || "No narrative insight generated.";

    if (h.category_breakdown && Object.keys(h.category_breakdown).length > 0) {
        CivicCharts.renderModalCategoryChart(h.category_breakdown);
    }

    modal.style.display = "flex";
}

function showRequestModal(req) {
    const modal = document.getElementById("requestModal");
    if (!modal) return;

    document.getElementById("modalReqId").textContent = `#${req.id}`;
    document.getElementById("modalReqLocation").textContent = req.location;
    document.getElementById("modalReqText").textContent = req.request_text;
    document.getElementById("modalReqCategory").textContent = req.category || "Other";
    
    const sevEl = document.getElementById("modalReqSeverity");
    sevEl.textContent = req.severity || "Low";
    sevEl.className = `badge badge-${(req.severity || 'low').toLowerCase()}`;

    document.getElementById("modalReqPeople").textContent = req.affected_people ? `${req.affected_people.toLocaleString()} residents` : "Not specified";
    document.getElementById("modalReqLanguage").textContent = req.language || "English";
    document.getElementById("modalReqNeed").textContent = req.detected_need || "Civic Support & Services";
    document.getElementById("modalReqStatus").textContent = req.status || "Analyzed";

    modal.style.display = "flex";
}

function setLoadingState(isLoading) {
    const refreshBtn = document.getElementById("refreshBtn");
    if (refreshBtn) {
        refreshBtn.disabled = isLoading;
        refreshBtn.textContent = isLoading ? "Syncing..." : "🔄 Refresh Data";
    }
}

function showBannerError(msg) {
    const banner = document.getElementById("errorBanner");
    if (banner) {
        banner.textContent = msg;
        banner.style.display = "block";
    }
}
