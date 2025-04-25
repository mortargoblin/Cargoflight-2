// Leflet map loader


// Map initialization
const map = L.map('map', {
  attributionControl: false,
  zoomControl: false
}).setView([50.073658, 14.418540], 4);

// stadia background layer
const stadia_bg = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_toner_background/{z}/{x}/{y}{r}.{ext}', {
	minZoom: 0,
	maxZoom: 20,
	attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
	ext: 'png'
});
stadia_bg.addTo(map)

/*
L.marker([50.073658, 14.418540]).addTo(map)
  .bindPopup('Praha.<br> nice')
  .openPopup();
*/

