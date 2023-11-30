// takes four parameters: call_name, target_id, argument=[] and callback=(). 
// callback=() does not do anything, nor is it needed at this point 
// call_name would be the function we are calling on the server side. As an example, we will use the search function
// target_id is the thing we want to update on the response page, in this case container is what we are trying to update, 
// with the new search results everytime a new item is searched for.
//
/*function fetcher(call_name, target_id, argument=[], callback=() => {/* do nothing }) {
    var xhttp = new XMLHttpRequest; //this is the creation of a XMLHttpRequest object, which is used to interact with servers
    // Passes arguments where it makes sense
    var arg_mod = "" //argument list variable
    if (argument.length != 0) { //if argument is not equal to zero
        for (a = 0; a < argument.length; a++){ //iterate through the argument array using its length, each time we go through, we add a '&' seperator,
            // for each different argument, and we make a unique name for each argument (arg0, arg1, arg2, etc.).
            arg_mod = arg_mod + "&arg" + a + "=" + encodeURIComponent(argument[a]);
        }
    }
    xhttp.open("GET", "/" + call_name + "?" + arg_mod); // this initializes the XMLHttpRequest.
    // open takes 2 parameters, one being the HTTP method and the URL, and an optional boolean parameter.
    // We are using GET in this case, which is used to request data from a specified resource (legacy DB).
    // Then we add a /, the call_name, in this case being search, defined in server.py, and the arg_mod, which should be whatever the user is trying to search for
    // We will use windshield as an example here. 
    // Finds target element
    var target = document.getElementById(target_id); //this finds the target in on the html page, in this case, container
    target.innerText = "Working"; // this sets the innertext of the target (container) to Working, that way we can see immediatly if the request is being processed.

    xhttp.onload = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log('Server response:', this.responseText);
            target.innerHTML = this.responseText;

            callback();
        }
    };
    xhttp.send();
}*/

function fetcher(call_name, target_id, argument=[], callback=() => {/* do nothing */}) {
    var xhttp = new XMLHttpRequest; //this is the creation of a XMLHttpRequest object, which is used to interact with servers
    // Passes arguments where it makes sense
    var arg_mod = "" //argument list variable
    if (argument.length != 0) { //if argument is not equal to zero
        for (a = 0; a < argument.length; a++){ //iterate through the argument array using its length, each time we go through, we add a '&' seperator,
            // for each different argument, and we make a unique name for each argument (arg0, arg1, arg2, etc.).
            arg_mod = arg_mod + "&arg" + a + "=" + argument[a];
        }
    }
    xhttp.open("GET", "/" + call_name + "?" + arg_mod); // this initializes the XMLHttpRequest.
    // open takes 2 parameters, one being the HTTP method and the URL, and an optional boolean parameter.
    // We are using GET in this case, which is used to request data from a specified resource (legacy DB).
    // Then we add a /, the call_name, in this case being search, defined in server.py, and the arg_mod, which should be whatever the user is trying to search for
    // We will use windshield as an example here. 
    // Finds target element
    var target = document.getElementById(target_id); //this finds the target in on the html page, in this case, container
    target.innerText = "Working"; // this sets the innertext of the target (container) to Working, that way we can see immediatly if the request is being processed.

    xhttp.onload = function() {
        console.log('Server response:', this.responseText);
        target.innerHTML = this.responseText;

        callback();
    };
    xhttp.send();
}




