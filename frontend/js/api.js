/**
 * CivicIntel AI - API Service Layer
 * Centralized HTTP Client connecting frontend to FastAPI backend.
 */

const API_BASE_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : window.location.origin;

class CivicIntelAPI {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, { ...options, headers });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const message = errorData.detail || errorData.message || `HTTP Error ${response.status}: ${response.statusText}`;
                throw new Error(message);
            }
            return await response.json();
        } catch (err) {
            console.error(`API Error on ${endpoint}:`, err);
            throw err;
        }
    }

    // Health Check
    static async checkHealth() {
        return this.request("/health");
    }

    // Citizen Requests
    static async submitRequest(requestText, location) {
        return this.request("/requests", {
            method: "POST",
            body: JSON.stringify({
                request_text: requestText,
                location: location
            })
        });
    }

    static async getRequests(filters = {}) {
        const query = new URLSearchParams();
        if (filters.search) query.append("search", filters.search);
        if (filters.category && filters.category !== "all") query.append("category", filters.category);
        if (filters.severity && filters.severity !== "all") query.append("severity", filters.severity);
        if (filters.language && filters.language !== "all") query.append("language", filters.language);
        if (filters.location && filters.location !== "all") query.append("location", filters.location);
        if (filters.limit) query.append("limit", filters.limit);

        const qs = query.toString();
        return this.request(`/requests${qs ? '?' + qs : ''}`);
    }

    static async getRequestById(id) {
        return this.request(`/requests/${id}`);
    }

    // Analytics
    static async getSummary() {
        return this.request("/analytics/summary");
    }

    static async getCategories() {
        return this.request("/analytics/categories");
    }

    static async getLanguages() {
        return this.request("/analytics/languages");
    }

    static async getLocations() {
        return this.request("/analytics/locations");
    }

    static async getInfrastructureComparison() {
        return this.request("/analytics/comparison");
    }

    // Hotspots
    static async getHotspots() {
        return this.request("/hotspots");
    }

    static async getHotspotDetail(location) {
        return this.request(`/hotspots/${encodeURIComponent(location)}`);
    }
}

window.CivicIntelAPI = CivicIntelAPI;
