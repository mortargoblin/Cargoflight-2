// MAIN.JS

////////////// VARIABLES

const upgradeButton = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');
const backButton = document.querySelector('#back');
const closeEvent = document.querySelector('#close-event');

const player_name = 'tester';

let nextTurn = true;
// TODO: move money to backend
let money = 2000000;
let currentLocation = {
  ident: "EFHK", 
  name: "Helsinki Vantaa Airport", 
  type: "large_airport", 
  iso_country: "FI", 
  lat: 60.3172, 
  long: 24.963301
};
let nextLocationList = []
let nextLocation = {}

let airplane_ar = [{
  type: "Lilla Damen 22",
  distance: 600,
  factor: 1,
  price: 0,
  selection: 4
}];

// EVENTS 

const upgradeEvent = 
`<h2>Upgrade your airplane</h2> <ol class="planes">
<li class="plane1">Name: Lilla Damen 22, Distance: 300, Selection: 4, Factor: 1, Price: 0 €</li>
<li class="plane2">Name: Stor Dam 23, Distance: 450, Selection: 5, Factor: 1.4, Price: 25 000 €</li>
<li class="plane3">Name: Nanny 24, Distance: 600, Selection: 6, Factor: 1.6, Price: 60 000 €</li>
<li class="plane4">Name: Mamma Birgitta 24, Distance: 1500, Selection: 7, Factor: 2, Price: 100 000 €</li>
</ol>`;


////////////// FUNCTIONS

async function upgrade_airplane_md(plane){
  let airplaneArray = encodeURIComponent(JSON.stringify(airplane_ar))

  let test = await fetch(`http://localhost:3000/create_new_game`)
  test = await test.json();



  let airplane = await fetch(`http://localhost:3000/upgrade_airplane?airplane_ar=${airplaneArray}&money=${money}&id=${plane}`);
  airplane = await airplane.json();
  money = airplane['money_remaining']
  airplane_ar =[{
    type: airplane['airplane_data']['type'],
    distance: airplane['airplane_data']['distance'],
    factor: airplane['airplane_data']['factor'],
    price: airplane['airplane_data']['price'],
    selection: airplane['airplane_data']['selection']
  }]
  console.log(test)
  console.log(airplane['text']);
  console.log(airplane['airplane_data']);
  console.log(airplane['money_remaining']);
}

// findPorts function
// update destination-list
async function findPorts(direction) {
  const airports = await fetch(
    `http://localhost:3000/find-ports?player=${player_name}
    &direction=${direction}`
  );
  const response = await airports.json();
  console.log(response);

  markDestinationList(response);
  markMap(response);
  refreshDestinationListener();
  return response[0];
}

function markDestinationList(airports) {
  destinationList.innerHTML = '';
  console.log('destination list airports length', airports.length);
  for (let i = 0; i < airports.length; i++) {
    destinationList.innerHTML += 
      `<li id="port-${i}"><div>${airports[i]["ident"]}</div> 
      <div id="airport-name">${airports[i]["name"]}</div></li>`
  }
}

function markMap(airports) {
  for (let i = 0; i < airports.length; i++) {
    L.marker([airports[i]["lat"], airports[i]["long"]]).addTo(map)
    .bindPopup(airports[i]["name"])
    .openPopup();
  }
}

// Show overlayed windows. events, menus, etc.
function eventWindow(event) {

  const element = document.querySelector('#event-container');
  element.classList.remove('event-container-hidden');
  document.querySelector('#map').style.display = 'none';
  document.querySelector('#event').innerHTML = event;
}

function closeEventWindow() {

  const element = document.querySelector('#event-container');
  element.classList.add('event-container-hidden');
  document.querySelector('#map').style.display = 'block';
}


//////////// BUTTONS

upgradeButton.addEventListener('click', function(evt) {
    eventWindow(upgradeEvent);

    const planeitem = document.querySelectorAll('#event-window .planes li')

    planeitem.forEach(item => {
    item.addEventListener('click', () =>{
      if (item.className === 'plane1') {
        const planenumber = 1
        upgrade_airplane_md(planenumber)
      }
      if (item.className === 'plane2') {
        const planenumber = 2
        upgrade_airplane_md(planenumber)
      }
      if (item.className === 'plane3') {
        const planenumber = 3
        upgrade_airplane_md(planenumber)
      }
      if (item.className === 'plane4') {
        const planenumber = 4
        upgrade_airplane_md(planenumber)
      }


      /*const planenumber = item.className*/
    })
  })
});

closeEvent.addEventListener('click', function() {
    closeEventWindow()
});

// Compass buttons
document.querySelector('#north').addEventListener('click', function() {
  findPorts('N');
});
document.querySelector('#west').addEventListener('click', function() {
  findPorts('W');
});
document.querySelector('#east').addEventListener('click', function() {
  findPorts('E');
});
document.querySelector('#south').addEventListener('click', function() {
  findPorts('S');
});

// Movement (via destination list)
function refreshDestinationListener() {
  const list = document.querySelector('#destination-list');
  // lord help me
  document.querySelector('#destination-list').addEventListener('click', function(evt) {
    if (evt.target.id.startsWith('port')) {
      const id = evt.target.id.split('-').pop();
      console.log(id);
      // move to HERE
    } // else if (evt.target.parentElement.id.startsWith('port')) {
      // const id = evt.target.parentElement.id.split('-').pop();
      // console.log(id);
      // move to HERE
    //}
  });
}

/////////// KEYBINDS

document.addEventListener('keydown', async function(evt) {
  console.log(evt.key);
  
});
