// Function to format time as days, hours, minutes, and seconds
function formatTime(seconds) {
    let days = Math.floor(seconds / 86400);
    seconds %= 86400;
    let hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    let minutes = Math.floor(seconds / 60);
    seconds = Math.floor(seconds % 60);
    return `${days} days ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Function to update the chart by fetching the latest server-side shuffle
function updateChart() {
    fetch('/shuffle_array')
        .then(response => response.json())
        .then(data => {
            // Updating the chart with the new array data
            chart.data.datasets[0].data = data.array;
            chart.update();

            // Updating the status message
            if (data.sorted) {
                document.getElementById('title').innerText = 'Boggoed!';
                clearInterval(updateInterval); // Stopping updates when sorted
                clearInterval(timerInterval);  // Stopping the timer when sorted
            } else {
                document.getElementById('title').innerText = 'Bogo It!';
            }

            // Updating the shuffle count display
            document.getElementById('shuffleCount').innerText = `Shuffles: ${data.shuffle_count}`;

            // Displaying the elapsed time received from the server
            document.getElementById('timer').innerText = formatTime(data.elapsed_time);
        });
}

// Creating the chart
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: Array.from({length: 12}, (_, i) => `${i + 1}`),
        datasets: [{
            label: 'Array Elements',
            data: [],
            backgroundColor: 'rgba(9, 255, 1, 0.3)',
            borderColor: 'rgba(9, 255, 1, 1)',
            borderWidth: 1,
            borderRadius: 5,
        }]
    },
    options: {
        animation: false,
        responsive: true,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.7)',
                titleFont: {
                    size: 14,
                    family: "'Roboto', 'Arial', sans-serif"
                },
                bodyFont: {
                    size: 12,
                    family: "'Roboto', 'Arial', sans-serif"
                },
                padding: 10,
                cornerRadius: 3,
                displayColors: false,
            }
        },
        scales: {
            y: {
                grid: {
                    display: false
                },
                beginAtZero: false
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    }
});

// Fetch updates every 200 milliseconds to display the latest server-side shuffle
const updateInterval = setInterval(updateChart, 200);
