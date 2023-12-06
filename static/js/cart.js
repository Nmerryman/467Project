
function loadCart() {
    fetcher('get_cart_items', 'container', [], () => {
        loadCartStats();
    });
}

function loadCartStats() {
    fetcher('get_cart_stats', 'cartStats', [], () => {});
}

function tryCheckout() {
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const streetAddress = document.getElementById('streetAddress').value;
    const city = document.getElementById('city').value;
    const state = document.getElementById('state').value;
    const zipCode = document.getElementById('zipCode').value;

    const cardNumber = document.getElementById('cardNumber').value;
    const cardName = document.getElementById('cardName').value;
    const cardExp = document.getElementById('cardExp').value;
    const cardCVV = document.getElementById('cardCVV').value;
    const cardZip = document.getElementById('cardZip').value;

    fetcher('checkout', 'payResult', [name, email, streetAddress, city, state, zipCode,
        cardNumber, cardName, cardExp, cardCVV, cardZip], function() {
        console.log('Page updated with checkout results');
    })
}

function removeItem(item) {
    fetcher('remove_from_cart/' + item, 'container', [], function() {
        console.log('Page updated with cart results');
        loadCart();
    });
}


function calculateValues() {

}

