// MAIN.JS

////////////// VARIABLES

const upgradeButton = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');
const backButton = document.querySelector('#back');
const closeEvent = document.querySelector('#close-event');

let player_name = `tester`;

let nextTurn = true;



//Do not remove that array
let airport_data = [];
player_stats();

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

async function find_name(){
  const response = await fetch(`http://localhost:3000/get_name`)
  const name = await response.json()
  console.log(name)
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


async function end_script(money, name, type, shifts, location) {
  const endscreen = `<div id="end">
<h1 class="end_title">GAME OVER!   SHIFTS REMAIN ${shifts}</h1>
<h2 class="end2_title">Here is your companys ${name} stats: </h2>
<li class="end_stats"><a>Money got: ${money}</a></li>
<li class="end_stats"><a>Plane typy at the end: ${type}</a></li>
<li class="end_stats"><a>Last location: ${location}</a></li>
<button id="restart-button">Restart Game</button>
</div>`

  const endWindow = document.querySelector('#game-container');
  endWindow.innerHTML = endscreen

  document.querySelector('#restart-button').addEventListener('click', () => {
    restartGame()
  })

}

//This upgrade statswindow
function statsWindow(money, name, airplane, shifts, location){


    const add = document.querySelector('#stats-item')

    add.innerHTML = ''

    const namecont = document.createElement('li')
    namecont.textContent = `Location: ${location}`

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
`<h2 class="upgrade_title">Upgrade your airplane</h2> <ol class="planes">
<li class="plane1"><a>Name: Lilla Damen 22, Distance: 300, Selection: 4, Factor: 1, Price: 0 €</li>
<li class="plane2"><a>Name: Stor Dam 23, Distance: 450, Selection: 5, Factor: 1.4, Price: 25 000 €</li>
<li class="plane3"><a>Name: Nanny 24, Distance: 600, Selection: 6, Factor: 1.6, Price: 60 000 €</li>
<li class="plane4"><a>Name: Mamma Birgitta 24, Distance: 1500, Selection: 7, Factor: 2, Price: 100 000 €</li>
</ol>`;


////////////// FUNCTIONS
async function createCompany(name) {

//  localStorage.setItem('playerName', name);

  if (name) {
      await fetch('http://localhost:3000/save_name', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ name: name })
      })
      .then(response => response.text())
      .catch(error => {
          console.error('Error saving name:', error);
          alert("Could not save name.");
      });
  } else {
      alert("Name is required to start the game.");
  }
}



async function newmoney(money) {
  money = parseInt(money["reward"])
  console.log(money)
  await fetch(`http://localhost:3000/add_money/${player_name}/${money}`)
}



function getList(evt) {
console.log(evt)

    let id = '';
    if (evt.target.id.startsWith('port')) {
      id = evt.target.id.split('_').pop();
    } else if (evt.target.parentElement.id.startsWith('port')) {
      id = evt.target.parentElement.id.split('_').pop();
    }
    const money = airport_data.find(x => x.ident === id)

    console.log(id);
    moveTo(id, money);

  }


  async function player_stats() {
    const data_get = await fetch(
        `http://localhost:3000/player_stats/${player_name}`)
    const data = await data_get.json()
    if (data['status'] === 'end') {

      end_script(data['money'], data['name'], data['type'], data['shifts'], data['location'])
    } else {
      console.log(data)
      statsWindow(data['money'], data['name'], data['type'], data['shifts'], data['location'])
    }
  }

//This -1 for your shifts
  async function shifts_gone() {
    await fetch(`http://localhost:3000/shifts_remain/${player_name}`)
  }

  async function upgrade_airplane_md(plane) {
    const data = await fetch(
        `http://localhost:3000/upgrade_airplane/${plane}/${player_name}`);
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
      airport_data = response
      console.log(airport_data)

      await markDestinationList(response);
      await markMap(response);
      await refreshDestinationListener()

    }
    return response[0];
  }

  async function moveTo(ident, money) {
    await fetch(`http://localhost:3000/move-to/${player_name}/${ident}`
    )
    await newmoney(money)
    await shifts_gone()
    await player_stats()
  }

  function markDestinationList(airports) {
    destinationList.innerHTML = '';
    console.log('destination list airports length', airports.length);
    for (let i = 0; i < airports.length; i++) {
      destinationList.innerHTML +=
          `<li id="port_${airports[i]["ident"]}"><div>${airports[i]["ident"]}</div> 
      <div id="airport-name">${airports[i]["name"]}</div><div id="reward">${parseInt(
              airports[i]["reward"])}€</div></li>`

    }
  }


currentMark()
  function currentMark() {
    const currentLayer = new L.LayerGroup()

    currentMark = new L.marker([50, 50], {icon: redicon})
    currentLayer.addLayer(currentMark)
    map.addLayer(currentLayer)
  }
  function markMap(airports) {

      const destinationLayer = new L.LayerGroup()
      //destinationLayer.clearLayers(destinationMark);
      for (let i = 0; i < airports.length; i++) {
          destinationMark = new L.marker([airports[i]["lat"], airports[i]["long"]], {icon: greenicon})
          destinationLayer.addLayer(destinationMark)
          map.addLayer(destinationLayer)
          destinationMark.bindPopup(airports[i]["name"])
          console.log(airports.length)
      }
  }



//////////// BUTTONS

document.querySelector('#new-company').addEventListener('click', function(){
  player_name = prompt('Enter company name')
  createCompany(player_name);
  document.querySelector('#companyName').textContent = player_name;
});


upgradeButton.addEventListener('click', function(evt) {
    eventWindow(upgradeEvent);

    const planeitem = document.querySelectorAll('#event-window .planes li')

    planeitem.forEach(item => {
      item.addEventListener('click', () => {
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

async function restartGame() {
  try {
    const response = await fetch(`http://localhost:3000/delete_rows`)
    if (response.ok) {
      alert('Game restarted')
      window.location.href = 'index.html'
    } else {
      alert('Fail when trying to open game')
    }
  } catch (error) {
    console.error('Error:', error)

  }
}


/////////// KEYBINDS

document.addEventListener('keydown', async function(evt) {
  console.log(evt.key);
});
