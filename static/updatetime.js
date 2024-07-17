function startClock() {
    setInterval(updateTime, 1000); // Update the time every second
}

function updateTime() {
var now = new Date();
var hours = now.getHours();
var minutes = now.getMinutes();
var ampm = hours >= 12 ? 'PM' : 'AM';
hours = hours % 12;
hours = hours ? hours : 12; // the hour '0' should be '12'
minutes = minutes < 10 ? '0' + minutes : minutes;
var timeString = hours + ':' + minutes + ' ' + ampm;
document.getElementById('time').textContent = timeString;
}

function respondWithTextToSpeech(text) {
    fetch('http://localhost:5000/speak', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: text })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        audio.play();
    })
    .catch(error => console.error('Error:', error));
}

function showTimeWidget() {
var timeWidget = document.getElementById('draggable');
timeWidget.style.display = 'block'; // Show the time widget
updateTime(); // Ensure the time is updated immediately

// Set a timeout to hide the widget after 1 minute and 30 seconds
setTimeout(function() {
timeWidget.style.display = 'none'; // Hide the widget
}, 120000); // 90000 milliseconds = 1 minute and 30 seconds
}