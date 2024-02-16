console.log('location_search.js loaded...!')

$(document).ready(function () {
    var autocomplete;
    var search_location = document.getElementById('id_search_location');
    
    autocomplete = new google.maps.places.Autocomplete((search_location), {
        types: ['geocode'],
    });

    
});