let chartInstance = null;

function formatTimestamp(timestamp) {
    return new Date(parseInt(timestamp)).toLocaleString();
}

function drawChart(chartData, analysisData) {
    const ctx = document.getElementById("trend-chart").getContext("2d");

    if (!chartData.length || !analysisData) {
        console.error("No data or analysis available for chart rendering.");
        return;
    }

    const timestamps = chartData.map(row => formatTimestamp(row.timestamp));
    const prices = chartData.map(row => row.price);

    const resistance = analysisData.resistance;
    const support = analysisData.support;

    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }

    const canvas = document.getElementById("trend-chart");
    canvas.addEventListener("dblclick", () => chartInstance?.resetZoom());

    let datasets = [
        {
            label: "Price",
            data: prices,
            borderColor: "blue",
            pointRadius: 0,
            yAxisID: "y-axis-price",
            fill: false
        }
    ];

    const indicators = [
    { key: "5_day_MA", label: "5-Day MA", color: "#e67e22" , hidden: true },
    { key: "25_day_MA", label: "25-Day MA", color: "#d35400" , hidden: true },
    { key: "100_day_MA", label: "100-Day MA", color: "red" , hidden: true },
    { key: "9_hr_EMA", label: "9-Hr EMA", color: "#e67e22" , hidden: true },
    { key: "50_hr_EMA", label: "50-Hr EMA", color: "#d35400" , hidden: true },
    { key: "12_hr_RSI", label: "RSI", color: "#27ae60" , hidden: true },
    { key: "market_cap", label: "Market Cap", color: "#16a085", yAxisID: "y-axis-marketcap", hidden: true },
    { key: "volume", label: "Volume", color: "#7f8c8d", yAxisID: "y-axis-volume", hidden: true }
];

    indicators.forEach(({ key, label, color, yAxisID, hidden }) => {
        if (chartData.some(row => row[key] !== null && row[key] !== undefined)) {
            datasets.push({
                label,
                data: chartData.map(row => row[key] ?? null),
                borderColor: color,
                fill: false,
                pointRadius: 0,
                hidden: hidden || false
            });
        }
    });

    datasets.push(
        {
            label: `Resistance`,
            data: Array(prices.length).fill(resistance),
            borderColor: "red",
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
        },
        {
            label: `Support`,
            data: Array(prices.length).fill(support),
            borderColor: "green",
            borderDash: [5, 5],
            fill: false,
            pointRadius: 0
        }
    );

    chartInstance = new Chart(ctx, {
        type: "line",
        data: { labels: timestamps, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                zoom: {
                    zoom: { drag: { enabled: true }, mode: "x" },
                    pan: { enabled: true, mode: "x", speed: 0.5 }
                }
            },
            scales: {
                y: {
                    ticks: {
                        display: false
                    }
                }
            }
        }
    });
}
