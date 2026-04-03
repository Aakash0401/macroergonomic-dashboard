/* ===Social gauge===
 * setGaugeValue must be called with a value from 0-1 according to survey results.
 * Risk levels:
 * 0.0-0.35 = low
 * 0.35 - 0.6 = moderate
 * 0.6 - 1.0 = high
*/
const gaugeElement = document.querySelector(".social-gauge");

function setGaugeValue(gauge, value) {
  if (value < 0 || value > 1) {
    return;
  }

  gauge.querySelector(".social-gauge-fill").style.transform = `rotate(${
    value / 2
  }turn)`;
  gauge.querySelector(".social-gauge-cover").textContent = `${Math.round(value * 100)}%`;
  if (value <= 0.35) {
    gauge.querySelector(".social-gauge-fill").style.background = '#58CA45'
    document.getElementById("social-header-risk-level").style.color = '#58CA45';
    document.getElementById("social-header-risk-level").textContent = "LOW RISK";
  } else if (value > 0.35 && value <= 0.6) {
    gauge.querySelector(".social-gauge-fill").style.background = '#CAAD45'
    document.getElementById("social-header-risk-level").style.color = '#CAAD45';
    document.getElementById("social-header-risk-level").textContent = "MEDIUM RISK";
  } else if (value > 0.6) {
    gauge.querySelector(".social-gauge-fill").style.background = '#CA4545'
    document.getElementById("social-header-risk-level").style.color = '#CA4545';
    document.getElementById("social-header-risk-level").textContent = "HIGH RISK";
  }
}

setGaugeValue(gaugeElement, 0.34);

/* Circular Graph 1 */
const ctx = document.getElementById('myChart');
new Chart(ctx, {
    type: 'doughnut',
    data: {
    datasets: [{
        data: [42, 58],
        backgroundColor: [
        '#CA4545',
        '#58CA45',
        ],
        hoverOffset: 4
        }]
    },
    options: {
        responsive: false, // Allows chart to resize with the container
        maintainAspectRatio: false // Allows custom aspect ratio
    },
});

/* Circular Graph 2 */
const ctx2 = document.getElementById('myChart2');
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
        datasets: [{
            data: [19, 81],
            backgroundColor: [
            '#CA4545',
            '#58CA45',
            ],
            hoverOffset: 4
        }]
    },
    options: {
        responsive: false, // Allows chart to resize with the container
        maintainAspectRatio: false // Allows custom aspect ratio
    },
});

/* Circular Graph 3 */
const ctx3 = document.getElementById('myChart3');
    new Chart(ctx3, {
        type: 'doughnut',
        data: {
        datasets: [{
            data: [25, 75],
            backgroundColor: [
            '#CA4545',
            '#58CA45',
            ],
            hoverOffset: 4
        }]
    },
    options: {
        responsive: false, // Allows chart to resize with the container
        maintainAspectRatio: false // Allows custom aspect ratio
    },
});

/* Line Graph */
const linelabels = ['21\'Q3', '21\'Q4', '22\'Q1', '22\'Q2', '22\'Q3', '22\'Q4', '23\'Q1', '23\'Q2', '23\'Q3', '23\'Q4', '24\'Q1', '24\'Q2', '24\'Q3'];
historicalRiskData = [40, 38, 30, 32, 29, 22, 20, 75, 56, 48, 40, 18, 21];

