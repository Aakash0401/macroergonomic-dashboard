labels = ["-5m", "-4m", "-3m", "-2m", "-1m"]

// Network Traffic graph
traffic_up = [0, 1, 2, 3, 4]
traffic_down = [0, 1, 2, 3, 4]

const trafficCtx = document.getElementById("traffic").getContext("2d")
new Chart(trafficCtx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [{
            label: 'Upload',
            data: traffic_up,
            fill: true,
            borderColor: '#ff0000',
            tension: 0.5
        },
        {
            label: 'Download',
            data: traffic_down,
            fill: true,
            borderColor: '#00ff44',
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
                max: 150,
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


// Threats graph
threats_data = [1,2,3,4,5];
const threatsCtx = document.getElementById("threats").getContext("2d")
new Chart(threatsCtx, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Number of Threats',
            data: threats_data,
            backgroundColor: [
            'rgba(33, 118, 246, 0.2)',
            ],
            borderColor: [
            'rgb(33, 118, 246)',
            ],
            borderWidth: 1
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
                max: 15, // could also set to maximum value in threats_data
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



function createUser(name, time, ip, upload, download, uploadTotal, downloadTotal) {
    const div = document.createElement("div")
    div.innerHTML = `<div class="user-box">
                        <img src="img/user.png" alt="user icon" style="height: 32px">
                        <div style="display: flex; flex-direction: column">
                            <div>Name</div>
                            <div>
                                <img src="img/clock.png" alt="clock icon">
                                <div>1d 2h 23m</div>
                            </div>
                        </div>
                        <div>192.168.4.1</div>
                        <div>
                            <img src="img/red_up_arrow.png" alt="up arrow">
                            <div>num</div>
                            <div>num</div>
                        </div>
                        <div>
                            <img src="img/green_down_arrow.png" alt="down arrow">
                            <div>num</div>
                            <div>num</div>
                        </div>
                    </div>`
    const userBox = div.children[0]

    const nameEl = userBox.children[1].children[0]
    const timeEl = userBox.children[1].children[1].children[1]
    const ipEl = userBox.children[2]
    const uploadEl = userBox.children[3].children[1]
    const uploadTotalEl = userBox.children[3].children[2]
    const downloadEl = userBox.children[4].children[1]
    const downloadTotalEl = userBox.children[4].children[2]

    nameEl.innerText = name
    timeEl.innerText = time
    ipEl.innerText = ip
    uploadEl.innerText = upload
    uploadTotalEl.innerText = uploadTotal
    downloadEl.innerText = download
    downloadTotalEl.innerText = downloadTotal

    document.querySelector("#users > .content").appendChild(userBox)
}

function createAlert(title, body, time, isSevere) {
    const alert = document.createElement("div")

    alert.classList.add("alert-box")
    if (isSevere)
        alert.classList.add("severe")

    const titleEl = document.createElement("div")
    titleEl.classList.add("heading")
    titleEl.innerText = title

    const bodyEl = document.createElement("div")
    bodyEl.innerText = body

    const mainEl = document.createElement("div")
    mainEl.appendChild(titleEl)
    mainEl.appendChild(bodyEl)

    alert.innerHTML += `<div style="text-align: center"><img src="img/hazard.png" alt="danger icon" style="height: 24px"><div>${time}</div></div>`
    alert.appendChild(mainEl)
    document.querySelector("#alerts > .content").appendChild(alert)
}

async function updatePage() {
    // Get new data
    const response = await fetch("/api/index")
    const json = await response.json()

    // Update overview section
    const overview = document.getElementById("stats-overview")
    overview.children[0].children[1].innerText = `${json.overview.active_users} users were active`
    overview.children[0].children[2].innerText = `${json.overview.open_ports} open ports were detected`
    overview.children[1].children[0].innerText = json.overview.active_users
    overview.children[3].children[0].innerText = `${json.overview.good_employee_percent}%`

    const value = json.overview.overall_percent / 100
    if (value <= 0.35) {
        overview.children[2].children[0].textContent = "Low";
    } else if (value > 0.35 && value <= 0.6) {
        overview.children[2].children[0].textContent = "Moderate";
    } else if (value > 0.6) {
        overview.children[2].children[0].textContent = "High";
    }

    // Update users section
    document.querySelector("#users > .content").innerHTML = ""
    json.users.map((user) => {
        return createUser(user.name, user.time, user.ip, user.upload, user.download, user.upload_total, user.download_total)
    })

    // Update alerts section
    document.querySelector("#alerts > .content").innerHTML = ""
    json.alerts.map((alert) => {
        return createAlert(alert.title, alert.body, alert.time, alert.isSevere)
    })

    // Update network traffic section
    const traffic = Chart.getChart(document.getElementById("traffic"))
    traffic.data.datasets[0].data = json.traffic_up
    traffic.data.datasets[1].data = json.traffic_down
    traffic.options.scales.y.max = Math.max(json.traffic_up.concat(json.traffic_down))
    traffic.update()

    // Update threats section
    const threats = Chart.getChart(document.getElementById("threats"))
    threats.data.datasets[0].data = json.threats
    threats.update()
}

setInterval(updatePage, 5000)
updatePage()