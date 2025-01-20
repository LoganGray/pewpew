// /*****************************
//  * GLOBAL CONFIGURATION
//  *****************************/

// Attack timing configuration (in milliseconds)
const attack_min = 100;  // Minimum time between attacks
const attack_max = 2000; // Maximum time between attacks

// List of possible attack types that will be randomly selected
// These are displayed in the attack log and attack bubbles
const attack_types = [
  "any port scan in a storm", 
  "ssh brutish force", 
  "Thought Leader Tweet",
  "SYN FLOOD BA-BY", 
  "Spotty", 
  "Heartbleed Hotel", 
  "Po_ODLE", 
  "Sharknado",
  "CORGI Attack", 
  "Ping of DOOM", 
  "Conficker", 
  "Goldfinger", 
  "SANDPAPER",
  "SNAILshock", 
  "Spaghetti RAT", 
  "Driduplex"
];

// Available sound effects for attacks
// Each corresponds to an audio element in index.html
// Can be triggered by URL parameters or randomly with allfx
const audio_types = [
  "starwars", 
  "tng", 
  "b5", 
  "wargames", 
  "pew", 
  "galaga", 
  "asteroids", 
  "china", 
  "timallen"
];

// Available sound effects for attacks
// Each corresponds to an audio element in index.html
// Can be triggered by URL parameters or randomly with allfx
audio_type = ["starwars", "tng", "b5", "wargames", "pew", "galaga", "asteroids", "china", "timallen"];

/*****************************
 * URL PARAMETER HANDLING
 *****************************/

/**
 * jQuery extension to parse URL parameters
 * Allows easy access to configuration options passed in URL
 * Example: ?norse_mode=1&bad_day=1&org_name=MyCompany
 */
