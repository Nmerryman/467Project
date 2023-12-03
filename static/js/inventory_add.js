function handleInput(event) {
    console.log("Handle input doesn't do anything yet")
}

function onClick(el) {
    const button = document.getElementById(el);
    var clicks = 0;
    clicks += 1
    if(clicks > 0) {
      button.removeAttribute("disabled");
    }
  }
