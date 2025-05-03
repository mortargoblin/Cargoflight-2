// MAIN.JS


const upgradeButton = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');
const backButton = document.querySelector('#back');
const closeEvent = document.querySelector('#closeEvent');

let nextTurn = true;

let money = 2000000

let airplane_ar = [{
    type: "Lilla Damen 22",
    distance: 600,
    factor: 1,
    price: 0,
    selection: 4
  }]

// EVENTS 

const upgradeEvent = 
`<h2>Upgrade your airplane</h2> <ol class="planes">
<li class="plane1">plane1</li>
<li class="plane2">plane2</li>
<li class="plane3">plane3</li>
<li class="plane4">plane4</li>
</ol>`

async function upgrade_airplane_md(plane){
  let airplaneArray = encodeURIComponent(JSON.stringify(airplane_ar))
  let airplane = await fetch(`http://localhost:3000/upgrade_airplane?airplane_ar=${airplaneArray}&money=${money}&id=${plane}`)
  airplane = await airplane.json();
  
  console.log(airplane['airplane_data']);
  console.log(airplane['money_remaining'])

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
  document.querySelector('#event').innerHTML = event;
}

function closeEventWindow() {
  document.querySelector('#event-container').style.display = 'hidden';
  document.querySelector('#map').style.display = 'block';
  document.querySelector('#event').innerHTML = '';
}




// BUTTONS
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
  document.querySelector('#event-container').style.display = 'hidden';
  document.querySelector('#map').style.display = 'block';
  document.querySelector('#event').innerHTML = ''; 
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
