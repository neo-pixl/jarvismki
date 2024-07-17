function showAlertWidget() {
    var alertWidget = document.getElementById('draggable2');
    alertWidget.style.display = 'block'; // Show the time widget
    
    // Set a timeout to hide the widget after 1 minute and 30 seconds
    setTimeout(function() {
    alertWidget.style.display = 'none'; // Hide the widget
    }, 120000); // 90000 milliseconds = 1 minute and 30 seconds
}
function showReminderWidget() {
    var reminderWidget = document.getElementById('draggable3'); // Assuming 'draggable3' is your reminder widget's ID
    if (!reminderWidget) {
        console.error("Reminder widget not found!");
        return;
    }

    reminderWidget.style.display = 'block'; // Show the reminder widget

    setTimeout(function() {
    reminderWidget.style.display = 'none'; // Hide the widget after a certain time
    }, 160000); // 60000 milliseconds = 1 minute
}

function showAudioWidget() {
    var audioWidget = document.getElementById('draggable4');
    audioWidget.style.display = 'block'; // Show the time widget
    
}
function showCalcWidget() {
    var calcWidget = document.getElementById('draggable7');
    calcWidget.style.display = 'block'; // Show the time widget

    setTimeout(function() {
    calcWidget.style.display = 'none'; // Hide the widget after a certain time
    }, 160000); // 60000 milliseconds = 1 minute
}
function showTicTacWidget() {
    var ticWidget = document.getElementById('draggable8');
    ticWidget.style.display = 'block'; // Show the time widget
}
async function showWeatherWidget() {
    await updateWeather(); // Fetch the latest weather data before showing the widget
    var weatherWidget = document.getElementById('draggable6'); // Ensure this is the correct ID for your weather widget
    if (weatherWidget) {
        weatherWidget.style.display = 'block'; // Show the weather widget
    }
    

    // Fetch and update the temperature just before showing the widget
    await updateWeather();  // This will fetch the latest weather and update the display
    weatherWidget.style.display = 'block'; // Show the weather widget

    // Optionally, set a timeout to hide the widget after some time
    setTimeout(function() {
        weatherWidget.style.display = 'none'; // Hide the widget
    }, 200000); // 300000 milliseconds = 5 minutes
}
async function showTrafficWidget() {
    await updateTraffic();  // Fetch the latest traffic data before showing the widget
    var trafficWidget = document.getElementById('draggable5');  // Adjust if your ID is different
    if (trafficWidget) {
        trafficWidget.style.display = 'block';  // Show the traffic widget
    }
    setTimeout(function() {
        weatherWidget.style.display = 'none'; // Hide the widget
    }, 200000);
}
function showSubWidget() {
    var subscriberCountWidget = document.getElementById('draggable5'); // Assuming 'draggable5' is your subscriber count widget's ID
    if (!subscriberCountWidget) {
        console.error("Subscriber count widget not found!");
        return;
    }

    subscriberCountWidget.style.display = 'block'; // Show the subscriber count widget

    setTimeout(function() {
        subscriberCountWidget.style.display = 'none'; // Hide the widget after a certain time
    }, 200000); // 200000 milliseconds = 3 minutes and 20 seconds
}