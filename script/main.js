// MAIN.JS

////////////// VARIABLES

const upgradeButton = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');
const backButton = document.querySelector('#back');
const closeEvent = document.querySelector('#close-event');

const player_name = 'tester';

let nextTurn = true;

player_stats()
/*
let currentLocation = {
  ident: "EFHK", 
  name: "Helsinki Vantaa Airport", 
  type: "large_airport", 
  iso_country: "FI", 
  lat: 60.3172, 
  long: 24.963301
};
*/
let nextLocationList = []
let nextLocation = {}



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


function end_script(money, name, shifts){
  const endWindow = document.querySelector('#end-window');
  endWindow.createElement('h2').innerHTML = 'Game Over!';
  endWindow.createElement('p').innerHTML = 'Thanks for playing our game.'
  const ul = endWindow.createElement('ul')
  const h2 = ul.createElement('h2').innerHTML = 'There is your player stats.'
  h2.createElement('p').innerHTML = `Company name: ${name}   Money get: ${money}     Shifts remain: ${shifts}`

  document.querySelector('#end-window').overflow = 'visible'
  document.querySelector('#event-container').overflow = 'hidden'
}

//This upgrade statswindow
function statsWindow(money, name, airplane, shifts){
  const add = document.querySelector('#stats-item')

    add.innerHTML = ''

    const namecont = document.createElement('li')
    namecont.textContent = `Name: ${name}`

    const moneycont = document.createElement('li')
    moneycont.textContent = `Money: ${money}`

    const airplanecont = document.createElement('li')
    airplanecont.textContent = `Airplane: ${airplane}`

    const shiftscont = document.createElement('li')
    shiftscont.textContent = `Shifts remain: ${shifts}`

    add.appendChild(namecont)
    add.appendChild(moneycont)
    add.appendChild(airplanecont)
    add.appendChild(shiftscont)
  }


// EVENTS
const upgradeEvent =
`<h2>Upgrade your airplane</h2> <ol class="planes">
<li class="plane1"><a>Name: Lilla Damen 22, Distance: 300, Selection: 4, Factor: 1, Price: 0 €</li>
<li class="plane2"><a>Name: Stor Dam 23, Distance: 450, Selection: 5, Factor: 1.4, Price: 25 000 €</li>
<li class="plane3"><a>Name: Nanny 24, Distance: 600, Selection: 6, Factor: 1.6, Price: 60 000 €</li>
<li class="plane4"><a>Name: Mamma Birgitta 24, Distance: 1500, Selection: 7, Factor: 2, Price: 100 000 €</li>
</ol>`;


////////////// FUNCTIONS
//This will keep your score in time and check when the game end.
function getList(evt) {
  const list = document.querySelector('#destination-list');

  let id = '';
  if (evt.target.id.startsWith('port')) {
    id = evt.target.id.split('_').pop();
  } else if (evt.target.parentElement.id.startsWith('port')) {
    id = evt.target.parentElement.id.split('_').pop();
  }
  console.log(id);
  moveTo(id);
}

async function player_stats(){
  const data_get = await fetch(`http://localhost:3000/player_stats/${player_name}`)
  const data = await data_get.json()
  if (data['status']==='end'){

    end_script(data['money'], data['name'], data['type'], data['shifts'])
  } else {
    console.log(data)
    statsWindow(data['money'], data['name'], data['type'], data['shifts'])
  }}


//This -1 for your shifts
async function shifts_gone(){
  const shift = await  fetch(`http://localhost:3000/shifts_remain/${player_name}`)
}

async function upgrade_airplane_md(plane){
  const data = await fetch(`http://localhost:3000/upgrade_airplane/${plane}/${player_name}`);
  const message = await data.json();

  console.log(message['text']);
  console.log(message['money_remaining']);
  closeEventWindow()
  await player_stats()

}

// findPorts function
// update destination-list
async function findPorts(direction) {
  const airports = await fetch(
    `http://localhost:3000/find-ports?player=${player_name}&direction=${direction}`
  );
  const response = await airports.json();
  console.log(response);
  if (response === 'Too few airports') {
    alert('Too few airports');
  } else {
    await rewardList(response);
    await markDestinationList(response);
    await markMap(response);
    await refreshDestinationListener();
  }
  return response[0];
}

async function moveTo(ident) {
  const destination = await fetch(
    `http://localhost:3000/move-to/${player_name}/${ident}`
  )
  await shifts_gone()
  await player_stats()
}

function markDestinationList(airports) {
  destinationList.innerHTML = '';
  console.log('destination list airports length', airports.length);
  for (let i = 0; i < airports.length; i++) {
    destinationList.innerHTML += 
      `<li id="port_${airports[i]["ident"]}"><div>${airports[i]["ident"]}</div> 
      <div id="airport-name">${airports[i]["name"]}</div></li>`
  }
}

function rewardList(airports){

}

function markMap(airports) {
  for (let i = 0; i < airports.length; i++) {
    L.marker([airports[i]["lat"], airports[i]["long"]]).addTo(map)
    .bindPopup(airports[i]["name"])
    .openPopup();
  }
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
  const list = document.querySelector('#destination-list')
  list.removeEventListener('click', getList, false);
  list.addEventListener('click', getList, false)

}

/////////// KEYBINDS

document.addEventListener('keydown', async function(evt) {
  console.log(evt.key);
});
