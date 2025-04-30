// MAIN.JS


const upgradeButton = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');

let nextTurn = true;

// EVENTS
const upgradeEvent = 
`<div id="event-window"> <h2>upgrade</h2> <ol><li>plane</li><li>plane</li></ol> </div>`

let airplane_ar = {
    "tyyppi": "Lilla Damen 22",
    "kantama": 300,
    "kerroin": 1,
    "hinta": 0,
    "valinnanvara" : 4
    }
let money = 2000

async function upgrade_airplane(airplane_ar, money){


}


// findPorts function
// update destination-list
async function findPorts(dir) {
  let airports = await fetch(`http://localhost:3000/find-ports?location=efhk&direction=${dir}`);
  airports = await airports.json();
  console.log(airports);
  destinationList.innerHTML = '';
  for (let i=0; i < airports.length; i++) {
    destinationList.innerHTML 
      += `<li id="port-${i}">${airports[i]["ident"]} .. ${airports[i]["name"]}</li>`
  }
}

function markMap(airports) {
  for (let i = 0; i < airports.length; i++) {
    L.marker([airports[i]["lat"], airports[i]["lon"]]).addTo(map)
  .bindPopup(airports[i]["ident"])
  .openPopup();
  }
}


// Show overlayed windows. events, menus, etc.
function eventWindow(event) {
  document.querySelector('#event-container').style.display = 'block';
  document.querySelector('#map').style.display = 'none';
  document.querySelector('#event-container').innerHTML = event;
}


// BUTTONS
upgradeButton.addEventListener('click', function(evt) {
    eventWindow(upgradeEvent);
});

// KEYBINDS
document.addEventListener('keydown', async function(evt) {
  console.log(evt.key);
  
  // findPorts(dire2ction) triggered on arrow keydown
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(evt.key) && nextTurn) {
    if (evt.key === 'ArrowUp') {findPorts('N')}
    if (evt.key === 'ArrowDown') {findPorts('S')}
    if (evt.key === 'ArrowLeft') {findPorts('W')}
    if (evt.key === 'ArrowRight') {findPorts('E')}
  }

});
