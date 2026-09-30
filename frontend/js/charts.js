/**
 * Chart.js Visualizations for CivicIntel AI
 */

const CivicCharts = {
    categoryChart: null,
    severityChart: null,
    languageChart: null,
    locationChart: null,
    comparisonChart: null,
    modalCategoryChart: null,

    // Category Distribution Chart
    renderCategories(categories) {
        const ctx = document.getElementById("categoryChartCanvas");
        if (!ctx) return;

        const labels = categories.map(c => c.category);
        const data = categories.map(c => c.count);

        if (this.categoryChart) this.categoryChart.destroy();

        this.categoryChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        "#2563eb", "#0ea5e9", "#10b981", "#f59e0b",
                        "#8b5cf6", "#ec4899", "#f97316", "#64748b", "#14b8a6"
                    ],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.raw} requests`
                        }
                    }
                },
                cutout: "62%"
            }
        });
    },

    // Severity Breakdown Chart
    renderSeverities(summary) {
        const ctx = document.getElementById("severityChartCanvas");
        if (!ctx) return;

        const labels = ["High Severity", "Medium Severity", "Low Severity"];
        const data = [summary.high_severity || 0, summary.medium_severity || 0, summary.low_severity || 0];

        if (this.severityChart) this.severityChart.destroy();

        this.severityChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ["#dc2626", "#d97706", "#059669"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "right", labels: { boxWidth: 12, font: { size: 11 } } },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.raw} requests`
                        }
                    }
                }
            }
        });
    },

    // Language Distribution Chart
    renderLanguages(languages) {
        const ctx = document.getElementById("languageChartCanvas");
        if (!ctx) return;

        const labels = languages.map(l => l.language);
        const data = languages.map(l => l.count);

        if (this.languageChart) this.languageChart.destroy();

        this.languageChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Requests",
                    data: data,
                    backgroundColor: "#2563eb",
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: "#f1f5f9" } },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // Requests by Location
    renderLocations(locations) {
        const ctx = document.getElementById("locationChartCanvas");
        if (!ctx) return;

        const topLocs = locations.slice(0, 8);
        const labels = topLocs.map(l => l.location);
        const data = topLocs.map(l => l.count);

        if (this.locationChart) this.locationChart.destroy();

        this.locationChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Requests",
                    data: data,
                    backgroundColor: "#0ea5e9",
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { beginAtZero: true, grid: { color: "#f1f5f9" } },
                    y: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // Comparative Intelligence Chart (Reported Need vs Demonstration Infrastructure Score vs Investment)
    renderComparison(comparisonList) {
        const ctx = document.getElementById("comparisonChartCanvas");
        if (!ctx) return;

        const labels = comparisonList.map(c => c.category);
        const needScores = comparisonList.map(c => c.reported_need_score);
        const infraScores = comparisonList.map(c => c.infrastructure_score);
        const invScores = comparisonList.map(c => c.investment_score);

        if (this.comparisonChart) this.comparisonChart.destroy();

        this.comparisonChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Citizen Need Intensity (0-100)",
                        data: needScores,
                        backgroundColor: "rgba(220, 38, 38, 0.8)",
                        borderRadius: 4
                    },
                    {
                        label: "Demo Infrastructure Baseline (0-100)",
                        data: infraScores,
                        backgroundColor: "rgba(16, 185, 129, 0.8)",
                        borderRadius: 4
                    },
                    {
                        label: "Demo Investment Context (0-100)",
                        data: invScores,
                        backgroundColor: "rgba(37, 99, 235, 0.8)",
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: { display: true, text: "Normalized Intelligence Index (0–100)" },
                        grid: { color: "#f1f5f9" }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { position: "top" },
                    tooltip: {
                        callbacks: {
                            afterLabel: (ctx) => {
                                const idx = ctx.dataIndex;
                                const item = comparisonList[idx];
                                if (ctx.datasetIndex === 2 && item.investment_amount) {
                                    return ` Total Demo Investment: ₹${(item.investment_amount / 10000000).toFixed(1)} Cr`;
                                }
                                return "";
                            }
                        }
                    }
                }
            }
        });
    },

    // Modal mini-category chart
    renderModalCategoryChart(breakdown) {
        const ctx = document.getElementById("modalCategoryChartCanvas");
        if (!ctx) return;

        const labels = Object.keys(breakdown);
        const data = Object.values(breakdown);

        if (this.modalCategoryChart) this.modalCategoryChart.destroy();

        this.modalCategoryChart = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"],
                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 10 } } }
                }
            }
        });
    }
};

window.CivicCharts = CivicCharts;
