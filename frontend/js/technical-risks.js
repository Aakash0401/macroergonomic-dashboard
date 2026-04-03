/* Makes the upload button interactive */
/* Upload button was removed as data will now be pulled from nmap scan
const uploadBtn = document.getElementById("uploadBtn")
const doUpload = document.getElementById("doUpload")
uploadBtn.addEventListener("click", function () {
    doUpload.click();
})
*/

/* Placeholder Data */
const pieData = [42, 58];

const getLabels = function(data, label) {
    return data.map((_, index) => `${label} ${index}`);
}

const getPieData = function(data, label) {
    return {
        labels: getLabels(data, label),
        datasets: [{
            label: label,
            data: pieData,
            backgroundColor: ['#CA4545', '#58CA45'],
            hoverOffset: 4
        }]
    }
}

const getPieDataWithLabels = function(data, main_label, labels) {
    return {
        labels: labels,
        datasets: [{
            label: main_label,
            data: data,
            backgroundColor: ['#CA4545', '#58CA45'],
            hoverOffset: 4
        }]
    }
}

const ctx = document.getElementById('vulnerabilityChart');
/* Circular Graph 1 */
new Chart(ctx, {
    type: 'pie',
    data: getPieData(pieData, "Vulnerability"),
    options: {
        responsive: false,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'right',
                labels: {
                    boxWidth: 15, 
                    generateLabels: function(chart) {
                        const data = chart.data;
                        if (data.labels.length && data.datasets.length) {
                            return data.labels.map(function(label, i) {
                                const dataset = data.datasets[0];
                                const backgroundColor = dataset.backgroundColor[i];
                                const value = dataset.data[i];
                                return {
                                    text: `${label} (${value}%)`, // Customize label text
                                    fillStyle: backgroundColor, // Color for the legend box
                                    hidden: isNaN(dataset.data[i]), // Hide if no data
                                    index: i,
                                    fontColor: '#FFFFFF' // Set label text color to white
                                };
                            });
                        }
                        return [];
                    },
                    color: '#FFFFFF' // Set label text color to white (for Chart.js v3+)
                }
            }
        }
    },
});

/* Line Graph */
const linelabels = ['21\'Q3', '21\'Q4', '22\'Q1', '22\'Q2', '22\'Q3', '22\'Q4', '23\'Q1', '23\'Q2', '23\'Q3', '23\'Q4', '24\'Q1', '24\'Q2', '24\'Q3'];
historicalRiskData = [40, 38, 30, 32, 29, 22, 20, 75, 56, 48, 40, 18, 21];

const getLineData = function(riskData, riskLegend, xaxis) {
    return {
        labels: xaxis,
        datasets: [{
            label: riskLegend,
            data: riskData,
            borderColor: 'rgb(89, 175,255)',
            tension: 0.5
        }]
    }
}

const ctx4 = document.getElementById('historicalRisk').getContext('2d');
new Chart(ctx4, {
    type: 'line',
    data: getLineData(historicalRiskData, "Risk Score (%)", linelabels),
    options: {
        responsive: false, // Allows chart to resize with the container
        maintainAspectRatio: false, // Allows custom aspect ratio
        scales: {
            x: {
                ticks: {
                    color: 'rgba(255, 255, 255, 1)' // Change x-axis label color
                },
                title: {
                    display: false,
                }
            },
            y: {
                min: 0,
                max: 100,
                ticks: {
                    color: 'rgba(255, 255, 255, 1)' // Change y-axis label color
                },
                title: {
                    display: false,
                }
            }
        },
        plugins: {
            legend: {
                labels: {
                    color: 'rgba(255, 255, 255, 1)' // Legend label font color
                }
            }
        }
    }
});

async function updatePage() {
    // Get new data
    const response = await fetch("/api/technical")
    const json = await response.json()

    // Update Risk Score
    document.getElementById("riskScore").children[1].innerText = json.score

    // Update Criticality
    // (still need to change box background color based on value)
    const values = ["LOW", "MEDIUM", "HIGH"]
    const criticalityBox = document.getElementById("Criticality").children[1]
    criticalityBox.innerText = values[json.criticality]

    // Update Issues
    const issuesBox = document.getElementById("issuesPanel")
    issuesBox.innerHTML = '<div class="title">Issues</div>'

    json.issues.map((issue) => {
        const newIssue = document.createElement("div")
        newIssue.classList.add("panel-row")
        if (issue.status == 2) {
            newIssue.classList.add("severe")
        } else if (issue.status == 1) {
            newIssue.classList.add("moderate")
        }
        newIssue.innerHTML = '<img src="img/hazard.png" alt="hazard icon"><div>hi</div>'
        newIssue.children[1].innerText = issue.name
        issuesBox.appendChild(newIssue)
    })

    // Update historical social risk scores
    const labels = json.historical.map((v) => {return v.label})
    const scores = json.historical.map((v) => {return v.score})
    const historicalRiskChart = Chart.getChart(document.getElementById("historicalRisk"))
    historicalRiskChart.data.labels = labels
    historicalRiskChart.data.datasets[0].data = scores
    historicalRiskChart.update()

    // Update Vulnerabilities
    const vuln_names = json.vulnerabilities.map((v) => {return v.name})
    const vuln_percents = json.vulnerabilities.map((v) => {return v.percent})
    const vulnerabilityChart = Chart.getChart(document.getElementById("vulnerabilityChart"))
    vulnerabilityChart.data = getPieDataWithLabels(vuln_percents, "Vulnerability", vuln_names)
    vulnerabilityChart.update("none")
}

setInterval(updatePage, 5000)
updatePage()

// Function to format time as a string
function formatTime(date) {
    let hours = date.getHours();
    let minutes = date.getMinutes();
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // Hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    let strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

// Function to update clock
function updateClock() {
    let now = new Date();
    let day = String(now.getDate()).padStart(2, '0');
    let month = String(now.getMonth() + 1).padStart(2, '0');
    let year = now.getFullYear();
    let timeString = formatTime(now);
    
    let formattedDate = `${day}/${month}/${year} ${timeString}`;
    document.getElementById('live-clock').textContent = formattedDate;
}

// Update clock every second
setInterval(updateClock, 1000);

// Initial call to display clock immediately on page load
updateClock();
