import 'https://unpkg.com/leaflet@1.9.3/dist/leaflet.js';
import 'https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js';
import { bicycleParkings } from './data.js';

const map = L.map('map').setView([52.2282, 21.0036], 12);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://osm.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
L.heatLayer(bicycleParkings, {
    "max": 10,
}).addTo(map);