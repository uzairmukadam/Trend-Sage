document.addEventListener("DOMContentLoaded", fetchDatasetNames);

function fetchDatasetNames() {
    fetch("http://127.0.0.1:5000/get_names")
        .then(response => response.json())
        .then(data => {
            const dropdown = document.getElementById("dataset-dropdown");
            dropdown.innerHTML = "";
            data.datasets.forEach(name => {
                const option = document.createElement("option");
                option.value = name;
                option.textContent = name;
                dropdown.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching dataset names:", error));
}

function loadDataset() {
    const selectedName = document.getElementById("dataset-dropdown").value;
    fetch(`http://127.0.0.1:5000/get_data/${selectedName}`)
        .then(response => response.json())
        .then(data => {
            updateMarketAnalysis(data.analysis);
            drawChart(data.chart, data.analysis);
        })
        .catch(error => console.error("Error loading dataset:", error));
}

function updateMarketAnalysis(analysisData) {
    const container = document.getElementById("analysis-container");

    let tableHTML = `<table id="analysis-table" border="1">
                        <thead><tr>`;

    for (const key of Object.keys(analysisData)) {
        tableHTML += `<th>${key}</th>`;
    }
    tableHTML += `</tr></thead><tbody><tr>`;

    for (const value of Object.values(analysisData)) {
        tableHTML += `<td>${value !== null ? value : "N/A"}</td>`;
    }
    tableHTML += `</tr></tbody></table>`;

    container.innerHTML = `${tableHTML}`;
}