const ctx4 = document.getElementById('historicalRisk').getContext('2d');
new Chart(ctx4, {
    type: 'line',
    data: {
        labels: linelabels,
        datasets: [{
            label: 'Risk Score (%)',
            data: historicalRiskData,
            fill: true,
            borderColor: 'rgb(89, 175, 255)',
            tension: 0.5
        }]
    },
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

/* Pie Chart */
const ctx5 = document.getElementById('employeeRiskLevel').getContext('2d');
new Chart(ctx5, {
    type: 'pie',
    data: {
        labels: [
            'Very Low',
            'Low',
            'Moderate',
            'High',
            'Very High'
        ],
        datasets: [{
            label: 'Number of Employees',
            data: [300, 50, 100, 150, 200],
            backgroundColor: [
              '#FFD1D1', '#E48888', '#DB5353', '#AB2424', '#781919'
            ],
            hoverOffset: 4
        }]
    },
    options: {
        responsive: false, // Allows chart to resize with the container
        maintainAspectRatio: false, // Allows custom aspect ratio
        plugins: {
            legend: {
                labels: {
                    color: 'rgba(255, 255, 255, 1)' // Legend label font color
                }
            }
        }
    }
});

/* Handle file upload */
// https://developer.mozilla.org/en-US/docs/Web/API/File_API/Using_files_from_web_applications#using_hidden_file_input_elements_using_the_click_method
const uploadBtn = document.getElementById("uploadBtn");
const fileUpload = document.getElementById("fileUpload");
uploadBtn.addEventListener("click", (e) => {
    if (fileUpload) {
        fileUpload.click()
    }
}, false)

fileUpload.addEventListener("change", (e) => {
    // https://stackoverflow.com/a/39515846
    const reader = new FileReader()
    reader.onload = async (fileEvent) => {
        const fileContent = fileEvent.target.result

        // Send csv, wait 1 second in case we can reload faster than the INSERT queries, then reload
        fetch("/api/socialupdate", {method: "post", body: fileContent})
        await new Promise(r => setTimeout(r, 1000))  // https://stackoverflow.com/a/39914235
        location.reload()  // Technically not needed, but gives visual feedback that something has changed
    }

    const file = e.target.files[0]

    reader.readAsText(file)
}, false)

/* Update page via API */
function getTitleText(el, n) {
    return el.children[n].getElementsByClassName("title-text")[0]
}

async function updatePage() {
    // Get new data
    const response = await fetch("/api/social")
    const json = await response.json()

    // Update overview section
    const statsOverview = document.getElementById("stats-overview")
    getTitleText(statsOverview, 0).innerText = `${json.overview.good_employee_percent}%`
    getTitleText(statsOverview, 1).innerText = json.overview.best_dept
    getTitleText(statsOverview, 2).innerText = json.overview.worst_dept
    setGaugeValue(gaugeElement, json.overview.overall_percent / 100)

    // Update areas of concern
    const areasOfConcern = document.getElementById("areas-of-concern")
    areasOfConcern.innerHTML = '<div class="title">Areas of Concern</div>'
    json.areas_of_concern.map((area) => {
        const newAoc = document.createElement("div")

        newAoc.classList.add("panel-row")
        if (area.severity === 2) {
            newAoc.classList.add("severe")
        } else if (area.severity === 1) {
            newAoc.classList.add("moderate")
        }

        newAoc.innerHTML += '<img src="img/hazard.png" alt="hazard icon">'

        const newAocTitle = document.createElement("div")
        newAocTitle.innerText = area.name
        newAoc.appendChild(newAocTitle)

        areasOfConcern.appendChild(newAoc)
    })

    // Update departments
    const departments = document.getElementById("departments")
    departments.innerHTML = '<div class="title">Departments</div>'
    Object.keys(json.departments).map((dept) => {
        const score  = json.departments[dept].score
        const hazard = json.departments[dept].hazard

        const newDept = document.createElement("div")
        newDept.classList.add("panel-row")

        const deptInfo = document.createElement("div")
        if (hazard)
            deptInfo.innerHTML += '<img src="img/hazard.png" alt="hazard icon">'
        const deptName = document.createTextNode(dept)
        deptInfo.appendChild(deptName)

        const deptScore = document.createElement("img")
        deptScore.src = `img/score_${score}.png`

        newDept.appendChild(deptInfo)
        newDept.appendChild(deptScore)

        departments.appendChild(newDept)
    })

    // Update employee risk levels
    const employeeRiskLevelChart = Chart.getChart(document.getElementById('employeeRiskLevel'))
    employeeRiskLevelChart.data.datasets[0].data = json.employee_risk_level
    employeeRiskLevelChart.update()

    // Update overall scores
    const overallScores = document.getElementById("overall-scores")
    json.scores.map((category, i) => {

        // Update chart
        const chart = Chart.getChart(overallScores.children[1].children[i].children[0])
        chart.data.datasets[0].data = [100 - category.percent_good, category.percent_good]
        chart.update()

        // Update numbers under chart
        overallScores.children[1].children[i].children[2].innerText = `${category.percent_good}%`

        // Update name
        overallScores.children[1].children[i].children[1].innerText = category.name

        // Update columns for each scoring criteria, e.g. Password Management, Email Usage
        const column = overallScores.children[2].children[i]
        column.innerHTML = ""

        category.scores.map((scoreData) => {
            const row = document.createElement("div")
            row.classList.add("overall-scores-row")

            const label = document.createElement("div")
            label.classList.add("label")
            label.innerText = scoreData.name

            const scoreDisplay = document.createElement("img")
            scoreDisplay.src = `img/score_${scoreData.value}.png`

            row.appendChild(label)
            row.appendChild(scoreDisplay)

            column.appendChild(row)
        })
    })

    // Update historical social risk scores
    const labels = json.historical.map((v) => {return v.label})
    const scores = json.historical.map((v) => {return v.score})
    const historicalRiskChart = Chart.getChart(document.getElementById("historicalRisk"))
    historicalRiskChart.data.labels = labels
    historicalRiskChart.data.datasets[0].data = scores
    historicalRiskChart.update()
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