/**
 * Leaflet.js Interactive Hotspot Map Module for CivicIntel AI
 * Grounded in OpenStreetMap cartography.
 */

const CivicMap = {
    map: null,
    markersLayer: null,

    init(elementId = "map") {
        const mapEl = document.getElementById(elementId);
        if (!mapEl) return;

        // Centered around Tamil Nadu demonstration region
        this.map = L.map(elementId, {
            center: [10.8505, 78.7047],
            zoom: 7,
            scrollWheelZoom: false
        });

        // OpenStreetMap Tile Layer
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | CivicIntel AI Demo'
        }).addTo(this.map);

        this.markersLayer = L.layerGroup().addTo(this.map);
    },

    renderHotspots(hotspots, onSelectHotspotCallback = null) {
        if (!this.map || !this.markersLayer) return;

        this.markersLayer.clearLayers();

        const bounds = [];

        hotspots.forEach(h => {
            if (!h.latitude || !h.longitude) return;

            const lat = h.latitude;
            const lng = h.longitude;
            bounds.push([lat, lng]);

            // Color coding based on Civic Need Index
            let pinColor = "#10b981"; // Low Need
            let tierClass = "badge-cni-tier3";
            let tierLabel = "Monitoring Tier";

            if (h.civic_need_index >= 70) {
                pinColor = "#dc2626"; // High Hotspot
                tierClass = "badge-cni-tier1";
                tierLabel = "Tier 1 Priority Hotspot";
            } else if (h.civic_need_index >= 40) {
                pinColor = "#d97706"; // Moderate Hotspot
                tierClass = "badge-cni-tier2";
                tierLabel = "Tier 2 Priority Hotspot";
            }

            // Circle marker with pulsing radius
            const marker = L.circleMarker([lat, lng], {
                radius: Math.min(18, Math.max(9, h.civic_need_index / 4.5)),
                fillColor: pinColor,
                color: "#ffffff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.85
            });

            // Interactive popup
            const popupHtml = `
                <div class="map-popup-card">
                    <div class="map-popup-title">${h.location}</div>
                    <span class="badge ${tierClass} map-popup-badge">${tierLabel}</span>
                    <div class="map-popup-row">
                        <span>Civic Need Index:</span>
                        <strong>${h.civic_need_index.toFixed(1)} / 100</strong>
                    </div>
                    <div class="map-popup-row">
                        <span>Reported Requests:</span>
                        <strong>${h.request_count}</strong>
                    </div>
                    <div class="map-popup-row">
                        <span>Affected Population:</span>
                        <strong>${h.affected_people.toLocaleString()}</strong>
                    </div>
                    <div class="map-popup-row">
                        <span>Dominant Need:</span>
                        <strong>${h.dominant_category}</strong>
                    </div>
                    <div style="margin-top: 8px;">
                        <button class="btn-secondary" style="width: 100%; padding: 4px 8px; font-size: 0.75rem;" onclick="window.inspectHotspot('${h.location}')">
                            🔍 Inspect Intelligence
                        </button>
                    </div>
                </div>
            `;

            marker.bindPopup(popupHtml);
            marker.on("click", () => {
                if (onSelectHotspotCallback) {
                    onSelectHotspotCallback(h);
                }
            });

            this.markersLayer.addLayer(marker);
        });

        if (bounds.length > 0) {
            this.map.fitBounds(bounds, { padding: [40, 40] });
        }
    }
};

window.CivicMap = CivicMap;