$.extend({
  /**
   * Returns an object containing all URL parameters
   * @returns {Object} Key-value pairs of URL parameters
   */
  getUrlVars: function() {
    const vars = [];
    const hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    
    for(let i = 0; i < hashes.length; i++) {
      const hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  },
  
  /**
   * Returns the value of a specific URL parameter
   * @param {string} name - The parameter name to retrieve
   * @returns {string|undefined} The parameter value or undefined if not found
   */
  getUrlVar: function(name) {
    return this.getUrlVars()[name];
  }
});

/*****************************
 * URL PARAMETER PROCESSING
 *****************************/

// Extract all URL parameters
const urlParams = {
  norse_mode: $.getUrlVar('norse_mode'),
  bad_day: $.getUrlVar('bad_day'),
  org_name: $.getUrlVar('org_name'),
  chatt_mode: $.getUrlVar('chatt_mode'),
  china_mode: $.getUrlVar('china_mode'),
  dprk_mode: $.getUrlVar('dprk_mode'),
  employee_mode: $.getUrlVar('employee_mode'),
  employee_fname: $.getUrlVar('employee_fname'),
  employee_lname: $.getUrlVar('employee_lname'),
  origin: $.getUrlVar('origin'),
  random_mode: $.getUrlVar('random_mode'),
  tng: $.getUrlVar('tng'),
  wargames: $.getUrlVar('wargames'),
  b5: $.getUrlVar('b5'),
  nofx: $.getUrlVar('nofx'),
  pew: $.getUrlVar('pew'),
  allfx: $.getUrlVar('allfx'),
  galaga: $.getUrlVar('galaga'),
  asteroids: $.getUrlVar('asteroids'),
  china: $.getUrlVar('china'),
  timallen: $.getUrlVar('timallen'),
  drill_mode: $.getUrlVar('drill_mode'),
  in_lat: $.getUrlVar('lat'),
  in_lon: $.getUrlVar('lon'),
  destination: $.getUrlVar('destination'),
  greenattacks: $.getUrlVar('greenattacks'),
  redattacks: $.getUrlVar('redattacks')
};

// Set default sound effect
let snd_id = "wargames";

// Override sound effect based on URL parameters
const soundMappings = {
  tng: "tng",
  b5: "b5",
  wargames: "wargames",
  pew: "pew",
  galaga: "galaga",
  asteroids: "asteroids",
  china: "china",
  timallen: "timallen"
};

for (const [param, sound] of Object.entries(soundMappings)) {
  if (typeof urlParams[param] !== 'undefined') {
    snd_id = sound;
    break;
  }
}

// Handle special modes
if (typeof urlParams.bad_day !== 'undefined') {
  attack_min = 200;
  attack_max = 200;
}

if (typeof urlParams.org_name !== 'undefined') {
  $("#titlediv").text(decodeURI(urlParams.org_name) + " IPew Attack Map").html();
}

// we maintain a fixed queue of "attacks" via this class
function FixedQueue(size, initialValues) {
  initialValues = (initialValues || []);
  var queue = Array.apply(null, initialValues);
  queue.fixedSize = size;
  queue.push = FixedQueue.push;
  queue.splice = FixedQueue.splice;
  queue.unshift = FixedQueue.unshift;
  FixedQueue.trimTail.call(queue);
  return(queue);
}

FixedQueue.trimHead = function() {
  if (this.length <= this.fixedSize){ return; }
  Array.prototype.splice.call(this, 0, (this.length - this.fixedSize));
};

FixedQueue.trimTail = function() {
  if (this.length <= this.fixedSize) { return; }
  Array.prototype.splice.call(this, this.fixedSize, (this.length - this.fixedSize));
};

FixedQueue.wrapMethod = function(methodName, trimMethod) {
  var wrapper = function() {
    var method = Array.prototype[methodName];
    var result = method.apply(this, arguments);
    trimMethod.call(this);
    return(result);
  };
  return(wrapper);
};

FixedQueue.push = FixedQueue.wrapMethod("push", FixedQueue.trimHead);
FixedQueue.splice = FixedQueue.wrapMethod("splice", FixedQueue.trimTail);
FixedQueue.unshift = FixedQueue.wrapMethod("unshift", FixedQueue.trimTail);

var rand = function(min, max) {
  return Math.random() * (max - min) + min;
};

var getRandomCountry = function(countries, weight) {
  var total_weight = weight.reduce(function (prev, cur, i, arr) {
    return prev + cur;
  });

  var random_num = rand(0, total_weight);
  var weight_sum = 0;

  for (var i = 0; i < countries.length; i++) {
    weight_sum += weight[i];
    weight_sum = +weight_sum.toFixed(2);

    if (random_num <= weight_sum) {
      return countries[i];
    }
  }
};

// need to make this dynamic since it is approximated from sources
var countries = [9,22,29,49,56,58,78,82,102,117,139,176,186];
var weight = [0.000,0.001,0.004,0.008,0.009,0.037,0.181,0.002,0.000,0.415,0.006,0.075,0.088];

/*****************************
 * DATA MANAGER
 *****************************/

class DataManager {
  /**
   * Record a new attack in the database
   * @param {Object} attackData - The attack data to record
   */
  static async recordAttack(attackData) {
    try {
      const response = await fetch(`${API_URL}/api/attacks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(attackData)
      });
      
      if (!response.ok) {
        console.error('Failed to record attack:', response.statusText);
      }
    } catch (error) {
      console.error('Error recording attack:', error);
    }
  }

  /**
   * Get attack statistics from the API
   * @returns {Promise<Object>} Attack statistics
   */
  static async getStats() {
    try {
      const response = await fetch(`${API_URL}/api/stats`);
      return await response.json();
    } catch (error) {
      console.error('Error getting stats:', error);
      return null;
    }
  }

  /**
   * Get recent attacks from the API
   * @param {number} limit - Maximum number of attacks to retrieve
   * @returns {Promise<Array>} Array of recent attacks
   */
  static async getRecentAttacks(limit = 100) {
    try {
      const response = await fetch(`${API_URL}/api/attacks?limit=${limit}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting recent attacks:', error);
      return [];
    }
  }

  /**
   * Get geo location for an IP address
   * @param {string} ip - IP address to lookup
   * @returns {Promise<Object>} Geo location data
   */
  static async getGeoLocation(ip) {
    try {
      const response = await fetch(`${API_URL}/api/ip2geo?ip=${ip}`);
      return await response.json();
    } catch (error) {
      console.error('Error getting geo location:', error);
      return null;
    }
  }
}

/*****************************
 * WEBSOCKET CONNECTION
 *****************************/
const socket = io(API_URL);
console.log('API_URL:', API_URL);
// Track last destination to avoid duplicate messages
let lastDestination = null;
let lastDemoStatus = null;

// Check demo mode status on page load
fetch(`${API_URL}/api/demo/status`)
  .then(response => response.json())
  .then(data => {
    if (data.demo_mode) {
      $('#attackdiv').append(
        `<span style="color:yellow">DEMO MODE IS ON</span><br/>`
      );
      $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
    }
    lastDemoStatus = data.demo_mode;
  })
  .catch(error => {
    console.error('Error getting demo status:', error);
  });

// Handle demo mode changes
socket.on('demo_mode_change', function(status) {
  if (lastDemoStatus !== status.demo_mode) {
    const message = status.demo_mode ? 
      `<span style="color:yellow">DEMO MODE IS ON</span><br/>` : 
      `<span style="color:yellow">DEMO MODE IS OFF</span><br/>`;
    
    $('#attackdiv').append(message);
    $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
    lastDemoStatus = status.demo_mode;
  }
});

socket.on('destination_change', function(dest) {
    // Only show message if destination actually changed
    if (!lastDestination || lastDestination.ip !== dest.ip) {
        // Get geo location for the new destination IP
        fetch(`${API_URL}/api/ip2geo?ip=${dest.ip}`)
            .then(response => response.json())
            .then(geo => {
                const location = geo.city ? `${geo.city}, ${geo.country}` : geo.country;
                const destStatus = dest.is_default ? 
                    `Using default destination ${dest.ip} (${location})` : 
                    `Destination set to ${dest.ip} (${location})`;
                
                $('#attackdiv').append(
                    `<span style="color:yellow">${destStatus}</span><br/>`
                );
                $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
                lastDestination = dest;
            })
            .catch(error => {
                console.error('Error getting destination location:', error);
                // Fallback to IP only if geo lookup fails
                const destStatus = dest.is_default ? 
                    `Using default destination ${dest.ip}` : 
                    `Destination set to ${dest.ip}`;
                
                $('#attackdiv').append(
                    `<span style="color:yellow">${destStatus}</span><br/>`
                );
                $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
                lastDestination = dest;
            });
    }
});

socket.on('new_attack', function(attack) {
    // Convert attack data to visualization format
    const attackData = {
        origin: {
            latitude: attack.geo.latitude,
            longitude: attack.geo.longitude
        },
        destination: {
            latitude: attack.dest_geo.latitude,
            longitude: attack.dest_geo.longitude
        },
        attack_type: attack.attack_type,
        source_ip: attack.source_ip,
        dest_ip: attack.dest_ip
    };
    
    // Visualize the attack
    hits.push({
        origin: attackData.origin,
        destination: attackData.destination
    });
    map.arc(hits, {strokeWidth: 2, strokeColor: 'red'});

    // Add boom effect
    boom.push({
        radius: 7,
        latitude: attackData.destination.latitude,
        longitude: attackData.destination.longitude,
        fillOpacity: 0.5,
        attk: attackData.attack_type
    });
    map.bubbles(boom, {
        popupTemplate: function (geo, data) {
            return '<div class="hoverinfo">' + data.attk + '</div>';
        }
    });

    // Update attack log with city and country information
    const originLocation = attack.geo.city ? `${attack.geo.city}, ${attack.geo.country}` : attack.geo.country;
    const destLocation = attack.dest_geo.city ? `${attack.dest_geo.city}, ${attack.dest_geo.country}` : attack.dest_geo.country;
    
    // Display the attack
    $('#attackdiv').append(
      originLocation + " (" + attackData.source_ip + ") " +
      " <span style='color:red'>attacks</span> " +
      destLocation + " (" + attackData.dest_ip + ") " +
      " <span style='color:steelblue'>(" + attackData.attack_type + ")</span> " +
      "<br/>"
    );
    $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
});

/*****************************
 * ATTACK VISUALIZATION
 *****************************/
function visualizeAttack(attack) {
    // Add hit to the arc queue
    hits.push({
        origin: attack.origin,
        destination: attack.destination
    });
    map.arc(hits, {strokeWidth: 2, strokeColor: 'red'});

    // Add boom to the bubbles queue
    boom.push({
        radius: 7, 
        latitude: attack.destination.latitude,
        longitude: attack.destination.longitude,
        fillOpacity: 0.5, 
        attk: attack.attack_type
    });
    map.bubbles(boom, {
        popupTemplate: function (geo, data) {
            return '<div class="hoverinfo">' + data.attk + '</div>';
        }
    });

    // Update the scrolling attack div
    $('#attackdiv').append(
        attack.origin.country + " (" + attack.source_ip + ") " +
        " <span style='color:red'>attacks</span> " +
        attack.destination.country + " (" + attack.dest_ip + ") " +
        " <span style='color:steelblue'>(" + attack.attack_type + ")</span> " +
        "<br/>"
    );
    $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
}

/*****************************
 * MAIN APPLICATION
 *****************************/

var map = new Datamap({
  scope: 'world',
  element: document.getElementById('container1'),
  projection: 'winkel3',
  // change the projection to something else only if you have absolutely no cartographic sense

  fills: { defaultFill: 'black', },

  geographyConfig: {
    dataUrl: null,
    hideAntarctica: true,
    borderWidth: 0.75,
    borderColor: '#4393c3',
    popupTemplate: function(geography, data) {
      return '<div class="hoverinfo" style="color:white;background:black">' +
             geography.properties.name + '</div>';
    },
    popupOnHover: true,
    highlightOnHover: false,
    highlightFillColor: 'black',
    highlightBorderColor: 'rgba(250, 15, 160, 0.2)',
    highlightBorderWidth: 2
  },
});

// Load geographic data files
var centers = [];
d3.tsv("country_centroids_primary.csv", function(data) { centers = data; });  // Country center points
d3.csv("samplatlong.csv", function(data) { slatlong = data; });              // Sample lat/long pairs
d3.csv("cnlatlong.csv", function(data) { cnlatlong = data; });               // China-specific coordinates

// Initialize fixed-size queues for visual effects
var hits = FixedQueue(7, []);  // Stores the last 7 attack arcs (lines between points)
var boom = FixedQueue(7, []);  // Stores the last 7 explosion effects (circles at target)

// Utility functions for generating random values
function getRandomInt(min, max) {return Math.floor(Math.random() * (max - min + 1)) + min;}  // Random integer in range
function getOctet() {return Math.round(Math.random()*255);}                                   // Random IP octet (0-255)
function randomIP() { return(getOctet() + '.' + getOctet() + '.' + getOctet() + '.' + getOctet()); }  // Random IP address
function getStroke() {return Math.round(Math.random()*100);}                                  // Random number for attack color
function getDestination() {return Math.round(Math.random()*100);}                            // Random number for destination selection

// doing this a bit fancy for a hack, but it makes it
// easier to group code functions together and have variables
// out of global scope
var attacks = {
  interval: getRandomInt(attack_min, attack_max),

  init: function() {
    // Check if demo mode is enabled via API
    fetch(`${API_URL}/api/demo/status`)
      .then(response => response.json())
      .then(data => {
        if (data.demo_mode) {
          setTimeout(
            jQuery.proxy(this.getData, this),
            this.interval
          );
        }
      });
  },

  getData: function() {
    var self = this;

    if (typeof norse_mode !== 'undefined') { return; }

    if (typeof random_mode !== 'undefined') { Math.floor((Math.random() * slatlong.length)); }

    dst = Math.floor((Math.random() * slatlong.length));
    src = Math.floor((Math.random() * slatlong.length));

    if ((dst == src)) {
      dst = src + 1;
      if (dst > slatlong.length-1) { dst = src - 1 }
    }

    if (typeof allfx !== 'undefined') {
      snd_id = audio_type[Math.floor((Math.random() * audio_type.length))];
    }
    // no guarantee of sound playing w/o the load - stupid browsers
    if (typeof nofx === 'undefined') {
      document.getElementById(snd_id).load();
      document.getElementById(snd_id).play();
    }

    // add hit to the arc queue
    // use strokeColor to set arc line color

    var srclat = slatlong[src].lat;
    var srclong = slatlong[src].long;
    var dstlat = slatlong[dst].lat;
    var dstlong = slatlong[dst].long;
    which_attack = attack_type[Math.floor((Math.random() * attack_type.length))];
    var srccountry = slatlong[src]["country"];
    // "Hi, Mandiant!!"
    if (typeof china_mode !== 'undefined') {
      srclat = cnlatlong[src].lat;
      srclong = cnlatlong[src].long;
      if (cnlatlong[src].country=="chn") { which_attack = "ZOMGOSH CHINA!!!!!!"; }
      srccountry = cnlatlong[src]["country"];
    }
    // "Hi, Kim Jong!"
    else if (typeof dprk_mode !== 'undefined') {
      srclat = 39.0194;
      srclong = 125.7381;
      which_attack = "ZOMG NORTH KOREAZ!!!";
      srccountry = "kp";
    }
    // source is always Chattanooga if chatt_mode is set
    // "Hi ThreatStream!!" http://www.csoonline.com/article/2689609/network-security/threat-intelligence-firm-mistakes-research-for-nation-state-attack.html
    else if (typeof chatt_mode !== 'undefined') {
      srclat = 35.0456297;
      srclong = -85.30968;
      which_attack = "OMG NATION STATE CHATTANOOGA!!!";
      srccountry = "usa";
    }
    // blame a former employee
    else if (typeof employee_mode !== 'undefined') {
      if (typeof in_lat !== 'undefined' && typeof in_lon !== 'undefined') {
        srclat = in_lat;
        srclong = in_lon;
      }
      which_attack = "Former employee attack"
      if (typeof employee_fname !== 'undefined' && typeof employee_lname !== 'undefined') {
        which_attack += ":" + employee_fname + " " + employee_lname;
      }
      srccountry = "usa";
    }

    // Specify a country
    else if (typeof origin !== 'undefined') {
      srccountry = origin.toUpperCase();
      var center_id = 0;
      for (i = 0; i < centers.length; i ++) {
        center_id = i;
        if (centers[i].FIPS10 === srccountry) {
          break;
        }
      }

      srccountry = origin.toLowerCase();
      srclat = centers[center_id].LAT;
      srclong = centers[center_id].LONG;
    }

    // Specify a destination country
    if (typeof destination !== 'undefined' && getDestination() < 80) {
      dstcountry = destination.toUpperCase();
      var center_id = 0;
      for (i = 0; i < centers.length; i ++) {
        center_id = i;
        if (centers[i].FIPS10 === dstcountry) {
          break;
        }
      }

      dstcountry = destination.toLowerCase();
      attackdiv_slatlong = dstcountry;
      dstlat = centers[center_id].LAT;
      dstlong = centers[center_id].LONG;
    }
    else {
      attackdiv_slatlong = slatlong[dst]["country"];
    }

    // Specify attack color
    if (typeof greenattacks !== 'undefined') {
      strokeColor = 'green';
    }
    else if (typeof redattacks !== 'undefined') {
      strokeColor = 'red';
    }
    else {
      if (getStroke() < 70) {
        strokeColor = 'green';
      }
      else {
        strokeColor = 'red';
      }
    }

    if (typeof drill_mode != 'undefined') {
      dstlat = in_lat
      dstlong = in_lon
    }

    //only attempt to queue draws if the page is not hidden;
    //trying to draw while the page is hidden causes the JS heap to balloon rapidly
    if(!document.hidden) {
      hits.push({
        origin: {latitude: +srclat, longitude: +srclong},
        destination: {latitude: +dstlat, longitude: +dstlong}
      });
      map.arc(hits, {strokeWidth: 2, strokeColor: strokeColor});

      // add boom to the bubbles queue
      boom.push({
        radius: 7, latitude: +dstlat, longitude: +dstlong,
        fillOpacity: 0.5, attk: which_attack
      });
      map.bubbles(boom, {
        popupTemplate: function (geo, data) {
          return '<div class="hoverinfo">' + data.attk + '</div>';
        }
      });

      // Record attack using DataManager
      const sourceIP = randomIP();
      const destIP = randomIP();
    
      // Visualize the attack
      hits.push({
        origin: {latitude: +srclat, longitude: +srclong},
        destination: {latitude: +dstlat, longitude: +dstlong}
      });
      map.arc(hits, {strokeWidth: 2, strokeColor: strokeColor});

      // Add boom effect
      boom.push({
        radius: 7, latitude: +dstlat, longitude: +dstlong,
        fillOpacity: 0.5, attk: which_attack
      });
      map.bubbles(boom, {
        popupTemplate: function (geo, data) {
          return '<div class="hoverinfo">' + data.attk + '</div>';
        }
      });

      // Record in database
      DataManager.recordAttack({
        source_ip: sourceIP,
        source_country: srccountry,
        source_lat: srclat,
        source_long: srclong,
        dest_ip: destIP,
        dest_country: attackdiv_slatlong,
        dest_lat: dstlat,
        dest_long: dstlong,
        attack_type: which_attack
      });

      // update the scrolling attack div with city and country information
      const originLocation = srccountry; // For random attacks we only have country
      const destLocation = attackdiv_slatlong; // For random attacks we only have country
      
      $('#attackdiv').append(
        originLocation + " (" + sourceIP + ") " +
        " <span style='color:red'>attacks</span> " +
        destLocation + " (" + destIP + ") " +
        " <span style='color:steelblue'>(" + which_attack + ")</span> " +
        "<br/>"
      );
      $('#attackdiv').animate({scrollTop: $('#attackdiv').prop("scrollHeight")}, 500);
    }
    // pick a new random time and start the timer again!
    this.interval = getRandomInt(attack_min, attack_max);
    this.init();
  },
};

// start the ball rolling!
attacks.init();

// lazy-dude's responsive window
d3.select(window).on('resize', function() { location.reload(); });
