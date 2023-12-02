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

function updateCartTotal(cart_total)
{
  const cartButton = document.getElementById('cartButton');
  cartButton.innerText = 'Cart (' + cart_total + ')';

  console.log('Cart successfully updated with: ', cart_total);
}

function addToCart(quantity_id, button_id, available_id)
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
}

