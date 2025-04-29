// MAIN.JS

// update destination-list
// (by clicking upgrade button, temporary)

const upgrade = document.querySelector('#upgrade');
const destinationList = document.querySelector('#destination-list');

upgrade.addEventListener('click', async function(evt) {
  let airports = await fetch('http://localhost:3000/find-ports?location=efhk&direction=E');
  airports = await airports.json();
  console.log(airports);
  destinationList.innerHTML = '';
  for (let i=0; i < airports.length; i++) {
    destinationList.innerHTML 
      += `<li id="port-${i}">${airports[i]["ident"]} .. ${airports[i]["name"]}</li>`
  }
});
