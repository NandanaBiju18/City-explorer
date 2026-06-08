let cityData = {}

function getCityData() {
    let city = document.getElementById("cityInput").value;
    
    document.getElementById("result").innerHTML = `
        <div class="loading">
            🌍 Searching city data...
            <br><br>
            ⏳ Please wait
        </div>
    `;

    fetch("/city-data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city: city })
    })
    .then(res => res.json())
    .then(data => {

    cityData = data;

    document.getElementById("result").classList.remove("hidden");
    document.getElementById("actions").classList.remove("hidden");

    document.getElementById("result").innerHTML = `
<div class="city-card">

    <h2>📍 ${data.city}</h2>

    <p>${data.state}, ${data.country}</p>

    <img src="${data.flag}" class="flag">

    ${
        data.wiki_image
        ? `<img src="${data.wiki_image}" class="city-img">`
        : ""
    }

    <p>${data.wiki_summary}</p>

    <hr>

    <div class="quick-info">

<p>💰 Currency: ${data.currency || "Not available"}</p>

<p>👥 Population: ${
    data.population
        ? Number(data.population).toLocaleString()
        : "Not available"
}</p>

<p>🕒 Local Time: ${data.local_time || "Not available"}</p>

<p>🌤 ${data.temp}°C | ${data.desc}</p>

</div>

</div>
`;
});
}

function showClimate() {
    document.getElementById("details").innerHTML = `
<h3>🌤 Climate</h3>

<p><b>Temperature:</b> ${cityData.temp}°C</p>
<p><b>Condition:</b> ${cityData.desc}</p>

<hr>

<h3>📍 Location</h3>

<p><b>Country:</b> ${cityData.country}</p>
<p><b>State:</b> ${cityData.state}</p>

<hr>

<h3>🌎 Additional Info</h3>
<p><b>Local Time:</b> ${cityData.local_time}</p>

<hr>

<a target="_blank"
href="https://www.google.com/maps?q=${cityData.lat},${cityData.lon}">
🗺 Open in Google Maps
</a>
`;
}

function showPlaces() {
    if (!cityData.city) {
        alert("Search a city first");
        return;
    }

    fetch("/tourist", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            lat: cityData.lat,
            lon: cityData.lon
        })
    })
    .then(res => res.json())
    .then(data => {

        let html = "<h3>📍 Tourist Attractions</h3>";

        if (!data.places || data.places.length === 0) {
            html += "<p>No attractions found.</p>";
        } else {

            data.places.forEach(place => {
                html += `<p>⭐ ${place}</p>`;
            });
        }

        document.getElementById("details").innerHTML = html;
    });
}

function showIntro() {
    document.getElementById("details").innerHTML = `
        <h3>🤖 AI City Insight</h3>
        <p>${cityData.intro}</p>
    `;
}

function showNews() {
    if (!cityData.city) {
        alert("Search a city first");
        return;
    }

    fetch("/news", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            city: cityData.city
        })
    })
    .then(res => res.json())
    .then(data => {

        let html = "<h3>📰 Latest News</h3>";

        if (!data.news || data.news.length === 0) {
            html += "<p>No news available.</p>";
        } else {

            data.news.forEach(n => {

                html += `
                <div class="news-card">
                    <h4>${n.title}</h4>
                    <p>${n.description || "No description available."}</p>
                    <small>${n.source}</small><br>
                    ${
                        n.url
                        ? `<a href="${n.url}" target="_blank">Read More</a>`
                        : ""
                    }
                </div>
                `;
            });
        }

        document.getElementById("details").innerHTML = html;
    });
}