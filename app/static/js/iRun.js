var geoJSON = [];
var latlngs = [];
var bounds = [[42.3063, -71.1389], [42.4014, -70.9355]];
var LineStringOpt = {color : 'red', opacity : 0.5, weight : 4};
var paths = [];
var accessToken = 'pk.eyJ1Ijoic3VtbWVyemhlbmciLCJhIjoiYVJ6R2RPayJ9.KSHYtaGYnIpQuoo9tJ3-Uw';
var message = '';

function Load() {
    // Initialize MapBox map<script>
    L.mapbox.accessToken = accessToken;
    map = L.mapbox.map('map', 'summerzheng.j3lod7k8').setView([42.32, -71.0], 12);
};


function ShowLoading(showLoading) {
    if (showLoading) {
        $('#loading').css('visibility', 'visible');
    } else {
        $('#loading').css('visibility', 'hidden');
    };
};


function ResetMap(){
    // Reset pan and zoom
    geoJSON = [];
    map.featureLayer.setGeoJSON(geoJSON);
    map.fitBounds(bounds);
};


function FindAndRoute(startPt, endPt, runDis){
   ShowLoading(true);
   message = '';
   $('#addmessage').html(message);
   $.getJSON('/findRoute', {'s': startPt,'e': endPt,'d':runDis}, function(findJSON){         
          // Maybe reset on bad query
          ShowLoading(false);
          if (findJSON != {}) {             
             console.log('after finding the path');
             message = findJSON['message'];
             $('#addmessage').html(message); 
             geoJSON.push(findJSON['path']);   
             map.featureLayer.setGeoJSON(geoJSON);        
             latlngs = geoJSON[0]['geometry']['coordinates']
             var polyline = L.polyline(latlngs, LineStringOpt).addTo(map);          
             //Pan and zoom                        
             map.fitBounds(findJSON['bounds']);
          }else{
             message = 'Path not found! Please check your address, and make sure they are within the blue boundary of Cambridge and Boston.' 
             $('#addmessage').html(message);
          }
   });      
};

function PathSearch() {
    // Grab address box valuePathTestMashUp
    var startPt = $('#startPt').val();
    console.log('Inside PathSearch');
    console.log(startPt);
    var endPt = $('#endPt').val();
    console.log(endPt);
    var runDis = $('#runDist').val();
    console.log(runDis);
    // Reset map ...
    ResetMap();
    // If it is not empty ...
    if (endPt == 'default = start') {
        // ... and find and route
        document.getElementById("endPt").value=document.getElementById("startPt").value;
        FindAndRoute(startPt, startPt, runDis);//FIXME: no runLoop fun implemented yet
    }else{
        console.log('prepare to run find and route');
        FindAndRoute(startPt, endPt, runDis);
    }
	
};

