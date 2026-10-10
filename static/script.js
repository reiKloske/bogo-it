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
let lastShuffleCount = 0;
let latestData = null;
let isDirty = false;

const socket = io();

socket.on('shuffle_update', (data) => {
    latestData = data;
    isDirty = true;
});

// Sound System - Web Audio API
let audioCtx = null;
let soundEnabled = false;

function initAudio() {
    if (audioCtx) return;
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
}

function playTone(frequency, duration = 50) {
    if (!soundEnabled || !audioCtx) return;
    
    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    oscillator.frequency.value = frequency;
    oscillator.type = 'triangle';
    
    const now = audioCtx.currentTime;
    gainNode.gain.setValueAtTime(0.15, now); 
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration / 1000);
    
    oscillator.start(now);
    oscillator.stop(now + duration / 1000);
}

function playArraySound(array) {
    if (!soundEnabled || !audioCtx) return;
    
    const minVal = Math.min(...array);
    const maxVal = Math.max(...array);
    
    const indices = [0, Math.floor(array.length / 2), array.length - 1];
    
    indices.forEach((idx, i) => {
        const value = array[idx];
        // Map to frequency: 300Hz - 1200Hz range (higher = clearer)
        const freq = 300 + ((value - minVal) / (maxVal - minVal)) * 900;
        
        // Slight delay between notes for arpeggio effect
        setTimeout(() => playTone(freq, 45), i * 10);
    });
}

// Play victory sound when sorted
function playVictorySound() {
    if (!audioCtx) return;
    
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, i) => {
        setTimeout(() => {
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);
            
            oscillator.frequency.value = freq;
            oscillator.type = 'triangle';
            
            const now = audioCtx.currentTime;
            gainNode.gain.setValueAtTime(0.2, now);
            gainNode.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
            
            oscillator.start(now);
            oscillator.stop(now + 0.25);
        }, i * 120);
    });
}

// Update the chart using the latest data received via WebSockets
function renderLatestData() {
    if (!latestData || !isDirty) return;
    isDirty = false;

    const data = latestData;
    
    // Updating the chart with the new array data
    chart.data.datasets[0].data = data.array;
    
    // Ensure labels match array length
    if (chart.data.labels.length !== data.array.length) {
        chart.data.labels = Array.from({length: data.array.length}, (_, i) => `${i + 1}`);
    }

    chart.update('none');

    // Play sound every new shuffle
    if (data.shuffle_count !== lastShuffleCount && !data.sorted) {
        playArraySound(data.array);
        lastShuffleCount = data.shuffle_count;
    }

    // Updating the status message
    if (data.sorted) {
        document.querySelector('.sorted-card').classList.add('visible');
        document.querySelector('.confetti').style.visibility = 'visible';
        document.getElementById('sorted-on').innerText = `On: ${data.sorted_date}`;
        isRunning = false; // Stop the animation loop when sorted
        
        // Victory sound
        if (soundEnabled) {
            playVictorySound();
        }
    }

    // Updating the shuffle count display
    document.getElementById('shuffleCount').innerText = `Shuffles: ${data.shuffle_count}`;

    // Displaying the elapsed time received from the server
    document.getElementById('timer').innerText = formatTime(data.elapsed_time);
}

function updateLoop() {
    renderLatestData();
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

// Sound toggle checkbox
(function() {
    const soundToggle = document.getElementById('soundToggle');
    
    // Load saved preference
    const savedSound = localStorage.getItem('soundEnabled');
    if (savedSound === 'true') {
        soundEnabled = true;
        soundToggle.checked = true;
    }
    
    soundToggle.addEventListener('change', function() {
        // Initialize audio on first user interaction
        if (!audioCtx) {
            initAudio();
        }
        
        soundEnabled = this.checked;
        localStorage.setItem('soundEnabled', soundEnabled);
        
        if (soundEnabled) {
            // Play a test tone just to confirm sound is working
            playTone(440, 100);
        }
    });
})();
