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

function handleUpdate(id1) {
  let id_num = id1;
  id_num = id_num.substring(3);
  var num = parseInt(document.getElementById(id1).value);

  console.log(num);

  fetcher('api/add_inventory/' + id_num + '/' + num, 'dummy')
}