function handleSearch(event) {
  var query = event.target.value;

  // Fetch search results and update the page
  fetcher('search','container', [query], function() {
     // This callback function will be called after the page is updated
     console.log('Page updated with search results for query:', query);
  });
  // TODO: Use the query to search your data and update the page
  console.log('Search query:', query);
}

var cart_total = 0;

function checkQuantity(quantity_id, button_id) 
{
  const number = document.getElementById(quantity_id);
  const add_to_cart_button = document.getElementById(button_id);
  const enteredQuantity = parseInt(number.value);
  const availableQuantity = parseInt(number.max);

  // Check if entered quantity exceeds available quantity
  if (enteredQuantity > availableQuantity) 
  {
    add_to_cart_button.disabled = true; // Disable the button
  } 
  else 
  {
    add_to_cart_button.disabled = false; // Enable the button
  }

  console.log("button_id: ", add_to_cart_button);
}

// this needs to be overhauled
/*function updateCartTotal(cart_total)
{
  const cartButton = document.getElementById('cartButton');
  cartButton.innerText = 'Cart (' + cart_total + ')';

  console.log('Cart successfully updated with: ', cart_total);
}*/

//USE THIS AS A TEMPLATE FOR UPDATING ELEMENTS ON STORE_FRONT!!!
/*function addToCart(quantity_id, button_id, available_id)
{
  console.log('hi');
  const number = document.getElementById(quantity_id);
  const add_to_cart_button = document.getElementById(button_id);
  const availableQuantity = parseInt(number.max);

  let enteredQuantity;

  if (number.value === '')
  {
    enteredQuantity = 0;
  }
  else 
  {
    enteredQuantity = parseInt(number.value);
  }

  number.max = availableQuantity - enteredQuantity;
  const availableText = document.getElementById(available_id);
  availableText.textContent = 'Available: ' + number.max;

  console.log("parts available: ", number.max);
  if (parseInt(number.max) === 0)
  {
    number.value = '';
    number.disabled = true;
    add_to_cart_button.disabled = true;
    console.log("This item is now out of stock");
  }

  cart_total += enteredQuantity;

  updateCartTotal(cart_total);

  console.log('Quantity entered: ', number.value);
  console.log('Button_id: ', add_to_cart_button);
}*/

// This needs to be changed, only handle the request for the session here.
// Make separate functions that are called that edit other parts the other elements
// the other elements also need to be saved in the session, particularly availability, and quantity so we can send it over to the cart page 
function addToCart(call_name, quantity_id, button_id, available_id, item_id, quantity_chosen, callback=() => {/* do nothing */}) {
  const number = document.getElementById(quantity_id);  

  let enteredQuantity;

  if (number.value === '')
  {
    enteredQuantity = 0;
  }
  else 
  {
    enteredQuantity = parseInt(number.value);
  }

  cart_total += enteredQuantity;
    
  var xhttp = new XMLHttpRequest;
 
  xhttp.open("POST", "/" + call_name + '/' + item_id + '/' + quantity_chosen); 

  console.log("POST", "/" + call_name + '/' + item_id + '/' + quantity_chosen); 

  console.log('call_name: ', call_name); // print call_name
  console.log('item_id: ', item_id); // print item_id
  console.log('quantity_chosen: ', quantity_chosen) // print quantity entered

  xhttp.onload = function() {
      console.log('Server response:', this.responseText);
      updateCartTotal('get_cart_total');

      callback();
  };
  xhttp.send();
}

//this updates both pages, cart and car parts store
window.onload = function() {
  updateCartTotal('get_cart_total');
};

function updateCartTotal(call_name)
{
  var xhttp = new XMLHttpRequest;

  xhttp.open("POST", '/' + call_name);
  const cartButton = document.getElementById('cartButton');

  console.log('Successfully retrieved cart total!!!');

  xhttp.onload = function() {
    var cart_total = this.responseText;
    cartButton.innerText = 'Cart (' + cart_total + ')';
  }

  xhttp.send();
}


function onClick(el) {
  const button = document.getElementById(el);
  var clicks = 0;
  clicks += 1
  if(clicks > 0) {
    button.removeAttribute("disabled");
  }
}
