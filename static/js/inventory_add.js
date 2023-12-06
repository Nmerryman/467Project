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

  fetcher('api/add_inventory/' + id_num + '/' + num, 'dummy', [], () => {
      window.location.reload();
  })
}

function updateInventory(id_num) {
    const val = document.getElementById('input' + id_num).value;
    fetcher('api/add_inventory/' + id_num + '/' + val, 'dummy', [], () => {
        window.location.reload();
    });

}

function inventorySearch() {
    const val = document.getElementById('search-bar').value;
    fetcher("search_inventory", "container", [val], () => {
        console.log("Search complete");
    });
}
