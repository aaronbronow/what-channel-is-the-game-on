/** Things the script needs to do
 * determine if browser supports location awareness
 * get coords from google with user input
 * get channel from our service with coords
 * render content
*/

var wcitgo = {
	isLoading:false,
	init:function(){
		this.bindEvents();
		
		// this.getLatLonFromIP();
	},
	bindEvents:function(){
		if(navigator.geolocation){
			$("#find-me").show();
		}
		
		$("#find").click(function(){
			if (navigator.geolocation) {
				$("#loader").show();
				$("#channel").text("checking...");
				locationThread = setTimeout(function(){
					navigator.geolocation.getCurrentPosition(success, error);
				}, 500);
			  
			} else {
			 	$("#loader").hide();
			  	error('not supported');
			}
		});
		
		$("#search").click(function(){
			if(!wcitgo.isLoading){
				var q = $("#zip").val();
				if(q.length < 1){
					return false;
				}
				wcitgo.startLoading();
				wcitgo.getLatLon(q);
			}
			return false;
		});
		
		$("#form").submit(function(){0
			if(!wcitgo.isLoading){
				var q = $("#zip").val();
				if(q.length < 1){
					return false;
				}
				wcitgo.startLoading();
				wcitgo.getLatLon(q);
			}
			return false;
		});
	},
	startLoading:function(){
		wcitgo.isLoading = true;
		$("#loader").show();
		$("#channel").text("checking...");
	},
	getLatLon:function(q){
		var geocoder = new google.maps.Geocoder();
		geocoder.geocode({address: q}, function(response){
			if(!response){
				alert("err");
			}else{
				// var zip = null;
				// 
				// 				$.each(response, function(placeIndex, place){
				// 					if($.inArray("postal_code", place.types) > -1){
				// 						$.each(place.address_components, function(addressIndex, address){
				// 							if($.inArray("postal_code", address.types) > -1){
				// 								zip = address.long_name;
				// 								return false;
				// 							}
				// 						});
				// 						return false;
				// 					}
				// 				});
				// 
				// 				var zipInput = document.querySelector('#zip');
				// 
				// 				zipInput.value = zip;

				
				wcitgo.getChannel(response[0].geometry.location.xa + "," + response[0].geometry.location.za);
			}

		});
	},
	getChannel:function(latlon){
		$.getJSON("/channels?latlon=" + latlon, function(data){
			if(data.status == "OK") {
				$("#channel").text(data.virtual);
				$("#tweet").attr("data-text", "I'm watching the #SuperBowl on FOX " + data.virtual);
				var scriptElement = document.createElement("script");
				scriptElement.src = "http://platform.twitter.com/widgets.js";
			
				document.body.appendChild(scriptElement);
			}else{
				$("#channel").text("not found");
			}
			
			wcitgo.navigateToScreen2();
		});
	},
	navigateToScreen2:function(){
		$("#screen1").fadeTo("fast", 0, function(){
			wcitgo.isLoading = false;
			
			$("#screen1").hide();
			
			$("div#ad").show();
			$("#screen2").fadeTo("fast", 1);
		});
	}
	// ,
	// 	getLatLonFromIP:function(){
	// 		$.getJSON("/location", function(data){
	// 			if(data.status && data.status == "OK"){
	// 				$("#guess-me").show();
	// 				$("#guess").text(data.latlon);
	// 			}
	// 		});
	// 	}
};

function error(msg) {
  var s = document.querySelector('#channel');
  s.innerHTML = typeof msg == 'string' ? msg : "channel unknown";
  s.className = 'fail';
  wcitgo.navigateToScreen2();

  // var zip = $("#zip").val();
  // 		
  // 		  if(zip.length == 5){
  // 			getChannelByZip(zip);
  // 		  
  // 		  }
  // console.log(arguments);
}

function success(position) {
  var s = document.querySelector('#channel');
	//var zipInput = document.querySelector('#zip');
	
  if (s.className == 'success') {
    // not sure why we're hitting this twice in FF, I think it's to do with a cached result coming back    
    return;
  }

  s.innerHTML = "found you!";
  s.className = 'success';

  // var mapcanvas = document.createElement('div');
  // 		  mapcanvas.id = 'mapcanvas';
  // 		  mapcanvas.style.height = '400px';
  // 		  mapcanvas.style.width = '560px';
  // 
  // 		  document.querySelector('article').appendChild(mapcanvas);

  var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
  // var myOptions = {
  // 		    zoom: 15,
  // 		    center: latlng,
  // 		    mapTypeControl: false,
  // 		    navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
  // 		    mapTypeId: google.maps.MapTypeId.ROADMAP
  // 		  };
  // 		  var map = new google.maps.Map(document.getElementById("mapcanvas"), myOptions);
  // 
  // 		  var marker = new google.maps.Marker({
  // 		      position: latlng, 
  // 		      map: map, 
  // 		      title:"You are here!"
  // 		  });

	var geocoder = new google.maps.Geocoder();
	geocoder.geocode({location: latlng}, function(response){
		if(!response){
			alert("err");
		}else{
			// var zip = null;
			// 			
			// 			$.each(response, function(placeIndex, place){
			// 				if($.inArray("postal_code", place.types) > -1){
			// 					$.each(place.address_components, function(addressIndex, address){
			// 						if($.inArray("postal_code", address.types) > -1){
			// 							zip = address.long_name;
			// 							return false;
			// 						}
			// 					});
			// 					return false;
			// 				}
			// 			});
			// 			
			// 			
			// 			zipInput.value = zip;
			
			wcitgo.getChannel(latlng.xa + "," + latlng.za);
		}
	
	});
	
	// geocoder.getLocations(latlng, function(response){
	// 				if (!response || response.Status.code != 200) {
	// 			    alert("Status Code:" + response.Status.code);
	// 			  } else {
	// 			    place = response.Placemark[0];
	// 				var zipcode = place.AddressDetails.Country.AdministrativeArea.Locality.PostalCode.PostalCodeNumber;
	// 				
	// 			    //alert(place.AddressDetails.Country.CountryNameCode);
	// 			  }
	// 			});
}





// function getChannel(latlng){
// 			$("#channel").load("/channels?latlng=" + latlng.wa + "," + latlng.ya, function(data){
// 				$("div#ad").show();
// 			});
// 			
// 		}

// function getChannelByZip(zip){
// 			$.get("/location?zip=" + zip, function(data){
// 				d = data.split(",");
// 				var latlng = new google.maps.LatLng(d[0], d[1]);
// 				
// 				
// 				getChannel(latlng);
// 			});
// 		}

$(document).ready(function(){
	wcitgo.init();
});
