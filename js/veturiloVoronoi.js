import 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
import { veturilo, lines } from './data.js';

const map = L.map('map').setView([52.2282, 21.0036], 12);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
veturilo.forEach(([lat, lon, name]) => {
    const marker = L.marker([lat, lon]);
    marker.bindPopup(name);
    marker.addTo(map);
});
for (let i = 0; i < lines.length; i++) {
    const polygon = L.polyline(lines[i], {color: "blue"});
    polygon.addTo(map);
}