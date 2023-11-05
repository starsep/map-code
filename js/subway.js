import 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';

const map = L.map('map').setView([52.2282, 21.0036], 12);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
const response = await fetch("./data.geojson");
const data = await response.json();
L.geoJSON(data, {
    // style: function(feature) {
    //     switch (feature.properties.bucket) {
    //         case 0: return {color: "green"};
    //         case 1: return {color: "yellow"};
    //     }
    // }
}).addTo(map);