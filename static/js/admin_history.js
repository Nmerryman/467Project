$( function() {
    $( "#date1" ).datepicker();
    $( "#date2" ).datepicker();
  } );

  function handleSearch(event) {
    var query = event.target.value;
  
    // Fetch search results and update the page
    fetcher('submit','container', [query], function() {
       // This callback function will be called after the page is updated
       console.log('Page updated with search results for query:', query);
    });
    // TODO: Use the query to search your data and update the page
    console.log('Search query:', query);
  }

function load_orders() {
    // Fetch all orders
    fetcher('api/load_orders', 'container', [], () => {
        console.log('Page updated with all orders!');
    });
}

function openPopup(orderId) {
    var popup = document.getElementById("popup" + orderId);
    console.log(orderId);
    popup.style.display = "block";
}

function closePopup(orderId) {
    var popup = document.getElementById("popup" + orderId);
    popup.style.display = "none";
}

document.getElementById('date-search-form').addEventListener('submit', function(event) {
    // Prevent the form from being submitted normally
    event.preventDefault();

    // Get the start and end dates
    var start_date = document.getElementById('datepicker1').value;
    var end_date = document.getElementById('datepicker2').value;

    // Call the date_search function (you'll define this function next)
    date_search(start_date, end_date);
});

function date_search(start_date, end_date) {
    // Make a GET request to the date_search route
    fetch('/date_search?start_date=' + start_date + '&end_date=' + end_date)
        .then(function(response) {
            // Parse the response as JSON
            return response.json();
        })
        .then(function(orders) {
            // Clear the container
            var container = document.getElementById('container');
            container.innerHTML = '';

            // Loop through the orders and add them to the container
            for (var i = 0; i < orders.length; i++) {
                var order = orders[i];

                // Create a new div for the order
                var orderDiv = document.createElement('div');
                orderDiv.textContent = 'Order ID: ' + order.id + ', Status: ' + order.status;

                // Add the order div to the container
                container.appendChild(orderDiv);
            }
        });
}

function fetcher(call_name, target_id, callback=() => {/* do nothing */}) {
    var xhttp = new XMLHttpRequest;
    var arg_mod = ""

    // Get the search parameters
    var start_date = document.getElementById('start_date').value.replace(/\//g, '-') || '';
    var end_date = document.getElementById('end_date').value.replace(/\//g, '-') || '';
    var status = document.getElementById('status').value || '';
    var min_cost = document.getElementById('min_cost').value || '';
    var max_cost = document.getElementById('max_cost').value || '';

    // Add the search parameters to the arguments
    if (start_date) arg_mod += '&start_date=' + start_date;
    if (end_date) arg_mod += '&end_date=' + end_date;
    if (status) arg_mod += '&status=' + status;
    if (min_cost) arg_mod += '&min_cost=' + min_cost;
    if (max_cost) arg_mod += '&max_cost=' + max_cost;

    xhttp.open("GET", "/" + call_name + "?" + arg_mod);
    var target = document.getElementById(target_id);
    target.innerText = "Working";

    xhttp.onload = function() {
        console.log('Server response:', this.responseText);
        target.innerHTML = this.responseText;

        callback();
    };
    xhttp.send();
}







