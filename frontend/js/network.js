document.addEventListener('DOMContentLoaded', function () {
    const nmapForm = document.getElementById('nmapForm');
    if (nmapForm) {
        nmapForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const target = document.getElementById('target').value;
            const scanType = document.getElementById('scan_type').value;
            const excludeZones = document.getElementById('exclude_zones').checked ? 'y' : 'n';
            const additionalExcludes = document.getElementById('additional_excludes').value;

            const data = {
                target: target,
                scan_type: scanType,
                exclude_zones: excludeZones,
                additional_excludes: additionalExcludes
            };
            const resultElement = document.getElementById('scan_results');
            if (resultElement) {
                // Clear previous results and show "Scan in Progress"
                resultElement.innerHTML = `<div class="loading-animation"></div><p>Scan in Progress...</p>`;
            }
            // Perform the fetch request to run the nmap scan
            fetch('/api/runnmapscan', {
                method: 'POST',
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }
                return response.json();
            })
            .then(result => {
                // Remove the loading animation and show the scan results
                if (resultElement) {
                    if (result.success) {
                        resultElement.textContent = result.results;
                    } else {
                        resultElement.textContent = 'Error: ' + result.message;
                    }
                }
            })
            .catch(error => {
                // Handle the error case
                console.error('Error:', error);
                if (resultElement) {
                    resultElement.textContent = 'Error: ' + error.message;
                }
            });
        });
    } else {
        console.error("nmapForm element not found!");
    }
});