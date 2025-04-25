//import defaultExport from './leaflet.js';

const map = L.map('map').setView([50.073658, 14.418540], 5);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

L.marker([50.073658, 14.418540]).addTo(map)
  .bindPopup('Praha.<br> nice')
  .openPopup();


  // osm layer

