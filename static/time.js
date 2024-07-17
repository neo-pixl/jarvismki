// time.js
function updateTime() {
    const now = new Date(); // Get the current time
    let hours = now.getHours();
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';

    // Convert 24-hour time format to 12-hour format
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    
    // Format the time as HH:mm AM/PM
    const timeString = `${hours}:${minutes} ${ampm}`;

    // Set the text of the element with ID 'time' to the formatted time string
    document.getElementById('time').textContent = timeString;
}

// Update the time every minute since seconds are not needed
setInterval(updateTime, 60000);

// Initialize the time display
updateTime();
