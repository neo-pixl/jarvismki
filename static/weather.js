async function updateWeather() {
    const apiKey = ''; // Your API key
    const city = ''
    const country = ''
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${city},${country}&units=imperial&appid=${apiKey}`;

    try {
        const response = await fetch(url);
        const data = await response.json();
        if (data.main && data.main.temp) {
            const tempWidget = document.getElementById('weatherTemperature');
            if (tempWidget) {
                tempWidget.textContent = `${Math.round(data.main.temp)}°F`; // Update the widget with the live temperature
            }
        }
    } catch (error) {
        console.error("Failed to fetch weather data:", error);
    }
}
