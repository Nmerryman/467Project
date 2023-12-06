function printDescriptions() 
{
    // Get all the items
    var items = document.getElementsByClassName('box');
    
    // Loop through each item
    for (var i = 0; i < items.length; i++) 
    {
        // Get the item number from the id
        var itemNumber = items[i].id.replace('item', '');
        
        // Get the description of the item using the unique ID
        var description = document.getElementById('description' + itemNumber).textContent;
    
        console.log('Description:', description);
    }
}

let total_weight = 0;
let total_order_price = 0;
let total_amount = 0;

function updateAmount() 
{
    // Get all the items
    var items = document.getElementsByClassName('box');
    
    // Loop through each item
    for (var i = 0; i < items.length; i++) 
    {
        // Get the item number from the id
        var itemNumber = items[i].id.replace('item', '');
        
        // Get the description of the item using the unique ID
        var price = document.getElementById('price' + itemNumber).textContent.substring(1);
        var quantity = document.getElementById('quantity' + itemNumber).textContent.substring(10);

        //console.log('Price: ', Number(price));
        //console.log('Quantity: ', Number(quantity));

        total_amount += Number(price) * Number(quantity);
        
        // Print the description to the console
        //console.log('price:', price, ' ', quantity);
    }

    total_amount = total_amount.toFixed(2);
    //console.log('Total Amount:', total_amount)
    total_order_price += parseFloat(total_amount);
    console.log('Total order price:', total_order_price);

    document.getElementById('amountLabel').textContent = 'Amount: $' + total_amount;
}

function updateWeight()
{
    var items = document.getElementsByClassName('box');

    // Loop through each item
    for (var i = 0; i < items.length; i++) 
    {
        // Get the item number from the id
        var itemNumber = items[i].id.replace('item', '');
        
        // Get the description of the item using the unique ID
        var weight = document.getElementById('weight' + itemNumber).textContent.slice(0, -4);
        var quantity = document.getElementById('quantity' + itemNumber).textContent.substring(10);

        //console.log('Weight: ', weight);
        //console.log('Quantity: ', Number(quantity));

        total_weight += Number(weight) * Number(quantity);
        
        // Print the description to the console
    }

    total_weight = total_weight.toFixed(2);
    //console.log('Total Weight:', total_weight)
    document.getElementById('weightLabel').textContent = 'Weight: ' + total_weight + 'lbs';
}

function handleUpdate() 
{
    console.log(total_weight);
  
    fetch('api/get_shipping_cost/' + total_weight)
        .then(response => response.text())
        .then(shipping_cost => {
            console.log('Shipping cost:', shipping_cost);
            document.getElementById('shipping').textContent = 'Shipping: $' + parseFloat(shipping_cost).toFixed(2);

            //console.log("shipping cost:", Number(shipping_cost));
            total_order_price += parseFloat(shipping_cost);
            console.log('Total order price:', total_order_price);
            document.getElementById('total').textContent = 'Total: $' + total_order_price.toFixed(2);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getTransactionNumber() {
    return fetch('/get_trans_num', {method: 'POST'})
        .then(response => response.text());
}

function authorizeCreditCard(trans_num, vendor, credit_card, name, expiration, total_order_price) {
    var formData = new FormData();
    formData.append('vendor', vendor);
    formData.append('trans_num', trans_num);
    formData.append('cc_num', credit_card);
    formData.append('name', name);
    formData.append('exp', expiration);
    formData.append('amount', total_order_price.toFixed(2));

    var items = document.getElementById('box');

    return fetch('/authorize_cc', {method: 'POST', body: formData})
        .then(response => response.text());
}

function addNewCustomer(name, email, address) {
    var formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('addr1', address);
    formData.append('addr2', ''); // Add address line 2 if available

    return fetch('/new_customer', {method: 'POST', body: formData})
        .then(response => response.text());
}

//order_new(1, 'In queue', 2, datetime.now())
function addOrder(cust_id, status, fee_id) {

    var formData = new FormData();
    formData.append('cust_id', cust_id);
    formData.append('status', status);
    formData.append('fee_id', fee_id);

    return fetch('/new_order', {method: 'POST', body: formData})
        .then(response => response.text());
}

function addItem(order_id, item_id, quantity, cost, weight)
{
    var formData = new FormData();
    formData.append('order_id', order_id);
    formData.append('item_id', item_id);
    formData.append('quantity', quantity);
    formData.append('cost', cost);
    formData.append('weight', weight);

    return fetch('/add_item', {method: 'POST', body: formData})
        .then(reponse => reponse.text());
}

function handleCheckout() {
    var name = document.getElementById('name').value;
    var email = document.getElementById('email').value;
    var address = document.getElementById('address').value;
    var credit_card = document.getElementById('credit-card').value;
    var expiration = document.getElementById('expiration').value;
    var vendor = 'VE0001-99';

    getTransactionNumber()
        .then(trans_num => {
            console.log('Transaction Number: ', trans_num);
            return authorizeCreditCard(trans_num, vendor, credit_card, name, expiration, total_order_price);
        })
        .then(result => {
            let result_obj = JSON.parse(result);

            if (result_obj.errors)
            {
                console.log('no no! wrong info!!!');
                console.log('Error:', result_obj.errors);
                throw new Error('Authorization failed: ' + result.obj.errors);
            }

            console.log('Authorization Result: ', result);
            console.log('Vendor: ', result_obj.vendor);
            console.log('Errors: ', result_obj.errors);
            
            return addNewCustomer(name, email, address);
        }).catch(error => {
            console.log('Error during checkout!!!!', error.message);
            throw error;
        })
        .then(customer_id => {
            console.log('New Customer ID: ', customer_id);
            return addOrder(customer_id, 'In Queue', 1);
        })
        .then(order_id => {
            console.log('New Order ID:', order_id);

            var items = document.getElementsByClassName('box');

            for (var i = 0; i < items.length; i++)
            {
                var itemNumber = items[i].id.replace('item', '');
                var quantity = document.getElementById('quantity' + itemNumber).textContent.substring(10);

                addItem(order_id, itemNumber, quantity, 0, 0);
            }
            console.log('All items added to order!');

            return fetch('/update_all', {method: 'POST'});
        });
}

/*window.onload = function() {
    updateAmount();
    updateWeight();
};*/

window.addEventListener('load', updateAmount);
window.addEventListener('load', updateWeight);
window.addEventListener('load', handleUpdate);
//window.addEventListener('load', handleCheckout);

window.onload = function() {
    const openConfirmButton = document.querySelectorAll('[data-confirm-target]');
    const closeConfirmButton = document.querySelectorAll('[data-return-button]');
    const overlay = document.getElementById('overlay');

    openConfirmButton.forEach(button => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            console.log('openConfirmButton clicked');
            const confirm_page = document.querySelector(button.dataset.confirmTarget);
            openConfirmPage(confirm_page);
        });
    });

    closeConfirmButton.forEach(button => {
        button.addEventListener('click', (event) => {
            event.stopPropagation();
            console.log('closeConfirmButton clicked');
            const confirm_page = button.closest('.confirm-page');
            closeConfirmPage(confirm_page);
        });
    });

    function openConfirmPage(confirm_page) {
        console.log('openConfirmPage function called');
        if (confirm_page == null) return;
        confirm_page.classList.add('active');
        overlay.classList.add('active');
    }

    function closeConfirmPage(confirm_page) {
        console.log('closeConfirmPage function called');
        if (confirm_page == null) return;
        confirm_page.classList.remove('active');
        overlay.classList.remove('active');
    }
}






