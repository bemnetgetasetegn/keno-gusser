// Start button functionality
document.getElementById('start-btn').addEventListener('click', function() {
    const startSection = document.getElementById('start-section');
    const gamePanel = document.getElementById('game-panel');
    
    // Hide start section
    startSection.style.opacity = '0';
    startSection.style.transform = 'scale(0.9)';
    
    setTimeout(() => {
        startSection.classList.add('hidden');
        gamePanel.classList.remove('hidden');
        
        setTimeout(() => {
            gamePanel.classList.add('show');
        }, 10);
    }, 300);
});

// Function to generate keno numbers
function generateKenoNumbers() {
    const numbers = [];
    const used = new Set();
    
    while (numbers.length < 20) {
        const num = Math.floor(Math.random() * 80) + 1;
        if (!used.has(num)) {
            used.add(num);
            numbers.push(num);
        }
    }
    
    return numbers.sort((a, b) => a - b);
}

// Function to display numbers as keno balls
function displayNumbers(numbers) {
    const display = document.getElementById('numbers-display');
    display.innerHTML = ''; // Clear previous numbers
    
    numbers.forEach((num, index) => {
        const ball = document.createElement('div');
        ball.className = 'keno-ball';
        ball.textContent = num;
        ball.style.animationDelay = `${index * 0.05}s`;
        display.appendChild(ball);
    });
}

// Guess button functionality
document.getElementById('guess-btn').addEventListener('click', function() {
    const numbers = generateKenoNumbers();
    displayNumbers(numbers);
    
    // Show refresh button
    document.getElementById('refresh-btn').classList.remove('hidden');
});

// Refresh button functionality
document.getElementById('refresh-btn').addEventListener('click', function() {
    const display = document.getElementById('numbers-display');
    
    // Fade out current numbers
    display.style.opacity = '0';
    display.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        const numbers = generateKenoNumbers();
        displayNumbers(numbers);
        
        // Fade in new numbers
        display.style.opacity = '1';
        display.style.transform = 'scale(1)';
    }, 300);
});
