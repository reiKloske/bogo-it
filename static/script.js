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

let isRunning = true;

let lastFetchTime = 0;
const FETCH_INTERVAL = 30; // ms

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
                document.querySelector('.sorted-card').classList.add('visible');
                document.querySelector('.confetti').style.visibility = 'visible';
                document.getElementById('sorted-on').innerText = `On: ${data.sorted_date}`;
                isRunning = false; // Stop the animation loop when sorted
            }

            // Updating the shuffle count display
            document.getElementById('shuffleCount').innerText = `Shuffles: ${data.shuffle_count}`;

            // Displaying the elapsed time received from the server
            document.getElementById('timer').innerText = formatTime(data.elapsed_time);
        });
}

function updateLoop(timestamp) {
    if (timestamp - lastFetchTime >= FETCH_INTERVAL) {
        updateChart();
        lastFetchTime = timestamp;
    }
    if (isRunning) {
        requestAnimationFrame(updateLoop);
    }
}

// Create the chart
const ctx = document.getElementById('bogoChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: Array.from({length: 15}, (_, i) => `${i + 1}`),
        datasets: [{
            label: 'Array Elements',
            data: [],
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
                beginAtZero: false,
                ticks: {
                    font: {
                        weight: 'bold',
                        size: 14,
                        family: "'Roboto', 'Arial', sans-serif"
                    }
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    autoSkip: false,
                    font: {
                        weight: 'bold',
                        size: 14,
                        family: "'Roboto', 'Arial', sans-serif"
                    }
                }
            }
        }
    }
});

// Start the animation loop
requestAnimationFrame(updateLoop);

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme');
    const body = document.body;
    const loader = document.querySelector('.loader');

    function applyTheme() {
        if (themeToggle.checked) {
            body.classList.remove('light-theme');
            loader.classList.remove('light-theme');
            chart.data.datasets[0].backgroundColor = '#ffffff';
            chart.data.datasets[0].borderColor = '#ffffff';
            localStorage.setItem('theme', 'dark');
        } else {
            body.classList.add('light-theme');
            loader.classList.add('light-theme');
            chart.data.datasets[0].backgroundColor = 'rgb(0, 0, 0)';
            chart.data.datasets[0].borderColor = 'rgb(0, 0, 0)';
            localStorage.setItem('theme', 'light');
        }
        chart.update();
    }

    // Checking local storage for a saved theme preference on page load
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'light') {
        themeToggle.checked = false;
    } else if (savedTheme === 'dark') {
        themeToggle.checked = true;
    } else {
        themeToggle.checked = true;
    }

    applyTheme();

    if (themeToggle) {
        themeToggle.addEventListener('change', applyTheme);
    }
    
    
});

document.getElementById('close-button').addEventListener('click', function() {
    document.querySelector('.sorted-card').classList.remove('visible');
});

// Fun Fact popup
(function() {
    const funFactCard = document.getElementById('funFactCard');
    const funFactClose = document.getElementById('funFactClose');
    
    // Check if user has already seen the fun fact
    if (!localStorage.getItem('funFactSeen')) {
        funFactCard.classList.add('visible');
    }
    
    funFactClose.addEventListener('click', function() {
        funFactCard.classList.remove('visible');
        localStorage.setItem('funFactSeen', 'true');
    });
})();
